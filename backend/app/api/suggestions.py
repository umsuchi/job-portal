"""EP-5 — the candidate's "Recommended for you" list."""
from __future__ import annotations

import uuid
from typing import Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_candidate
from app.db.session import get_db
from app.models.job import JOB_OPEN, Job
from app.models.suggestion import SuggestionCache
from app.models.user import RecruiterProfile, User
from app.schemas.job import JobOut
from app.schemas.suggestion import SuggestionOut, SuggestionsResponse
from app.services import ai_suggestions

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.get("", response_model=SuggestionsResponse)
async def get_suggestions(
    refresh: bool = Query(default=False, description="Bypass the cache and regenerate"),
    candidate: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    """US-5.1/5.2/5.3.

    Served from the per-candidate cache unless the skills changed, the cache is
    older than the TTL, or `refresh=true`. The Groq call happens at most once
    per regeneration, never once per page load (FR-10).
    """
    profile = candidate.candidate_profile
    skills: List[str] = list(getattr(profile, "skills", None) or [])

    cache = await db.get(SuggestionCache, candidate.id)
    cached = not refresh and ai_suggestions.is_fresh(cache, skills)

    if cached:
        source, payload, generated_at = cache.source, list(cache.payload or []), cache.generated_at
    else:
        source, payload, generated_at = await ai_suggestions.generate(
            db, candidate.id, skills
        )

    job_ids = []
    for item in payload:
        try:
            job_ids.append(uuid.UUID(item["job_id"]))
        except (KeyError, ValueError, TypeError):
            continue

    jobs: Dict[uuid.UUID, Job] = {}
    if job_ids:
        rows = await db.execute(
            select(Job).where(Job.id.in_(job_ids), Job.status == JOB_OPEN)
        )
        jobs = {job.id: job for job in rows.scalars().all()}

    companies: Dict[uuid.UUID, str] = {}
    if jobs:
        rows = await db.execute(
            select(RecruiterProfile.user_id, RecruiterProfile.company_name).where(
                RecruiterProfile.user_id.in_([j.recruiter_id for j in jobs.values()])
            )
        )
        companies = dict(rows.all())

    suggestions: List[SuggestionOut] = []
    for item in payload:
        try:
            job = jobs.get(uuid.UUID(item["job_id"]))
        except (KeyError, ValueError, TypeError):
            continue
        # A job closed since the cache was written simply drops out of the list.
        if job is None:
            continue
        job_out = JobOut.model_validate(job)
        job_out.company_name = companies.get(job.recruiter_id)
        job_out.has_applied = None
        suggestions.append(
            SuggestionOut(
                rank=len(suggestions) + 1,
                reason=item.get("reason", ""),
                matched_skills=list(item.get("matched_skills") or []),
                overlap=int(item.get("overlap") or 0),
                job=job_out,
            )
        )

    return SuggestionsResponse(
        source=source if source in ("ai", "fallback") else "fallback",
        generated_at=generated_at,
        cached=cached,
        candidate_skills=skills,
        suggestions=suggestions,
    )
