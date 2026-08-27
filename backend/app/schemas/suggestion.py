"""Response models for /suggestions (EP-5)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

from app.schemas.job import JobOut


class SuggestionOut(BaseModel):
    rank: int
    reason: str
    matched_skills: List[str] = Field(default_factory=list)
    overlap: int = 0
    job: JobOut


class SuggestionsResponse(BaseModel):
    # "ai" when Groq ranked them, "fallback" when the SQL overlap ranking was
    # used because Groq errored, timed out or returned unusable JSON (FR-9).
    source: Literal["ai", "fallback"]
    generated_at: datetime
    cached: bool
    candidate_skills: List[str] = Field(default_factory=list)
    suggestions: List[SuggestionOut] = Field(default_factory=list)
