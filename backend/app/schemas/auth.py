"""Request/response models for /auth (EP-1)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Role = Literal["candidate", "recruiter"]
ExperienceLevel = Literal["entry", "junior", "mid", "senior", "lead", "principal"]
JobType = Literal["full_time", "part_time", "contract", "internship", "temporary"]
WorkMode = Literal["onsite", "hybrid", "remote"]


def _clean_list(v, limit: int = 40):
    """Trim, drop blanks, de-duplicate case-insensitively, cap the length."""
    if v is None:
        return []
    seen, out = set(), []
    for raw in v:
        s = " ".join(str(raw).strip().split())
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out[:limit]


def _clean_skills(v):
    return _clean_list(v, limit=40)


def _clean_locations(v):
    return _clean_list(v, limit=10)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: Role
    # Optional profile fields so signup can create a usable profile in one call.
    full_name: Optional[str] = Field(default=None, max_length=255)
    company_name: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CandidateProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    resume_url: Optional[str] = None
    location: Optional[str] = None

    skills: List[str] = Field(default_factory=list)
    years_experience: Optional[int] = None
    experience_level: Optional[ExperienceLevel] = None

    preferred_job_types: List[str] = Field(default_factory=list)
    preferred_work_modes: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    desired_salary_min: Optional[int] = None
    open_to_work: bool = True


class RecruiterProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_name: Optional[str] = None
    company_website: Optional[str] = None
    avatar_url: Optional[str] = None
    about: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    role: Role
    created_at: datetime
    candidate_profile: Optional[CandidateProfileOut] = None
    recruiter_profile: Optional[RecruiterProfileOut] = None


class ProfileUpdate(BaseModel):
    """Accepts both role shapes; the API applies only the fields for the
    caller's own role and ignores the rest."""

    # --- candidate ----------------------------------------------------------
    full_name: Optional[str] = Field(default=None, max_length=255)
    headline: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = Field(default=None, max_length=4000)
    avatar_url: Optional[str] = Field(default=None, max_length=1024)
    resume_url: Optional[str] = Field(default=None, max_length=1024)
    location: Optional[str] = Field(default=None, max_length=255)
    skills: Optional[List[str]] = None
    years_experience: Optional[int] = Field(default=None, ge=0, le=60)
    experience_level: Optional[ExperienceLevel] = None
    preferred_job_types: Optional[List[JobType]] = None
    preferred_work_modes: Optional[List[WorkMode]] = None
    preferred_locations: Optional[List[str]] = None
    desired_salary_min: Optional[int] = Field(default=None, ge=0)
    open_to_work: Optional[bool] = None

    # --- recruiter ----------------------------------------------------------
    company_name: Optional[str] = Field(default=None, max_length=255)
    company_website: Optional[str] = Field(default=None, max_length=512)
    about: Optional[str] = Field(default=None, max_length=4000)
    industry: Optional[str] = Field(default=None, max_length=120)
    headquarters: Optional[str] = Field(default=None, max_length=255)

    _norm_skills = field_validator("skills")(_clean_skills)
    _norm_locations = field_validator("preferred_locations")(_clean_locations)


# Fields each role is allowed to write, so the API never has to guess.
CANDIDATE_FIELDS = (
    "full_name", "headline", "bio", "avatar_url", "resume_url", "location",
    "skills", "years_experience", "experience_level", "preferred_job_types",
    "preferred_work_modes", "preferred_locations", "desired_salary_min", "open_to_work",
)
RECRUITER_FIELDS = (
    "company_name", "company_website", "avatar_url", "about", "industry", "headquarters",
)

# Editing any of these changes what the suggestion engine would return, so the
# cached suggestions have to go (US-5.3).
MATCHING_FIELDS = frozenset({
    "skills", "years_experience", "experience_level", "preferred_job_types",
    "preferred_work_modes", "preferred_locations", "desired_salary_min", "location",
})
