"""Users and their role-specific profiles (spec §9)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, created_at_col, uuid_pk

ROLE_CANDIDATE = "candidate"
ROLE_RECRUITER = "recruiter"
ROLES = (ROLE_CANDIDATE, ROLE_RECRUITER)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('candidate', 'recruiter')", name="ck_users_role"
        ),
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


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    headline: Mapped[Optional[str]] = mapped_column(String(255))
    skills: Mapped[List[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
    resume_url: Mapped[Optional[str]] = mapped_column(String(1024))

    user: Mapped["User"] = relationship(back_populates="candidate_profile")


class RecruiterProfile(Base):
    __tablename__ = "recruiter_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    company_website: Mapped[Optional[str]] = mapped_column(String(512))

    user: Mapped["User"] = relationship(back_populates="recruiter_profile")
