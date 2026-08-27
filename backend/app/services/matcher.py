"""Stage 1 of the suggestion engine (spec §12): deterministic scoring in SQL+Python.

Still no API call and no embeddings. Postgres narrows the field using the GIN
indexes on the two skill arrays; the ranking then scores each surviving job on
several signals rather than counting one.

Why more than skills: a Senior React role in Berlin and a Junior React role that
is remote overlap identically on skills, but they are not equally good matches
for a candidate with eight years who only wants remote work. Every signal below
exists to separate cases skill-overlap alone cannot.

Each signal returns a contribution and a short human-readable label. The labels
are what the UI shows as match chips and what the AI prompt gets as grounding, so
a score is never an unexplained number.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import (
    EXPERIENCE_LEVEL_RANK,
    JOB_OPEN,
    Job,
    level_for_years,
    today,
)
from app.models.user import CandidateProfile

SHORTLIST_SIZE = 10
# Widened pool the ranking runs over before trimming to SHORTLIST_SIZE.
CANDIDATE_POOL = 120

# Relative worth of each signal. Skills still dominate — the rest break ties and
# demote roles that match on paper but not in practice.
W_REQUIRED_SKILL = 10.0
W_NICE_TO_HAVE_SKILL = 3.0
W_COVERAGE = 6.0          # share of the job's requirements the candidate meets
W_WORK_MODE = 5.0
W_LOCATION = 4.0
W_JOB_TYPE = 4.0
W_SENIORITY = 6.0
W_SALARY = 3.0
W_FRESHNESS = 1.5


def normalize(skill: str) -> str:
    return " ".join(skill.strip().lower().split())


def profile_hash(profile: Optional[CandidateProfile]) -> str:
    """Digest of everything the ranking depends on.

    The suggestion cache is keyed on this, so editing *any* matching input —
    skills, seniority, preferences — invalidates it without an explicit delete
    (FR-10). It used to hash skills alone, which silently served stale results
    when a candidate changed their preferred locations.
    """
    if profile is None:
        return hashlib.sha256(b"").hexdigest()

    parts = [
        "|".join(sorted(normalize(s) for s in (profile.skills or []) if s.strip())),
        str(profile.years_experience or ""),
        profile.experience_level or "",
        "|".join(sorted(normalize(t) for t in (profile.preferred_job_types or []))),
        "|".join(sorted(normalize(m) for m in (profile.preferred_work_modes or []))),
        "|".join(sorted(normalize(l) for l in (profile.preferred_locations or []))),
        str(profile.desired_salary_min or ""),
        normalize(profile.location or ""),
    ]
    return hashlib.sha256("␟".join(parts).encode("utf-8")).hexdigest()


def overlap(job_skills: Sequence[str], candidate_skills: Sequence[str]) -> List[str]:
    """Case-insensitive intersection, returned in the job's original casing."""
    wanted = {normalize(s) for s in candidate_skills}
    return [s for s in job_skills if normalize(s) in wanted]


def _location_matches(job: Job, profile: CandidateProfile) -> bool:
    """Does the job's location satisfy one of the candidate's preferences?

    Substring both ways, because "Berlin" should match "Berlin, Germany" and a
    preference of "Germany" should match it too.
    """
    wanted = [normalize(l) for l in (profile.preferred_locations or []) if l.strip()]
    if not wanted:
        return False
    here = normalize(job.location)
    return any(w in here or here in w for w in wanted)


@dataclass
class Signal:
    """One reason a job scored the way it did."""
    label: str
    weight: float


@dataclass
class Match:
    job: Job
    score: float
    matched_skills: List[str] = field(default_factory=list)
    matched_nice_to_have: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)

    @property
    def overlap(self) -> int:
        return len(self.matched_skills)


def score(job: Job, profile: Optional[CandidateProfile], newest_first_rank: float = 0.0) -> Match:
    """Score one job for one candidate, collecting the reasons as we go."""
    skills = list(getattr(profile, "skills", None) or [])
    matched = overlap(list(job.required_skills or []), skills)
    matched_nice = overlap(list(job.nice_to_have_skills or []), skills)
    missing = [
        s for s in (job.required_skills or [])
        if normalize(s) not in {normalize(m) for m in matched}
    ]

    total = 0.0
    signals: List[Signal] = []

    # --- skills -------------------------------------------------------------
    total += W_REQUIRED_SKILL * len(matched)
    total += W_NICE_TO_HAVE_SKILL * len(matched_nice)
    if matched:
        shown = ", ".join(matched[:3])
        extra = len(matched) - 3
        signals.append(Signal(f"{shown}{f' +{extra} more' if extra > 0 else ''}", 0))

    required_count = len(job.required_skills or [])
    if required_count:
        coverage = len(matched) / required_count
        total += W_COVERAGE * coverage
        if coverage >= 0.999:
            signals.append(Signal("Meets every requirement", W_COVERAGE))

    if profile is None:
        return Match(job=job, score=total, matched_skills=matched,
                     matched_nice_to_have=matched_nice, missing_skills=missing,
                     signals=[s.label for s in signals])

    # --- work mode ----------------------------------------------------------
    modes = [normalize(m) for m in (profile.preferred_work_modes or [])]
    if modes:
        if normalize(job.work_mode) in modes:
            total += W_WORK_MODE
            signals.append(Signal(f"{job.work_mode.title()} — as you prefer", W_WORK_MODE))
        else:
            # A wanted-remote candidate should not top out on an onsite role.
            total -= W_WORK_MODE * 0.5

    # --- location -----------------------------------------------------------
    if job.work_mode == "remote":
        # Remote satisfies any location preference, so it never counts against.
        total += W_LOCATION * 0.5
    elif _location_matches(job, profile):
        total += W_LOCATION
        signals.append(Signal(f"In {job.location}", W_LOCATION))
    elif profile.preferred_locations:
        total -= W_LOCATION * 0.5

    # --- employment type ----------------------------------------------------
    types = [normalize(t) for t in (profile.preferred_job_types or [])]
    if types:
        if normalize(job.job_type) in types:
            total += W_JOB_TYPE
            signals.append(Signal(job.job_type.replace("_", "-").title(), W_JOB_TYPE))
        else:
            total -= W_JOB_TYPE * 0.5

    # --- seniority ----------------------------------------------------------
    candidate_level = profile.experience_level or level_for_years(profile.years_experience)
    if candidate_level and job.experience_level:
        distance = abs(
            EXPERIENCE_LEVEL_RANK.get(candidate_level, 2)
            - EXPERIENCE_LEVEL_RANK.get(job.experience_level, 2)
        )
        # Same level scores full; each step away costs a third, floored at -1.
        total += W_SENIORITY * max(-1.0, 1.0 - distance / 3.0)
        if distance == 0:
            signals.append(Signal(f"{job.experience_level.title()} level", W_SENIORITY))

    years = profile.years_experience
    if years is not None and job.min_years_experience is not None:
        if years >= job.min_years_experience:
            total += W_SENIORITY * 0.5
            if job.min_years_experience > 0:
                signals.append(
                    Signal(f"{job.min_years_experience}+ years — you have {years}", 0)
                )
        else:
            # Under the stated bar: demote, but never hide. The bar is often soft.
            total -= W_SENIORITY * 0.5

    # --- salary -------------------------------------------------------------
    wanted_salary = profile.desired_salary_min
    if wanted_salary and job.salary_max:
        if job.salary_max >= wanted_salary:
            total += W_SALARY
            signals.append(Signal("Pays in your range", W_SALARY))
        else:
            total -= W_SALARY

    # --- recency ------------------------------------------------------------
    total += W_FRESHNESS * newest_first_rank

    return Match(
        job=job,
        score=total,
        matched_skills=matched,
        matched_nice_to_have=matched_nice,
        missing_skills=missing,
        signals=[s.label for s in signals],
    )


async def shortlist(
    db: AsyncSession, profile: Optional[CandidateProfile], limit: int = SHORTLIST_SIZE
) -> List[Match]:
    """Open jobs worth showing this candidate, best first.

    The SQL prefilter still leans on the GIN indexes: a job qualifies if it shares
    a skill with the candidate on either the required or the nice-to-have list.
    Everything finer-grained happens in Python on that bounded set, which keeps
    the query one index scan rather than a scoring expression Postgres would have
    to evaluate per row.
    """
    skills = [s.strip() for s in (getattr(profile, "skills", None) or []) if s and s.strip()]
    if not skills:
        return []

    # Array overlap is exact-match, so probe with both the original casing and a
    # normalized copy; the precise ranking happens below in Python.
    probe = list({*skills, *(normalize(s) for s in skills)})

    rows = await db.execute(
        select(Job)
        .where(
            Job.status == JOB_OPEN,
            # Never recommend something that can no longer be applied to.
            or_(Job.application_deadline.is_(None), Job.application_deadline >= today()),
            or_(
                Job.required_skills.overlap(probe),
                Job.nice_to_have_skills.overlap(probe),
            ),
        )
        .order_by(Job.created_at.desc())
        .limit(CANDIDATE_POOL)
    )
    jobs = list(rows.scalars().all())
    if not jobs:
        return []

    # Newest job gets 1.0, oldest 0.0 — a mild nudge, never a deciding factor.
    span = max(len(jobs) - 1, 1)
    matches = [
        score(job, profile, newest_first_rank=1.0 - index / span)
        for index, job in enumerate(jobs)
    ]

    # A job with no skill overlap at all only arrived via a nice-to-have; keep it
    # only if something else about it actually fits.
    matches = [m for m in matches if m.matched_skills or m.matched_nice_to_have]
    matches.sort(key=lambda m: (m.score, m.overlap, m.job.created_at), reverse=True)
    return matches[:limit]


def to_prompt_payload(matches: List[Match]) -> List[Dict]:
    """Trim each job to what the model needs to rank and explain it."""
    payload = []
    for match in matches:
        job = match.job
        payload.append(
            {
                "job_id": str(job.id),
                "title": job.title,
                "company": getattr(
                    getattr(job.recruiter, "recruiter_profile", None), "company_name", None
                ),
                "summary": (job.description or "")[:400],
                "required_skills": list(job.required_skills or []),
                "nice_to_have_skills": list(job.nice_to_have_skills or []),
                "matched_skills": match.matched_skills,
                "missing_skills": match.missing_skills,
                "experience_level": job.experience_level,
                "min_years_experience": job.min_years_experience,
                "location": job.location,
                "work_mode": job.work_mode,
                "job_type": job.job_type,
                "salary_range": (
                    f"{job.salary_min}-{job.salary_max} {job.salary_currency}"
                    if job.salary_min or job.salary_max else None
                ),
                "responsibilities": list(job.responsibilities or [])[:4],
                "days_until_deadline": job.days_until_deadline,
            }
        )
    return payload


def candidate_payload(profile: Optional[CandidateProfile]) -> Dict:
    """What the model is told about the person it is matching."""
    if profile is None:
        return {"skills": []}
    return {
        "headline": profile.headline,
        "bio": (profile.bio or "")[:400] or None,
        "skills": list(profile.skills or []),
        "years_experience": profile.years_experience,
        "experience_level": profile.experience_level
                            or level_for_years(profile.years_experience),
        "current_location": profile.location,
        "preferred_locations": list(profile.preferred_locations or []),
        "preferred_work_modes": list(profile.preferred_work_modes or []),
        "preferred_job_types": list(profile.preferred_job_types or []),
        "desired_salary_min": profile.desired_salary_min,
    }


# Kept for callers that only have a skill list (and for the older tests).
def skills_hash(skills: Sequence[str]) -> str:
    joined = "|".join(sorted(normalize(s) for s in skills if s.strip()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
