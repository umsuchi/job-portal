"""Applications and the server-side status lifecycle (spec §11.2)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, uuid_pk

STATUS_APPLIED = "applied"
STATUS_REVIEWED = "reviewed"
STATUS_SHORTLISTED = "shortlisted"
STATUS_REJECTED = "rejected"
STATUS_HIRED = "hired"
STATUS_WITHDRAWN = "withdrawn"

APPLICATION_STATUSES = (
    STATUS_APPLIED,
    STATUS_REVIEWED,
    STATUS_SHORTLISTED,
    STATUS_REJECTED,
    STATUS_HIRED,
    STATUS_WITHDRAWN,
)

TERMINAL_STATUSES: Set[str] = {STATUS_HIRED, STATUS_REJECTED, STATUS_WITHDRAWN}

# Transitions a recruiter may make. Withdrawal is candidate-only and handled
# separately in the applications API.
RECRUITER_TRANSITIONS: Dict[str, Set[str]] = {
    STATUS_APPLIED: {STATUS_REVIEWED, STATUS_REJECTED},
    STATUS_REVIEWED: {STATUS_SHORTLISTED, STATUS_REJECTED},
    STATUS_SHORTLISTED: {STATUS_HIRED, STATUS_REJECTED},
    STATUS_REJECTED: set(),
    STATUS_HIRED: set(),
    STATUS_WITHDRAWN: set(),
}


def can_recruiter_transition(current: str, target: str) -> bool:
    return target in RECRUITER_TRANSITIONS.get(current, set())


def can_candidate_withdraw(current: str) -> bool:
    return current not in TERMINAL_STATUSES


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        # FR-5: one application per candidate per job.
        UniqueConstraint("job_id", "candidate_id", name="uq_applications_job_candidate"),
        CheckConstraint(
            "status IN ('applied', 'reviewed', 'shortlisted', 'rejected', 'hired', 'withdrawn')",
            name="ck_applications_status",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    job_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cover_note: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=STATUS_APPLIED, server_default=STATUS_APPLIED
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    job: Mapped["Job"] = relationship(back_populates="applications", lazy="selectin")  # noqa: F821
    candidate: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    messages: Mapped[List["Message"]] = relationship(  # noqa: F821
        back_populates="application", cascade="all, delete-orphan"
    )
