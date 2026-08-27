"""Guards on the seed content itself (scripts/data.py).

These are cheap structural checks — they do not touch the database. What they
protect is the thing that silently breaks: seed skills drifting away from the
frontend catalogue, so the array-overlap match stops firing and the dashboard
looks empty for no visible reason.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.models.application import APPLICATION_STATUSES
from app.models.job import JOB_TYPES
from scripts import data

CATALOGUE = (
    Path(__file__).resolve().parents[2] / "frontend" / "src" / "lib" / "skills.ts"
)


def catalogue_skills() -> set[str]:
    """Canonical names from the frontend catalogue, via its `s('Name', ...)` rows."""
    source = CATALOGUE.read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r"^  s\('((?:[^'\\]|\\.)+)'", source, re.M)}


def test_fifteen_of_each():
    assert len(data.RECRUITERS) == 15
    assert len(data.CANDIDATES) == 15
    assert len(data.JOBS) == 15


def test_emails_are_unique():
    emails = [r["email"] for r in data.RECRUITERS] + [c["email"] for c in data.CANDIDATES]
    assert len(emails) == len(set(emails))


def test_jobs_reference_real_recruiters_and_valid_enums():
    for job in data.JOBS:
        assert 0 <= job["recruiter"] < len(data.RECRUITERS)
        assert job["job_type"] in JOB_TYPES
        assert job["required_skills"], f"{job['title']} has no required skills"
        assert job["salary_min"] <= job["salary_max"]
        assert len(job["description"]) >= 10


def test_applications_are_valid_and_unique_per_pair():
    seen = set()
    for cand_i, job_i, status, _note in data.APPLICATIONS:
        assert 0 <= cand_i < len(data.CANDIDATES)
        assert 0 <= job_i < len(data.JOBS)
        assert status in APPLICATION_STATUSES
        # FR-5 would reject a duplicate at the database, so never seed one.
        assert (cand_i, job_i) not in seen
        seen.add((cand_i, job_i))


def test_status_spread_covers_every_state():
    """A demo where every application says "applied" shows nothing interesting."""
    used = {status for _c, _j, status, _n in data.APPLICATIONS}
    assert used == set(APPLICATION_STATUSES)


def test_threads_point_at_seeded_applications():
    for app_index, turns in data.THREADS:
        assert 0 <= app_index < len(data.APPLICATIONS)
        assert turns
        for sender, body in turns:
            assert sender in {"candidate", "recruiter"}
            assert body.strip()


def test_every_candidate_matches_at_least_one_job():
    """Otherwise that candidate's dashboard is empty and the demo looks broken."""
    job_skills = [{s.lower() for s in job["required_skills"]} for job in data.JOBS]
    for candidate in data.CANDIDATES:
        mine = {s.lower() for s in candidate["skills"]}
        assert any(mine & required for required in job_skills), (
            f"{candidate['full_name']} matches no seeded job"
        )


@pytest.mark.skipif(not CATALOGUE.exists(), reason="frontend not checked out")
def test_seed_skills_use_catalogue_spellings():
    """Seed skills must be spelled exactly as the frontend catalogue spells them.

    Postgres array overlap is an exact match, so "postgres" here and
    "PostgreSQL" in the picker would never meet.
    """
    known = catalogue_skills()
    assert len(known) > 200, "catalogue parsed as suspiciously small"

    used = {s for c in data.CANDIDATES for s in c["skills"]}
    used |= {s for j in data.JOBS for s in j["required_skills"]}

    unknown = sorted(used - known)
    assert not unknown, f"seed skills missing from the frontend catalogue: {unknown}"
