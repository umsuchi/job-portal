"""Stage 1 of the suggestion engine (spec §12): deterministic SQL shortlist.

No API call, no embeddings — just Postgres array overlap against the GIN index
on ``jobs.required_skills``, ranked by how many skills actually match.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JOB_OPEN, Job

SHORTLIST_SIZE = 10
# Widened candidate pool the ranking is computed over before trimming to 10.
CANDIDATE_POOL = 100


def normalize(skill: str) -> str:
    return " ".join(skill.strip().lower().split())


def skills_hash(skills: Sequence[str]) -> str:
    """Stable digest of a skill set — changing skills invalidates the cache."""
    joined = "|".join(sorted(normalize(s) for s in skills if s.strip()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def overlap(job_skills: Sequence[str], candidate_skills: Sequence[str]) -> List[str]:
    """Case-insensitive intersection, returned in the job's original casing."""
    wanted = {normalize(s) for s in candidate_skills}
    return [s for s in job_skills if normalize(s) in wanted]


async def shortlist(
    db: AsyncSession, candidate_skills: Sequence[str], limit: int = SHORTLIST_SIZE
) -> List[Tuple[Job, List[str]]]:
    """Open jobs sharing at least one skill, best overlap first.

    Returns ``(job, matched_skills)`` pairs. Empty list when the candidate has
    no skills on file — the caller turns that into an "add skills" empty state
    rather than a random job dump.
    """
    cleaned = [s.strip() for s in candidate_skills if s and s.strip()]
    if not cleaned:
        return []

    # Postgres array overlap is exact-match, so send both the original casing
    # and a normalized copy; the precise ranking happens in Python below.
    probe = list({*cleaned, *(normalize(s) for s in cleaned)})

    rows = await db.execute(
        select(Job)
        .where(Job.status == JOB_OPEN, Job.required_skills.overlap(probe))
        .order_by(Job.created_at.desc())
        .limit(CANDIDATE_POOL)
    )
    jobs = list(rows.scalars().all())

    scored: List[Tuple[Job, List[str]]] = []
    for job in jobs:
        matched = overlap(list(job.required_skills or []), cleaned)
        if matched:
            scored.append((job, matched))

    # Rank by absolute overlap, then by the share of the job's requirements met
    # (a 2-of-3 match beats a 2-of-9), then newest first as a stable tiebreak.
    scored.sort(
        key=lambda pair: (
            len(pair[1]),
            len(pair[1]) / max(len(pair[0].required_skills or []), 1),
            pair[0].created_at,
        ),
        reverse=True,
    )
    return scored[:limit]


def to_prompt_payload(pairs: List[Tuple[Job, List[str]]]) -> List[Dict]:
    """Trim jobs down to what the model actually needs to rank them."""
    payload = []
    for job, matched in pairs:
        payload.append(
            {
                "job_id": str(job.id),
                "title": job.title,
                "required_skills": list(job.required_skills or []),
                "matched_skills": matched,
                "location": job.location,
                "job_type": job.job_type,
                "description": (job.description or "")[:400],
            }
        )
    return payload
