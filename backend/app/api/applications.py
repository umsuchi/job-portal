"""EP-3 — apply, list, withdraw; plus the recruiter's status transition (US-2.4)."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_candidate, require_recruiter
from app.db.session import get_db
from app.models.application import (
    STATUS_WITHDRAWN,
    Application,
    can_candidate_withdraw,
    can_recruiter_transition,
)
from app.models.job import JOB_OPEN, Job
from app.models.message import Message
from app.models.user import RecruiterProfile, User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    JobSummary,
    StatusUpdate,
)

router = APIRouter(prefix="/applications", tags=["applications"])


async def load_application_for_party(
    application_id: uuid.UUID, user: User, db: AsyncSession
) -> Application:
    """Fetch an application only if `user` is the candidate or the owning recruiter.

    Shared with the messages router so FR-7 has a single implementation.
    """
    app_row = await db.get(Application, application_id)
    if app_row is None:
        raise HTTPException(status_code=404, detail="Application not found.")
    job = await db.get(Job, app_row.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Application not found.")
    if user.id not in (app_row.candidate_id, job.recruiter_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this application.",
        )
    return app_row


async def _unread_map(db: AsyncSession, user: User, app_ids: List[uuid.UUID]) -> dict:
    if not app_ids:
        return {}
    rows = await db.execute(
        select(Message.application_id, func.count(Message.id))
        .where(
            Message.application_id.in_(app_ids),
            Message.receiver_id == user.id,
            Message.read_at.is_(None),
        )
        .group_by(Message.application_id)
    )
    return dict(rows.all())


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def apply(
    payload: ApplicationCreate,
    candidate: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    """US-3.2 — one application per candidate per job (FR-5)."""
    job = await db.get(Job, payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != JOB_OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job is closed and no longer accepting applications.",
        )

    application = Application(
        job_id=job.id,
        candidate_id=candidate.id,
        cover_note=(payload.cover_note or "").strip() or None,
    )
    db.add(application)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job.",
        )
    await db.refresh(application)
    return await _serialize(db, application, candidate)


async def _serialize(
    db: AsyncSession, application: Application, user: User
) -> ApplicationOut:
    job = await db.get(Job, application.job_id)
    company = await db.scalar(
        select(RecruiterProfile.company_name).where(
            RecruiterProfile.user_id == job.recruiter_id
        )
    )
    unread = await _unread_map(db, user, [application.id])
    out = ApplicationOut.model_validate(application)
    out.job = JobSummary(
        id=job.id,
        title=job.title,
        location=job.location,
        job_type=job.job_type,
        status=job.status,
        company_name=company,
    )
    out.unread_messages = unread.get(application.id, 0)
    return out


@router.get("/me", response_model=List[ApplicationOut])
async def my_applications(
    candidate: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    """US-3.3 — the candidate's applications, most recent first."""
    rows = await db.execute(
        select(Application, Job, RecruiterProfile.company_name)
        .join(Job, Job.id == Application.job_id)
        .outerjoin(RecruiterProfile, RecruiterProfile.user_id == Job.recruiter_id)
        .where(Application.candidate_id == candidate.id)
        .order_by(Application.applied_at.desc())
    )
    records = rows.all()
    unread = await _unread_map(db, candidate, [r[0].id for r in records])

    out = []
    for application, job, company in records:
        item = ApplicationOut.model_validate(application)
        item.job = JobSummary(
            id=job.id,
            title=job.title,
            location=job.location,
            job_type=job.job_type,
            status=job.status,
            company_name=company,
        )
        item.unread_messages = unread.get(application.id, 0)
        out.append(item)
    return out


@router.get("/{application_id}", response_model=ApplicationOut)
async def get_application(
    application_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    application = await load_application_for_party(application_id, user, db)
    return await _serialize(db, application, user)


@router.patch("/{application_id}/status", response_model=ApplicationOut)
async def update_status(
    application_id: uuid.UUID,
    payload: StatusUpdate,
    recruiter: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """US-2.4 — only the owning recruiter, and only along a legal edge of §11.2."""
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found.")
    job = await db.get(Job, application.job_id)
    if job is None or job.recruiter_id != recruiter.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own the job for this application.",
        )
    if not can_recruiter_transition(application.status, payload.status):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot move an application from '{application.status}' to '{payload.status}'.",
        )
    application.status = payload.status
    await db.commit()
    await db.refresh(application)
    return await _serialize(db, application, recruiter)


@router.delete("/{application_id}", response_model=ApplicationOut)
async def withdraw(
    application_id: uuid.UUID,
    candidate: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    """US-3.4 — withdraw; blocked once hired, rejected or already withdrawn."""
    application = await db.get(Application, application_id)
    if application is None or application.candidate_id != candidate.id:
        raise HTTPException(status_code=404, detail="Application not found.")
    if not can_candidate_withdraw(application.status):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An application that is '{application.status}' can no longer be withdrawn.",
        )
    application.status = STATUS_WITHDRAWN
    await db.commit()
    await db.refresh(application)
    return await _serialize(db, application, candidate)
