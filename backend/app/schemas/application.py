"""Request/response models for /applications (EP-3)."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ApplicationStatus = Literal[
    "applied", "reviewed", "shortlisted", "rejected", "hired", "withdrawn"
]
# A recruiter can never set "withdrawn" — that is the candidate's action.
RecruiterSettableStatus = Literal["reviewed", "shortlisted", "rejected", "hired"]


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    cover_note: Optional[str] = Field(default=None, max_length=4000)


class StatusUpdate(BaseModel):
    status: RecruiterSettableStatus


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    location: str
    job_type: str
    work_mode: str = "onsite"
    experience_level: str = "mid"
    application_deadline: Optional[date] = None
    is_expired: bool = False
    status: str
    company_name: Optional[str] = None
    company_avatar_url: Optional[str] = None


class CandidateSummary(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    years_experience: Optional[int] = None
    experience_level: Optional[str] = None
    resume_url: Optional[str] = None


class ApplicationOut(BaseModel):
    """Shape returned to the candidate (my applications)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    cover_note: Optional[str]
    status: ApplicationStatus
    applied_at: datetime
    job: Optional[JobSummary] = None
    unread_messages: int = 0


class ApplicantOut(BaseModel):
    """Shape returned to the recruiter (applicants for a job)."""

    id: uuid.UUID
    job_id: uuid.UUID
    cover_note: Optional[str]
    status: ApplicationStatus
    applied_at: datetime
    candidate: CandidateSummary
    unread_messages: int = 0
