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
from app.models.job import EXPERIENCE_LEVELS, JOB_TYPES, WORK_MODES
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
        assert job["work_mode"] in WORK_MODES
        assert job["experience_level"] in EXPERIENCE_LEVELS
        assert job["required_skills"], f"{job['title']} has no required skills"
        assert job["salary_min"] <= job["salary_max"]
        assert len(job["description"]) >= 10


def test_jobs_carry_the_structured_detail():
    """A demo job with an empty responsibilities list shows an empty page."""
    for job in data.JOBS:
        for section in ("responsibilities", "requirements", "benefits"):
            assert job[section], f"{job['title']} has no {section}"
        assert job["nice_to_have_skills"], f"{job['title']} has no nice-to-haves"
        # A skill on both lists would be scored twice by the matcher.
        required = {s.lower() for s in job["required_skills"]}
        assert not required & {s.lower() for s in job["nice_to_have_skills"]}


def test_seed_covers_every_work_mode_and_several_levels():
    """So the filters and the ranking signals are all visible in the demo."""
    assert {j["work_mode"] for j in data.JOBS} == set(WORK_MODES)
    assert len({j["experience_level"] for j in data.JOBS}) >= 3
    assert len({j["job_type"] for j in data.JOBS}) >= 3


def test_profiles_carry_the_matching_inputs():
    for candidate in data.CANDIDATES:
        for field in ("avatar_url", "bio", "location", "years_experience",
                      "experience_level", "preferred_job_types",
                      "preferred_work_modes", "preferred_locations",
                      "desired_salary_min"):
            assert candidate.get(field), f"{candidate['full_name']} is missing {field}"
        assert candidate["experience_level"] in EXPERIENCE_LEVELS
        for job_type in candidate["preferred_job_types"]:
            assert job_type in JOB_TYPES
        for mode in candidate["preferred_work_modes"]:
            assert mode in WORK_MODES

    for recruiter in data.RECRUITERS:
        for field in ("avatar_url", "about", "industry", "headquarters"):
            assert recruiter.get(field), f"{recruiter['company_name']} is missing {field}"


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
    used |= {s for j in data.JOBS for s in j["nice_to_have_skills"]}

    unknown = sorted(used - known)
    assert not unknown, f"seed skills missing from the frontend catalogue: {unknown}"
