"""Job posts (spec §9, extended).

One deliberate change from the original spec: ``job_type`` used to mix
employment type with work arrangement — "remote" sat alongside "full_time",
so a full-time remote role could not describe itself. Work arrangement now
lives in its own ``work_mode`` column, which is also what makes location
matching in the suggestion engine mean anything.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
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

# Employment type only — how the role is contracted.
JOB_TYPES = ("full_time", "part_time", "contract", "internship", "temporary")

# Work arrangement — where the work happens.
WORK_MODES = ("onsite", "hybrid", "remote")

# Ordered from least to most senior; the order is what makes the seniority
# distance in `services/matcher.py` meaningful.
EXPERIENCE_LEVELS = ("entry", "junior", "mid", "senior", "lead", "principal")

EXPERIENCE_LEVEL_RANK = {level: index for index, level in enumerate(EXPERIENCE_LEVELS)}

# How close a deadline has to be before the UI calls it urgent.
CLOSING_SOON_DAYS = 7


def today() -> date:
    """Server-side "today", in UTC.

    Deadlines are dates, not moments, so a candidate a few hours either side of
    UTC can see a boundary shift by a day. That is the accepted cost of not
    pretending to a precision recruiters never gave us.
    """
    return datetime.now(timezone.utc).date()

# Typical years behind each level, used to infer a level when a candidate gives
# only a number of years.
LEVEL_MIN_YEARS = {
    "entry": 0, "junior": 1, "mid": 3, "senior": 6, "lead": 8, "principal": 12,
}


def level_for_years(years: Optional[int]) -> Optional[str]:
    """Best-guess seniority for a number of years, for candidates who gave one."""
    if years is None:
        return None
    match = "entry"
    for level in EXPERIENCE_LEVELS:
        if years >= LEVEL_MIN_YEARS[level]:
            match = level
    return match


def _in_list(column: str, values: tuple) -> str:
    joined = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({joined})"


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(_in_list("status", JOB_STATUSES), name="ck_jobs_status"),
        CheckConstraint(_in_list("job_type", JOB_TYPES), name="ck_jobs_job_type"),
        CheckConstraint(_in_list("work_mode", WORK_MODES), name="ck_jobs_work_mode"),
        CheckConstraint(
            _in_list("experience_level", EXPERIENCE_LEVELS),
            name="ck_jobs_experience_level",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_jobs_salary_range",
        ),
        CheckConstraint(
            "min_years_experience IS NULL OR min_years_experience >= 0",
            name="ck_jobs_min_years",
        ),
        # Powers the `required_skills && :candidate_skills` shortlist in §12.
        Index("ix_jobs_required_skills_gin", "required_skills", postgresql_using="gin"),
        # Nice-to-haves widen the shortlist, so they need their own index.
        Index(
            "ix_jobs_nice_to_have_skills_gin",
            "nice_to_have_skills",
            postgresql_using="gin",
        ),
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

    # --- what the role is ---------------------------------------------------
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    requirements: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    benefits: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )

    # --- who it is for ------------------------------------------------------
    required_skills: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    nice_to_have_skills: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    experience_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="mid", server_default="mid"
    )
    min_years_experience: Mapped[Optional[int]] = mapped_column(Integer)

    # --- where and how ------------------------------------------------------
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[str] = mapped_column(String(30), nullable=False)
    work_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default="onsite", server_default="onsite"
    )
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD", server_default="USD"
    )

    # Inclusive: applications are accepted all through this day. Stored as a
    # DATE rather than a timestamp because that is how deadlines are stated
    # ("apply by 15 March") — a timestamp would invent a precision recruiters
    # never specify and would read differently in every timezone.
    application_deadline: Mapped[Optional[date]] = mapped_column(Date)

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

    @property
    def is_remote(self) -> bool:
        return self.work_mode == "remote"

    @property
    def is_expired(self) -> bool:
        """Past its deadline. A job with no deadline never expires."""
        if self.application_deadline is None:
            return False
        return self.application_deadline < today()

    @property
    def days_until_deadline(self) -> Optional[int]:
        """Whole days left, inclusive of the deadline day.

        0 means "closes today", negative means it already closed. None when the
        post has no deadline at all — which the UI must render as "no deadline"
        rather than as an urgent 0.
        """
        if self.application_deadline is None:
            return None
        return (self.application_deadline - today()).days

    @property
    def accepts_applications(self) -> bool:
        """The single question the apply endpoint and the UI both need."""
        return self.is_open and not self.is_expired
