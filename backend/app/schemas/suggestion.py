"""Response models for /suggestions (EP-5)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

from app.schemas.job import JobOut


class SuggestionOut(BaseModel):
    rank: int
    reason: str
    matched_skills: List[str] = Field(default_factory=list)
    matched_nice_to_have: List[str] = Field(default_factory=list)
    # Short human-readable reasons the scorer ranked this job where it did —
    # rendered as chips on the dashboard, e.g. "Remote — as you prefer".
    signals: List[str] = Field(default_factory=list)
    overlap: int = 0
    score: float = 0.0
    job: JobOut


class SuggestionsResponse(BaseModel):
    # "ai" when Groq ranked them, "fallback" when the deterministic ranking was
    # used because Groq errored, timed out or returned unusable JSON (FR-9).
    source: Literal["ai", "fallback"]
    generated_at: datetime
    cached: bool
    candidate_skills: List[str] = Field(default_factory=list)
    suggestions: List[SuggestionOut] = Field(default_factory=list)
