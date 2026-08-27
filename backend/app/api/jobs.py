"""EP-2 — job posting, plus the public browse/filter used by EP-3."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_optional, require_recruiter
from app.db.session import get_db
from app.models.application import Application
from app.models.job import JOB_CLOSED, JOB_OPEN, Job
from app.models.message import Message
from app.models.user import CandidateProfile, RecruiterProfile, User
from app.schemas.application import ApplicantOut, CandidateSummary
from app.schemas.common import Page
from app.schemas.job import JobCreate, JobOut, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


async def _company_names(db: AsyncSession, recruiter_ids: List[uuid.UUID]) -> dict:
    if not recruiter_ids:
        return {}
    rows = await db.execute(
        select(RecruiterProfile.user_id, RecruiterProfile.company_name).where(
            RecruiterProfile.user_id.in_(recruiter_ids)
        )
    )
    return {rid: name for rid, name in rows.all()}


async def _to_out(
    db: AsyncSession, jobs: List[Job], viewer: Optional[User] = None
) -> List[JobOut]:
    companies = await _company_names(db, [j.recruiter_id for j in jobs])
    job_ids = [j.id for j in jobs]

    counts: dict = {}
    if job_ids:
        rows = await db.execute(
            select(Application.job_id, func.count(Application.id))
            .where(Application.job_id.in_(job_ids))
            .group_by(Application.job_id)
        )
        counts = dict(rows.all())

    applied: set = set()
    if viewer is not None and viewer.is_candidate and job_ids:
        rows = await db.execute(
            select(Application.job_id).where(
                Application.job_id.in_(job_ids), Application.candidate_id == viewer.id
            )
        )
        applied = {r[0] for r in rows.all()}

    out = []
    for j in jobs:
        item = JobOut.model_validate(j)
        item.company_name = companies.get(j.recruiter_id)
        item.application_count = counts.get(j.id, 0)
        if viewer is not None and viewer.is_candidate:
            item.has_applied = j.id in applied
        out.append(item)
    return out


def _apply_filters(
    stmt: Select,
    q: Optional[str],
    skill: Optional[List[str]],
    location: Optional[str],
    job_type: Optional[str],
) -> Select:
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Job.title.ilike(like), Job.description.ilike(like)))
    if skill:
        cleaned = [s.strip() for s in skill if s.strip()]
        if cleaned:
            # Array overlap: the job needs at least one of the requested skills.
            stmt = stmt.where(Job.required_skills.overlap(cleaned))
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location.strip()}%"))
    if job_type:
        stmt = stmt.where(Job.job_type == job_type)
    return stmt


@router.get("", response_model=Page[JobOut])
async def list_jobs(
    q: Optional[str] = Query(default=None, description="Keyword in title or description"),
    skill: Optional[List[str]] = Query(default=None, description="Repeatable skill tag"),
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    include_closed: bool = False,
    mine: bool = Query(default=False, description="Recruiter: only my own posts"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    viewer: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """US-3.1 — public browse with keyword / skill / location / type filters."""
    stmt = select(Job)
    count_stmt = select(func.count(Job.id))

    conditions = []
    if mine:
        if viewer is None or not viewer.is_recruiter:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only recruiters can list their own jobs.",
            )
        conditions.append(Job.recruiter_id == viewer.id)
    # Closed posts are only ever listed for the recruiter who owns them.
    if not (mine and include_closed):
        conditions.append(Job.status == JOB_OPEN)

    if conditions:
        stmt = stmt.where(and_(*conditions))
        count_stmt = count_stmt.where(and_(*conditions))

    stmt = _apply_filters(stmt, q, skill, location, job_type)
    count_stmt = _apply_filters(count_stmt, q, skill, location, job_type)

    total = await db.scalar(count_stmt) or 0
    rows = await db.execute(
        stmt.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    )
    jobs = list(rows.scalars().all())
    return Page[JobOut](
        items=await _to_out(db, jobs, viewer), total=total, limit=limit, offset=offset
    )


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    recruiter: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """US-2.1 — recruiters only (FR-3)."""
    job = Job(recruiter_id=recruiter.id, **payload.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return (await _to_out(db, [job], recruiter))[0]


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: uuid.UUID,
    viewer: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status == JOB_CLOSED and not (
        viewer is not None and viewer.id == job.recruiter_id
    ):
        # Closed posts stay reachable for the owner, hidden from everyone else.
        raise HTTPException(status_code=404, detail="Job not found.")
    return (await _to_out(db, [job], viewer))[0]


async def _owned_job(job_id: uuid.UUID, recruiter: User, db: AsyncSession) -> Job:
    job = await db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.recruiter_id != recruiter.id:
        # FR-4: a recruiter cannot touch a post they do not own.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this job post."
        )
    return job


@router.put("/{job_id}", response_model=JobOut)
async def update_job(
    job_id: uuid.UUID,
    payload: JobUpdate,
    recruiter: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """US-2.2 — owner-only edit; can also reopen or close via `status`."""
    job = await _owned_job(job_id, recruiter, db)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(job, field, value)

    lo, hi = job.salary_min, job.salary_max
    if lo is not None and hi is not None and lo > hi:
        raise HTTPException(
            status_code=422, detail="salary_min cannot be greater than salary_max."
        )

    await db.commit()
    await db.refresh(job)
    return (await _to_out(db, [job], recruiter))[0]


@router.delete("/{job_id}", response_model=JobOut)
async def close_job(
    job_id: uuid.UUID,
    recruiter: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """US-2.2 — soft close. Existing applications and threads are preserved."""
    job = await _owned_job(job_id, recruiter, db)
    job.status = JOB_CLOSED
    await db.commit()
    await db.refresh(job)
    return (await _to_out(db, [job], recruiter))[0]


@router.get("/{job_id}/applications", response_model=List[ApplicantOut])
async def list_applicants(
    job_id: uuid.UUID,
    recruiter: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """US-2.3 — applicants for one of the recruiter's own jobs."""
    await _owned_job(job_id, recruiter, db)

    rows = await db.execute(
        select(Application, User, CandidateProfile)
        .join(User, User.id == Application.candidate_id)
        .outerjoin(CandidateProfile, CandidateProfile.user_id == User.id)
        .where(Application.job_id == job_id)
        .order_by(Application.applied_at.desc())
    )

    unread_rows = await db.execute(
        select(Message.application_id, func.count(Message.id))
        .join(Application, Application.id == Message.application_id)
        .where(
            Application.job_id == job_id,
            Message.receiver_id == recruiter.id,
            Message.read_at.is_(None),
        )
        .group_by(Message.application_id)
    )
    unread = dict(unread_rows.all())

    out = []
    for app_row, user, profile in rows.all():
        out.append(
            ApplicantOut(
                id=app_row.id,
                job_id=app_row.job_id,
                cover_note=app_row.cover_note,
                status=app_row.status,
                applied_at=app_row.applied_at,
                candidate=CandidateSummary(
                    id=user.id,
                    email=user.email,
                    full_name=getattr(profile, "full_name", None),
                    headline=getattr(profile, "headline", None),
                    skills=list(getattr(profile, "skills", None) or []),
                    resume_url=getattr(profile, "resume_url", None),
                ),
                unread_messages=unread.get(app_row.id, 0),
            )
        )
    return out
