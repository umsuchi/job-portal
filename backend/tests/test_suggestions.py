"""EP-5 — shortlist, AI ranking, graceful fallback (FR-9), caching (FR-10)."""
import pytest
import pytest_asyncio

from app.services import ai_suggestions, matcher
from tests.conftest import JOB_BODY


@pytest_asyncio.fixture
async def catalogue(recruiter):
    """Three jobs with decreasing overlap against the candidate fixture's skills
    (React, Node.js, PostgreSQL)."""
    made = []
    for title, skills in [
        ("Full Stack Engineer", ["React", "Node.js", "PostgreSQL"]),   # 3
        ("Frontend Engineer", ["React", "CSS"]),                        # 1
        ("Rust Systems Engineer", ["Rust", "C++"]),                     # 0
    ]:
        resp = await recruiter.post("/jobs", json={**JOB_BODY, "title": title,
                                                   "required_skills": skills})
        made.append(resp.json())
    return made


async def test_only_candidates_get_suggestions(recruiter):
    assert (await recruiter.get("/suggestions")).status_code == 403


async def test_fallback_ranks_by_overlap_when_groq_is_unavailable(candidate, catalogue):
    """FR-9: no API key configured, so the SQL ranking is served — not an error."""
    resp = await candidate.get("/suggestions")
    assert resp.status_code == 200
    body = resp.json()

    assert body["source"] == "fallback"
    titles = [s["job"]["title"] for s in body["suggestions"]]
    assert titles == ["Full Stack Engineer", "Frontend Engineer"]
    assert [s["rank"] for s in body["suggestions"]] == [1, 2]
    assert body["suggestions"][0]["overlap"] == 3
    # Even without AI text, every card has a usable reason.
    assert "React" in body["suggestions"][0]["reason"]


async def test_candidate_without_skills_gets_an_empty_list(client, catalogue):
    from tests.conftest import make_actor
    blank = await make_actor(client, "candidate", full_name="No Skills")
    body = (await blank.get("/suggestions")).json()
    assert body["suggestions"] == []
    assert body["candidate_skills"] == []


async def test_ai_ranking_is_used_when_groq_responds(monkeypatch, candidate, catalogue):
    full_stack = next(j for j in catalogue if j["title"] == "Full Stack Engineer")
    frontend = next(j for j in catalogue if j["title"] == "Frontend Engineer")

    async def fake_groq(skills, jobs_payload):
        # Model reverses the SQL order and supplies its own reasons.
        return {"suggestions": [
            {"job_id": frontend["id"], "rank": 1, "reason": "Strong React fit for a focused frontend role."},
            {"job_id": full_stack["id"], "rank": 2, "reason": "Covers all three of your core skills."},
        ]}

    monkeypatch.setattr(ai_suggestions, "_call_groq", fake_groq)
    body = (await candidate.get("/suggestions", params={"refresh": True})).json()

    assert body["source"] == "ai"
    assert [s["job"]["title"] for s in body["suggestions"]] == [
        "Frontend Engineer", "Full Stack Engineer"
    ]
    assert body["suggestions"][0]["reason"].startswith("Strong React fit")


async def test_hallucinated_job_ids_are_dropped_and_omissions_backfilled(
    monkeypatch, candidate, catalogue
):
    frontend = next(j for j in catalogue if j["title"] == "Frontend Engineer")

    async def fake_groq(skills, jobs_payload):
        return {"suggestions": [
            {"job_id": "00000000-0000-0000-0000-000000000000", "rank": 1, "reason": "Invented."},
            {"job_id": frontend["id"], "rank": 2, "reason": "Real one."},
        ]}

    monkeypatch.setattr(ai_suggestions, "_call_groq", fake_groq)
    body = (await candidate.get("/suggestions", params={"refresh": True})).json()

    titles = [s["job"]["title"] for s in body["suggestions"]]
    assert "Frontend Engineer" in titles
    # The shortlisted job the model forgot is still present, with a generated reason.
    assert "Full Stack Engineer" in titles
    assert len(titles) == 2


async def test_unusable_model_output_falls_back(monkeypatch, candidate, catalogue):
    async def fake_groq(skills, jobs_payload):
        return {"not_what_we_asked_for": True}

    monkeypatch.setattr(ai_suggestions, "_call_groq", fake_groq)
    body = (await candidate.get("/suggestions", params={"refresh": True})).json()
    assert body["source"] == "fallback"
    assert len(body["suggestions"]) == 2


async def test_results_are_cached_then_invalidated_by_a_skill_change(candidate, catalogue):
    calls = {"n": 0}
    original = ai_suggestions.generate

    async def counting_generate(db, candidate_id, skills):
        calls["n"] += 1
        return await original(db, candidate_id, skills)

    ai_suggestions.generate = counting_generate
    try:
        first = (await candidate.get("/suggestions")).json()
        assert first["cached"] is False
        assert calls["n"] == 1

        second = (await candidate.get("/suggestions")).json()
        assert second["cached"] is True
        assert calls["n"] == 1  # FR-10: no second generation, no second Groq call

        # US-5.3: changing skills invalidates the cache.
        await candidate.put("/auth/me", json={"skills": ["Rust", "C++"]})
        third = (await candidate.get("/suggestions")).json()
        assert third["cached"] is False
        assert calls["n"] == 2
        assert [s["job"]["title"] for s in third["suggestions"]] == ["Rust Systems Engineer"]
    finally:
        ai_suggestions.generate = original


async def test_jobs_closed_after_caching_drop_out(candidate, recruiter, catalogue):
    full_stack = next(j for j in catalogue if j["title"] == "Full Stack Engineer")
    first = (await candidate.get("/suggestions")).json()
    assert len(first["suggestions"]) == 2

    await recruiter.delete(f"/jobs/{full_stack['id']}")
    second = (await candidate.get("/suggestions")).json()
    assert second["cached"] is True  # cache untouched...
    titles = [s["job"]["title"] for s in second["suggestions"]]
    assert "Full Stack Engineer" not in titles  # ...but the closed job is filtered out
    assert [s["rank"] for s in second["suggestions"]] == [1]


# ------------------------------------------------------------- unit-level

def test_skills_hash_is_order_and_case_insensitive():
    assert matcher.skills_hash(["React", "Node.js"]) == matcher.skills_hash(["node.js", "react"])
    assert matcher.skills_hash(["React"]) != matcher.skills_hash(["Rust"])


def test_overlap_is_case_insensitive():
    assert matcher.overlap(["React", "Go"], ["react"]) == ["React"]


@pytest.mark.parametrize("raw,expected_len", [
    ('{"suggestions": []}', 0),
    ('```json\n{"suggestions": []}\n```', 0),
    ('Here you go:\n{"suggestions": []}', 0),
])
def test_json_extraction_tolerates_wrapping(raw, expected_len):
    parsed = ai_suggestions._extract_json(raw)
    assert parsed is not None
    assert len(parsed["suggestions"]) == expected_len


def test_json_extraction_gives_up_cleanly():
    assert ai_suggestions._extract_json("I cannot help with that.") is None


def test_reason_is_trimmed_to_length():
    long = " ".join(["word"] * 40)
    assert len(ai_suggestions._trim(long).split()) <= ai_suggestions.MAX_REASON_WORDS + 1
