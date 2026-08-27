"""The multi-signal ranking (EP-5, extended).

Each test isolates one signal: two jobs identical on skills, differing only in
the thing under test. If the ranking ignored that signal, the test would fail.
"""
from __future__ import annotations

import pytest

from app.models.job import level_for_years
from app.services import matcher
from tests.conftest import JOB_BODY, make_actor


async def post(recruiter, **overrides):
    body = {**JOB_BODY, **overrides}
    resp = await recruiter.post("/jobs", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def ranked_titles(candidate):
    body = (await candidate.get("/suggestions", params={"refresh": True})).json()
    return [s["job"]["title"] for s in body["suggestions"]], body


async def profiled(client, **profile):
    actor = await make_actor(client, "candidate", full_name="Test Candidate")
    await actor.put("/auth/me", json=profile)
    return actor


BASE_SKILLS = ["React", "TypeScript", "Node.js"]


async def test_preferred_work_mode_outranks_an_identical_onsite_role(client, recruiter):
    await post(recruiter, title="Onsite Role", work_mode="onsite", location="Berlin, Germany")
    await post(recruiter, title="Remote Role", work_mode="remote", location="Remote")

    candidate = await profiled(client, skills=BASE_SKILLS, preferred_work_modes=["remote"])
    titles, _ = await ranked_titles(candidate)
    assert titles[0] == "Remote Role"


async def test_seniority_fit_outranks_a_distant_level(client, recruiter):
    await post(recruiter, title="Principal Role", experience_level="principal",
               min_years_experience=12)
    await post(recruiter, title="Junior Role", experience_level="junior",
               min_years_experience=1)

    candidate = await profiled(client, skills=BASE_SKILLS, years_experience=1,
                               experience_level="junior")
    titles, _ = await ranked_titles(candidate)
    assert titles[0] == "Junior Role"


async def test_matching_location_outranks_a_distant_one(client, recruiter):
    await post(recruiter, title="Far Role", work_mode="onsite", location="Reykjavik, Iceland")
    await post(recruiter, title="Near Role", work_mode="onsite", location="Dhaka, Bangladesh")

    candidate = await profiled(client, skills=BASE_SKILLS, preferred_locations=["Dhaka"])
    titles, _ = await ranked_titles(candidate)
    assert titles[0] == "Near Role"


async def test_location_preference_matches_a_partial_name(client, recruiter):
    """"Berlin" should match "Berlin, Germany" — and "Germany" should too."""
    await post(recruiter, title="Berlin Role", work_mode="onsite", location="Berlin, Germany")
    candidate = await profiled(client, skills=BASE_SKILLS, preferred_locations=["Germany"])
    _, body = await ranked_titles(candidate)
    assert any("Berlin" in s for s in body["suggestions"][0]["signals"])


async def test_preferred_employment_type_is_scored(client, recruiter):
    await post(recruiter, title="Full Time Role", job_type="full_time")
    await post(recruiter, title="Contract Role", job_type="contract")

    candidate = await profiled(client, skills=BASE_SKILLS, preferred_job_types=["contract"])
    titles, _ = await ranked_titles(candidate)
    assert titles[0] == "Contract Role"


async def test_salary_below_expectation_is_demoted(client, recruiter):
    await post(recruiter, title="Underpaid Role", salary_min=20000, salary_max=30000)
    await post(recruiter, title="Paid Role", salary_min=90000, salary_max=140000)

    candidate = await profiled(client, skills=BASE_SKILLS, desired_salary_min=80000)
    titles, _ = await ranked_titles(candidate)
    assert titles[0] == "Paid Role"


async def test_nice_to_have_skills_widen_the_shortlist(client, recruiter):
    """A job the candidate matches only on a nice-to-have still surfaces."""
    await post(recruiter, title="Nice To Have Only",
               required_skills=["Rust"], nice_to_have_skills=["React"])

    candidate = await profiled(client, skills=["React"])
    titles, body = await ranked_titles(candidate)
    assert "Nice To Have Only" in titles
    entry = next(s for s in body["suggestions"] if s["job"]["title"] == "Nice To Have Only")
    assert entry["matched_nice_to_have"] == ["React"]
    assert entry["overlap"] == 0


async def test_required_skills_outweigh_nice_to_haves(client, recruiter):
    await post(recruiter, title="Required Match",
               required_skills=["React"], nice_to_have_skills=["Rust"])
    await post(recruiter, title="Nice Match",
               required_skills=["Rust"], nice_to_have_skills=["React"])

    candidate = await profiled(client, skills=["React"])
    titles, _ = await ranked_titles(candidate)
    assert titles[0] == "Required Match"


async def test_every_suggestion_carries_readable_signals(client, recruiter):
    await post(recruiter, title="Fully Specified Role")
    candidate = await profiled(
        client, skills=BASE_SKILLS, years_experience=6, experience_level="senior",
        preferred_work_modes=["remote"], preferred_job_types=["full_time"],
        desired_salary_min=80000,
    )
    _, body = await ranked_titles(candidate)
    signals = body["suggestions"][0]["signals"]
    assert signals, "a fully-specified match should explain itself"
    assert any("Remote" in s for s in signals)
    assert any("Senior" in s for s in signals)
    assert all(isinstance(s, str) and s.strip() for s in signals)


async def test_changing_a_non_skill_preference_invalidates_the_cache(client, recruiter):
    """The old cache key hashed skills alone and would have served a stale list."""
    await post(recruiter, title="Some Role")
    candidate = await profiled(client, skills=BASE_SKILLS, preferred_work_modes=["onsite"])

    first = (await candidate.get("/suggestions")).json()
    assert first["cached"] is False
    assert (await candidate.get("/suggestions")).json()["cached"] is True

    await candidate.put("/auth/me", json={"preferred_work_modes": ["remote"]})
    assert (await candidate.get("/suggestions")).json()["cached"] is False


async def test_a_candidate_with_no_preferences_still_gets_ranked_results(client, recruiter):
    """Preferences are optional; their absence must not empty the dashboard."""
    await post(recruiter, title="Some Role")
    candidate = await profiled(client, skills=BASE_SKILLS)
    titles, body = await ranked_titles(candidate)
    assert titles == ["Some Role"]
    assert body["suggestions"][0]["reason"]


# ------------------------------------------------------------- unit level

@pytest.mark.parametrize("years,expected", [
    (0, "entry"), (1, "junior"), (2, "junior"), (3, "mid"),
    (6, "senior"), (9, "lead"), (15, "principal"), (None, None),
])
def test_level_inferred_from_years(years, expected):
    assert level_for_years(years) == expected


def test_profile_hash_covers_more_than_skills():
    class P:
        skills = ["React"]
        years_experience = 5
        experience_level = "senior"
        preferred_job_types = ["full_time"]
        preferred_work_modes = ["remote"]
        preferred_locations = ["Dhaka"]
        desired_salary_min = 80000
        location = "Dhaka"

    base = matcher.profile_hash(P())

    changed = P()
    changed.preferred_work_modes = ["onsite"]
    assert matcher.profile_hash(changed) != base

    same = P()
    same.skills = ["react"]  # casing only
    assert matcher.profile_hash(same) == base
