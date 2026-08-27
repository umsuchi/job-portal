"""Per-candidate suggestion cache (FR-10, US-5.3).

One row per candidate. ``skills_hash`` is a digest of the candidate's skill
list, so a profile update naturally invalidates the cache without an explicit
delete; ``generated_at`` handles the hourly TTL.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, List

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SuggestionCache(Base):
    __tablename__ = "suggestion_caches"

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skills_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="fallback")
    payload: Mapped[List[Any]] = mapped_column(JSONB, nullable=False, default=list)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
