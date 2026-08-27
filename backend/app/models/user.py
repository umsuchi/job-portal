"""Users and their role-specific profiles (spec §9, extended).

The candidate profile carries more than identity now: the extra fields are the
inputs the suggestion engine scores against, so a candidate who fills them in
gets meaningfully better matches than one who only lists skills.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, created_at_col, uuid_pk
from app.models.job import EXPERIENCE_LEVELS

ROLE_CANDIDATE = "candidate"
ROLE_RECRUITER = "recruiter"
ROLES = (ROLE_CANDIDATE, ROLE_RECRUITER)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('candidate', 'recruiter')", name="ck_users_role"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = created_at_col()

    candidate_profile: Mapped[Optional["CandidateProfile"]] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    recruiter_profile: Mapped[Optional["RecruiterProfile"]] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )

    @property
    def is_candidate(self) -> bool:
        return self.role == ROLE_CANDIDATE

    @property
    def is_recruiter(self) -> bool:
        return self.role == ROLE_RECRUITER

    @property
    def display_name(self) -> str:
        if self.candidate_profile and self.candidate_profile.full_name:
            return self.candidate_profile.full_name
        if self.recruiter_profile and self.recruiter_profile.company_name:
            return self.recruiter_profile.company_name
        return self.email

    @property
    def avatar_url(self) -> Optional[str]:
        profile = self.candidate_profile or self.recruiter_profile
        return getattr(profile, "avatar_url", None)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    __table_args__ = (
        CheckConstraint(
            "experience_level IS NULL OR experience_level IN ("
            + ", ".join(f"'{level}'" for level in EXPERIENCE_LEVELS)
            + ")",
            name="ck_candidate_experience_level",
        ),
        CheckConstraint(
            "years_experience IS NULL OR years_experience >= 0",
            name="ck_candidate_years_experience",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    # --- identity -----------------------------------------------------------
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    headline: Mapped[Optional[str]] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024))
    resume_url: Mapped[Optional[str]] = mapped_column(String(1024))
    location: Mapped[Optional[str]] = mapped_column(String(255))

    # --- what they can do ---------------------------------------------------
    skills: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    years_experience: Mapped[Optional[int]] = mapped_column(Integer)
    experience_level: Mapped[Optional[str]] = mapped_column(String(20))

    # --- what they are looking for (all scored by the matcher) --------------
    preferred_job_types: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    preferred_work_modes: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    preferred_locations: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    desired_salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    open_to_work: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    user: Mapped["User"] = relationship(back_populates="candidate_profile")


class RecruiterProfile(Base):
    __tablename__ = "recruiter_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    company_website: Mapped[Optional[str]] = mapped_column(String(512))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024))
    about: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(120))
    headquarters: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="recruiter_profile")
