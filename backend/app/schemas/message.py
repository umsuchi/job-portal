"""Request/response models for the per-application message thread (EP-4)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    body: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    sender_name: Optional[str] = None
    sender_avatar_url: Optional[str] = None
    is_mine: bool = False


class ThreadOut(BaseModel):
    application_id: uuid.UUID
    job_title: str
    counterpart_name: str
    counterpart_avatar_url: Optional[str] = None
    messages: List[MessageOut]


class UnreadCount(BaseModel):
    unread: int
