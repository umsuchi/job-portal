"""Stage 2 of the suggestion engine (spec §12): one Groq call, strict JSON out.

Contract with the rest of the app: this module never raises for an AI problem.
If Groq is unconfigured, slow, erroring or returns unusable JSON, the
deterministic ranking from ``matcher`` is returned instead with
``source="fallback"`` (FR-9).

The model now sees more than a skill list — the candidate's seniority, location
and preferences, and each job's description, work mode and salary band — so the
one-line reason can cite the thing that actually makes the role a fit, rather
than restating the tags.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.suggestion import SuggestionCache
from app.models.user import CandidateProfile
from app.services import matcher

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_REASON_WORDS = 24

SYSTEM_PROMPT = (
    "You are a job-matching assistant. You are given a candidate profile and a "
    "shortlist of jobs that already matched on skills. Rank the shortlist by how "
    "well each job fits this specific candidate, and explain each briefly.\n\n"
    "Weigh all of it, not just skills: seniority against the candidate's years and "
    "level, work mode and location against their stated preferences, employment "
    "type, and salary against what they want.\n\n"
    'Return ONLY valid JSON: an object with one key "suggestions", an array of '
    'objects with "job_id" (string, copied exactly from the input), "rank" '
    '(integer starting at 1) and "reason" (one sentence, max 20 words).\n\n'
    "Write each reason about THIS candidate — name the concrete thing that fits, "
    'such as "Remote and senior-level, matching your React and Node.js '
    'background." Never invent a job id, never mention a skill the candidate does '
    "not have, and include no text outside the JSON object."
)


def _fallback_reason(match: "matcher.Match") -> str:
    """A readable reason without the AI, built from the signals the scorer found."""
    skills = list(match.matched_skills)[:3]
    if skills:
        if len(skills) == 1:
            base = f"Matches your {skills[0]} experience"
        else:
            base = "Matches your " + ", ".join(skills[:-1]) + f" and {skills[-1]} experience"
    elif match.matched_nice_to_have:
        base = f"Uses your {match.matched_nice_to_have[0]} experience"
    else:
        base = "Related to your profile"

    # Add at most one non-skill signal, so the sentence stays a sentence.
    extra = next(
        (s for s in match.signals if s not in {", ".join(skills)} and "," not in s),
        None,
    )
    return f"{base}{f' · {extra}' if extra else ''}."


def _trim(reason: str) -> str:
    words = str(reason).strip().split()
    if len(words) > MAX_REASON_WORDS:
        return " ".join(words[:MAX_REASON_WORDS]).rstrip(".,;:") + "…"
    return " ".join(words)


def _extract_json(raw: str) -> Optional[Dict[str, Any]]:
    """Parse the model's reply, tolerating a stray code fence or preamble."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None


async def _call_groq(candidate: Dict, jobs_payload: List[Dict]) -> Optional[Dict]:
    if not settings.groq_api_key:
        logger.info("GROQ_API_KEY is not set — using the deterministic ranking.")
        return None

    body = {
        "model": settings.groq_model,
        "temperature": 0.2,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {"candidate": candidate, "jobs": jobs_payload}, ensure_ascii=False
                ),
            },
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=settings.groq_timeout_seconds) as client:
            resp = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                json=body,
            )
        if resp.status_code != 200:
            logger.warning("Groq returned %s: %s", resp.status_code, resp.text[:300])
            return None
        content = resp.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        logger.warning("Groq call failed (%s) — falling back to the ranking.", exc)
        return None

    return _extract_json(content)


def _merge(
    matches: List["matcher.Match"], parsed: Optional[Dict]
) -> Tuple[str, List[Dict[str, Any]]]:
    """Apply the model's ranking to the shortlist, or keep the scorer's order.

    The shortlist is the source of truth for which jobs exist; the model can only
    reorder and explain them. A hallucinated job_id is dropped, and any
    shortlisted job the model omitted is appended with a generated reason, so
    the candidate always sees the full ranked set.
    """
    by_id = {str(m.job.id): m for m in matches}

    def entry(match: "matcher.Match", reason: str) -> Dict[str, Any]:
        return {
            "job_id": str(match.job.id),
            "reason": reason,
            "matched_skills": match.matched_skills,
            "matched_nice_to_have": match.matched_nice_to_have,
            "signals": match.signals,
            "overlap": match.overlap,
            "score": round(match.score, 2),
        }

    ordered: List[Dict[str, Any]] = []
    if parsed:
        raw_items = parsed.get("suggestions")
        if isinstance(parsed, list):
            raw_items = parsed
        if isinstance(raw_items, list):
            seen = set()
            for item in raw_items:
                if not isinstance(item, dict):
                    continue
                job_id = str(item.get("job_id", ""))
                if job_id not in by_id or job_id in seen:
                    continue
                seen.add(job_id)
                match = by_id[job_id]
                reason = _trim(item.get("reason") or "") or _fallback_reason(match)
                ordered.append(entry(match, reason))

    source = "ai" if ordered else "fallback"

    covered = {item["job_id"] for item in ordered}
    for match in matches:
        if str(match.job.id) in covered:
            continue
        ordered.append(entry(match, _fallback_reason(match)))

    for index, item in enumerate(ordered, start=1):
        item["rank"] = index
    return source, ordered


async def generate(
    db: AsyncSession, candidate_id, profile: Optional[CandidateProfile]
) -> Tuple[str, List[Dict[str, Any]], datetime]:
    """Build a fresh ranked list and persist it to the per-candidate cache."""
    matches = await matcher.shortlist(db, profile)
    if not matches:
        payload: List[Dict[str, Any]] = []
        source = "fallback"
    else:
        parsed = await _call_groq(
            matcher.candidate_payload(profile), matcher.to_prompt_payload(matches)
        )
        source, payload = _merge(matches, parsed)

    generated_at = datetime.now(timezone.utc)
    cache = await db.get(SuggestionCache, candidate_id)
    if cache is None:
        cache = SuggestionCache(candidate_id=candidate_id)
        db.add(cache)
    cache.skills_hash = matcher.profile_hash(profile)
    cache.source = source
    cache.payload = payload
    cache.generated_at = generated_at
    await db.commit()

    return source, payload, generated_at


def is_fresh(cache: Optional[SuggestionCache], profile: Optional[CandidateProfile]) -> bool:
    """FR-10 — reuse the cache while the profile is unchanged and it is < TTL old.

    The hash covers every field the ranking reads, not just skills, so editing a
    location preference invalidates it too.
    """
    if cache is None:
        return False
    if cache.skills_hash != matcher.profile_hash(profile):
        return False
    generated = cache.generated_at
    if generated.tzinfo is None:
        generated = generated.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - generated < timedelta(
        minutes=settings.suggestions_cache_ttl_minutes
    )
