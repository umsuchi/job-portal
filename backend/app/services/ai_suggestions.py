"""Stage 2 of the suggestion engine (spec §12): one Groq call, strict JSON out.

Contract with the rest of the app: this module never raises for an AI problem.
If Groq is unconfigured, slow, erroring or returns unusable JSON, the SQL
ranking from ``matcher`` is returned instead with ``source="fallback"`` (FR-9).
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
from app.models.job import Job
from app.models.suggestion import SuggestionCache
from app.services import matcher

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_REASON_WORDS = 22

SYSTEM_PROMPT = (
    "You are a job-matching assistant. Given a candidate's skills and a list of "
    "shortlisted jobs, return ONLY valid JSON: an object with a single key "
    '"suggestions" whose value is an array of objects with "job_id" (string, '
    'copied exactly from the input), "rank" (integer starting at 1) and '
    '"reason" (one sentence, max 20 words, naming the specific skills that '
    "match). Rank every job you are given, best fit first. Do not invent job "
    "ids. Do not include any text outside the JSON object."
)


def _fallback_reason(matched: Sequence[str]) -> str:
    skills = list(matched)[:3]
    if not skills:
        return "Related to your profile."
    if len(skills) == 1:
        return f"Matches your {skills[0]} experience."
    return "Matches your " + ", ".join(skills[:-1]) + f" and {skills[-1]} experience."


def _trim(reason: str) -> str:
    words = str(reason).strip().split()
    if len(words) > MAX_REASON_WORDS:
        words = words[:MAX_REASON_WORDS]
        return " ".join(words).rstrip(".,;:") + "…"
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


async def _call_groq(candidate_skills: Sequence[str], jobs_payload: List[Dict]) -> Optional[Dict]:
    if not settings.groq_api_key:
        logger.info("GROQ_API_KEY is not set — using SQL ranking.")
        return None

    body = {
        "model": settings.groq_model,
        "temperature": 0.2,
        "max_tokens": 1200,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "candidate_skills": list(candidate_skills),
                        "jobs": jobs_payload,
                    },
                    ensure_ascii=False,
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
        logger.warning("Groq call failed (%s) — falling back to SQL ranking.", exc)
        return None

    return _extract_json(content)


def _merge(
    pairs: List[Tuple[Job, List[str]]], parsed: Optional[Dict]
) -> Tuple[str, List[Dict[str, Any]]]:
    """Apply the model's ranking to the shortlist, or fall back to SQL order.

    The shortlist is the source of truth for which jobs exist; the model can
    only reorder and explain them. A hallucinated job_id is dropped, and any
    shortlisted job the model omitted is appended with a generated reason, so
    the candidate always sees the full ranked set.
    """
    by_id = {str(job.id): (job, matched) for job, matched in pairs}

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
                job, matched = by_id[job_id]
                reason = _trim(item.get("reason") or "") or _fallback_reason(matched)
                ordered.append(
                    {
                        "job_id": job_id,
                        "reason": reason,
                        "matched_skills": matched,
                        "overlap": len(matched),
                    }
                )

    source = "ai" if ordered else "fallback"

    covered = {item["job_id"] for item in ordered}
    for job, matched in pairs:
        job_id = str(job.id)
        if job_id in covered:
            continue
        ordered.append(
            {
                "job_id": job_id,
                "reason": _fallback_reason(matched),
                "matched_skills": matched,
                "overlap": len(matched),
            }
        )

    for index, item in enumerate(ordered, start=1):
        item["rank"] = index
    return source, ordered


async def generate(
    db: AsyncSession, candidate_id, candidate_skills: Sequence[str]
) -> Tuple[str, List[Dict[str, Any]], datetime]:
    """Build a fresh ranked list and persist it to the per-candidate cache."""
    pairs = await matcher.shortlist(db, candidate_skills)
    if not pairs:
        payload: List[Dict[str, Any]] = []
        source = "fallback"
    else:
        parsed = await _call_groq(candidate_skills, matcher.to_prompt_payload(pairs))
        source, payload = _merge(pairs, parsed)

    generated_at = datetime.now(timezone.utc)
    cache = await db.get(SuggestionCache, candidate_id)
    digest = matcher.skills_hash(candidate_skills)
    if cache is None:
        cache = SuggestionCache(candidate_id=candidate_id)
        db.add(cache)
    cache.skills_hash = digest
    cache.source = source
    cache.payload = payload
    cache.generated_at = generated_at
    await db.commit()

    return source, payload, generated_at


def is_fresh(cache: Optional[SuggestionCache], candidate_skills: Sequence[str]) -> bool:
    """FR-10 — reuse the cache while the skills are unchanged and it is < TTL old."""
    if cache is None:
        return False
    if cache.skills_hash != matcher.skills_hash(candidate_skills):
        return False
    generated = cache.generated_at
    if generated.tzinfo is None:
        generated = generated.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - generated
    return age < timedelta(minutes=settings.suggestions_cache_ttl_minutes)
