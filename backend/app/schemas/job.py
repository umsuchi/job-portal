"""Request/response models for /jobs (EP-2)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.auth import _clean_skills

JobType = Literal["full_time", "part_time", "contract", "internship", "remote"]
JobStatus = Literal["open", "closed"]


class JobBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)
    required_skills: List[str] = Field(default_factory=list)
    location: str = Field(min_length=1, max_length=255)
    job_type: JobType
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _check(self):
        self.required_skills = _clean_skills(self.required_skills)
        if not self.required_skills:
            raise ValueError("At least one required skill is needed.")
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max.")
        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10)
    required_skills: Optional[List[str]] = None
    location: Optional[str] = Field(default=None, min_length=1, max_length=255)
    job_type: Optional[JobType] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    status: Optional[JobStatus] = None

    @model_validator(mode="after")
    def _check(self):
        if self.required_skills is not None:
            self.required_skills = _clean_skills(self.required_skills)
            if not self.required_skills:
                raise ValueError("At least one required skill is needed.")
        return self


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recruiter_id: uuid.UUID
    title: str
    description: str
    required_skills: List[str]
    location: str
    job_type: JobType
    salary_min: Optional[int]
    salary_max: Optional[int]
    status: JobStatus
    created_at: datetime
    company_name: Optional[str] = None
    application_count: Optional[int] = None
    # Populated for authenticated candidates so the UI can disable "Apply".
    has_applied: Optional[bool] = None
