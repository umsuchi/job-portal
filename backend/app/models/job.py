"""Job posts (spec §9)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, created_at_col, uuid_pk

JOB_OPEN = "open"
JOB_CLOSED = "closed"
JOB_STATUSES = (JOB_OPEN, JOB_CLOSED)

JOB_TYPES = ("full_time", "part_time", "contract", "internship", "remote")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("status IN ('open', 'closed')", name="ck_jobs_status"),
        CheckConstraint(
            "job_type IN ('full_time', 'part_time', 'contract', 'internship', 'remote')",
            name="ck_jobs_job_type",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_jobs_salary_range",
        ),
        # Powers the `required_skills && :candidate_skills` shortlist in §12.
        Index("ix_jobs_required_skills_gin", "required_skills", postgresql_using="gin"),
        # Partial: the browse list only ever reads open jobs, so keeping
        # closed rows out makes the index smaller and the scan cheaper.
        Index(
            "ix_jobs_open_created_at",
            "created_at",
            postgresql_where=text("status = 'open'"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[str] = mapped_column(String(30), nullable=False)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=JOB_OPEN, server_default=JOB_OPEN
    )
    created_at: Mapped[datetime] = created_at_col()

    recruiter: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    applications: Mapped[List["Application"]] = relationship(  # noqa: F821
        back_populates="job", cascade="all, delete-orphan"
    )

    @property
    def is_open(self) -> bool:
        return self.status == JOB_OPEN
