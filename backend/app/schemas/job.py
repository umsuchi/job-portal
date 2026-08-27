"""Request/response models for /jobs (EP-2)."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.job import today

from app.schemas.auth import _clean_list, _clean_skills

JobType = Literal["full_time", "part_time", "contract", "internship", "temporary"]
WorkMode = Literal["onsite", "hybrid", "remote"]
ExperienceLevel = Literal["entry", "junior", "mid", "senior", "lead", "principal"]
JobStatus = Literal["open", "closed"]


class JobBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevel = "mid"
    min_years_experience: Optional[int] = Field(default=None, ge=0, le=40)

    location: str = Field(min_length=1, max_length=255)
    job_type: JobType
    work_mode: WorkMode = "onsite"
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    salary_currency: str = Field(default="USD", min_length=3, max_length=3)
    # Inclusive — applications are accepted all through this day.
    application_deadline: Optional[date] = None

    @model_validator(mode="after")
    def _check(self):
        self.required_skills = _clean_skills(self.required_skills)
        self.nice_to_have_skills = _clean_skills(self.nice_to_have_skills)
        self.responsibilities = _clean_list(self.responsibilities, limit=15)
        self.requirements = _clean_list(self.requirements, limit=15)
        self.benefits = _clean_list(self.benefits, limit=15)

        if not self.required_skills:
            raise ValueError("At least one required skill is needed.")

        # A skill listed as both required and nice-to-have would be counted
        # twice by the matcher; required always wins.
        required = {s.lower() for s in self.required_skills}
        self.nice_to_have_skills = [
            s for s in self.nice_to_have_skills if s.lower() not in required
        ]

        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max.")

        self.salary_currency = self.salary_currency.upper()

        # Guard against the obvious typo. Only on create: an already-expired
        # post must stay editable, or a recruiter could never fix a title on it.
        if self.application_deadline and self.application_deadline < today():
            raise ValueError("The application deadline cannot be in the past.")
        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10)
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None

    required_skills: Optional[List[str]] = None
    nice_to_have_skills: Optional[List[str]] = None
    experience_level: Optional[ExperienceLevel] = None
    min_years_experience: Optional[int] = Field(default=None, ge=0, le=40)

    location: Optional[str] = Field(default=None, min_length=1, max_length=255)
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    salary_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    # Deliberately unvalidated here: editing an expired post must not fail
    # merely because its deadline has passed.
    application_deadline: Optional[date] = None
    status: Optional[JobStatus] = None

    @model_validator(mode="after")
    def _check(self):
        if self.required_skills is not None:
            self.required_skills = _clean_skills(self.required_skills)
            if not self.required_skills:
                raise ValueError("At least one required skill is needed.")
        if self.nice_to_have_skills is not None:
            self.nice_to_have_skills = _clean_skills(self.nice_to_have_skills)
        for name in ("responsibilities", "requirements", "benefits"):
            value = getattr(self, name)
            if value is not None:
                setattr(self, name, _clean_list(value, limit=15))
        if self.salary_currency:
            self.salary_currency = self.salary_currency.upper()
        return self


class CompanyOut(BaseModel):
    """The recruiter-side detail shown alongside a job."""
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None
    about: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recruiter_id: uuid.UUID

    title: str
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevel
    min_years_experience: Optional[int] = None

    location: str
    job_type: JobType
    work_mode: WorkMode
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"

    application_deadline: Optional[date] = None
    # Derived server-side so every client agrees on what "expired" means.
    is_expired: bool = False
    days_until_deadline: Optional[int] = None
    accepts_applications: bool = True

    status: JobStatus
    created_at: datetime

    # Joined in by the API rather than stored on the row.
    company: Optional[CompanyOut] = None
    company_name: Optional[str] = None
    application_count: Optional[int] = None
    # Populated for authenticated candidates so the UI can disable "Apply".
    has_applied: Optional[bool] = None
