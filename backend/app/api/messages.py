"""EP-4 — a message thread scoped to one application (FR-7)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.applications import load_application_for_party
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.job import Job
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageOut, ThreadOut, UnreadCount

router = APIRouter(tags=["messages"])


def _to_out(message: Message, viewer: User, names: dict) -> MessageOut:
    return MessageOut(
        id=message.id,
        application_id=message.application_id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        body=message.body,
        sent_at=message.sent_at,
        read_at=message.read_at,
        sender_name=names.get(message.sender_id),
        is_mine=message.sender_id == viewer.id,
    )


async def _names(db: AsyncSession, user_ids: List[uuid.UUID]) -> dict:
    rows = await db.execute(select(User).where(User.id.in_(user_ids)))
    return {u.id: u.display_name for u in rows.scalars().all()}


@router.get("/messages/unread-count", response_model=UnreadCount)
async def unread_count(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """US-4.3 — cheap endpoint the frontend polls every ~20s for the nav badge."""
    total = await db.scalar(
        select(func.count(Message.id)).where(
            Message.receiver_id == user.id, Message.read_at.is_(None)
        )
    )
    return UnreadCount(unread=total or 0)


@router.get("/applications/{application_id}/messages", response_model=ThreadOut)
async def get_thread(
    application_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """US-4.1/4.2 — read the thread and mark the caller's inbound messages read."""
    application = await load_application_for_party(application_id, user, db)
    job = await db.get(Job, application.job_id)

    rows = await db.execute(
        select(Message)
        .where(Message.application_id == application_id)
        .order_by(Message.sent_at.asc())
    )
    messages = list(rows.scalars().all())

    now = datetime.now(timezone.utc)
    touched = False
    for m in messages:
        if m.receiver_id == user.id and m.read_at is None:
            m.read_at = now
            touched = True
    if touched:
        await db.commit()

    counterpart_id = (
        job.recruiter_id if user.id == application.candidate_id else application.candidate_id
    )
    names = await _names(db, [application.candidate_id, job.recruiter_id])

    return ThreadOut(
        application_id=application_id,
        job_title=job.title,
        counterpart_name=names.get(counterpart_id, "Unknown"),
        messages=[_to_out(m, user, names) for m in messages],
    )


@router.post(
    "/applications/{application_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    application_id: uuid.UUID,
    payload: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """US-4.1/4.2 — the receiver is derived server-side, never taken from the client."""
    application = await load_application_for_party(application_id, user, db)
    job = await db.get(Job, application.job_id)

    if user.id == application.candidate_id:
        receiver_id = job.recruiter_id
    else:
        receiver_id = application.candidate_id

    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Message body cannot be empty.")

    message = Message(
        application_id=application_id,
        sender_id=user.id,
        receiver_id=receiver_id,
        body=body,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    names = await _names(db, [user.id])
    return _to_out(message, user, names)
