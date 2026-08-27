"""Request/response models for /auth (EP-1)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Role = Literal["candidate", "recruiter"]


def _clean_skills(v):
    if v is None:
        return []
    seen, out = set(), []
    for raw in v:
        s = str(raw).strip()
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out[:40]


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
    skills: List[str] = Field(default_factory=list)
    resume_url: Optional[str] = None


class RecruiterProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_name: Optional[str] = None
    company_website: Optional[str] = None


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

    full_name: Optional[str] = Field(default=None, max_length=255)
    headline: Optional[str] = Field(default=None, max_length=255)
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = Field(default=None, max_length=1024)
    company_name: Optional[str] = Field(default=None, max_length=255)
    company_website: Optional[str] = Field(default=None, max_length=512)

    _norm_skills = field_validator("skills")(_clean_skills)
