"""EP-2 — job posting, ownership (FR-4), role gates (FR-3), browse filters."""
from tests.conftest import JOB_BODY


async def test_only_recruiters_can_post(candidate, recruiter):
    assert (await candidate.post("/jobs", json=JOB_BODY)).status_code == 403
    assert (await recruiter.post("/jobs", json=JOB_BODY)).status_code == 201


async def test_job_requires_at_least_one_skill(recruiter):
    body = {**JOB_BODY, "required_skills": []}
    assert (await recruiter.post("/jobs", json=body)).status_code == 422


async def test_salary_range_is_validated(recruiter):
    body = {**JOB_BODY, "salary_min": 200000, "salary_max": 100000}
    assert (await recruiter.post("/jobs", json=body)).status_code == 422


async def test_non_owner_cannot_edit_or_close(job, other_recruiter):
    assert (await other_recruiter.put(f"/jobs/{job['id']}", json={"title": "Hijacked"})).status_code == 403
    assert (await other_recruiter.delete(f"/jobs/{job['id']}")).status_code == 403


async def test_owner_can_edit_and_close(job, recruiter, client):
    resp = await recruiter.put(f"/jobs/{job['id']}", json={"title": "Staff React Engineer"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Staff React Engineer"

    closed = await recruiter.delete(f"/jobs/{job['id']}")
    assert closed.json()["status"] == "closed"
    # Closed jobs disappear from the public browse and detail views.
    assert (await client.get(f"/jobs/{job['id']}")).status_code == 404
    assert all(j["id"] != job["id"] for j in (await client.get("/jobs")).json()["items"])
    # ...but the owner can still see it.
    assert (await recruiter.get(f"/jobs/{job['id']}")).status_code == 200


async def test_browse_filters(job, recruiter, client):
    await recruiter.post("/jobs", json={
        **JOB_BODY, "title": "Data Engineer", "required_skills": ["Python", "Airflow"],
        "location": "Berlin", "job_type": "full_time",
    })

    by_keyword = await client.get("/jobs", params={"q": "React"})
    assert [j["title"] for j in by_keyword.json()["items"]] == ["Senior React Engineer"]

    by_skill = await client.get("/jobs", params={"skill": "Airflow"})
    assert [j["title"] for j in by_skill.json()["items"]] == ["Data Engineer"]

    by_location = await client.get("/jobs", params={"location": "berl"})
    assert len(by_location.json()["items"]) == 1

    by_type = await client.get("/jobs", params={"job_type": "remote"})
    assert all(j["job_type"] == "remote" for j in by_type.json()["items"])

    none = await client.get("/jobs", params={"skill": ["COBOL"]})
    assert none.json()["total"] == 0


async def test_has_applied_flag_for_candidate(job, candidate):
    before = await candidate.get("/jobs")
    assert before.json()["items"][0]["has_applied"] is False
    await candidate.post("/applications", json={"job_id": job["id"]})
    after = await candidate.get("/jobs")
    assert after.json()["items"][0]["has_applied"] is True


async def test_mine_filter_requires_recruiter(candidate, recruiter, job):
    assert (await candidate.get("/jobs", params={"mine": True})).status_code == 403
    mine = await recruiter.get("/jobs", params={"mine": True, "include_closed": True})
    assert mine.json()["total"] == 1


# ------------------------------------------------- extended job detail (EP-2)

async def test_job_carries_structured_detail(recruiter):
    resp = await recruiter.post("/jobs", json={
        **JOB_BODY,
        "responsibilities": ["Own the frontend", "Mentor two engineers"],
        "requirements": ["5+ years of React"],
        "benefits": ["Fully remote"],
        "nice_to_have_skills": ["Storybook", "Web Performance"],
        "experience_level": "senior",
        "min_years_experience": 5,
        "work_mode": "remote",
        "salary_currency": "eur",
    })
    assert resp.status_code == 201
    job = resp.json()
    assert job["responsibilities"] == ["Own the frontend", "Mentor two engineers"]
    assert job["nice_to_have_skills"] == ["Storybook", "Web Performance"]
    assert job["experience_level"] == "senior"
    assert job["work_mode"] == "remote"
    assert job["salary_currency"] == "EUR"  # normalized


async def test_a_skill_cannot_be_both_required_and_nice_to_have(recruiter):
    """Otherwise the matcher would score it twice."""
    resp = await recruiter.post("/jobs", json={
        **JOB_BODY,
        "required_skills": ["React", "TypeScript"],
        "nice_to_have_skills": ["React", "Storybook"],
    })
    assert resp.status_code == 201
    assert resp.json()["nice_to_have_skills"] == ["Storybook"]


async def test_work_mode_and_experience_filters(recruiter, client):
    await recruiter.post("/jobs", json={
        **JOB_BODY, "title": "Onsite Junior", "work_mode": "onsite",
        "experience_level": "junior", "location": "Dhaka",
    })
    await recruiter.post("/jobs", json={
        **JOB_BODY, "title": "Remote Senior", "work_mode": "remote",
        "experience_level": "senior",
    })

    remote = await client.get("/jobs", params={"work_mode": "remote"})
    assert [j["title"] for j in remote.json()["items"]] == ["Remote Senior"]

    junior = await client.get("/jobs", params={"experience_level": "junior"})
    assert [j["title"] for j in junior.json()["items"]] == ["Onsite Junior"]


async def test_skill_filter_also_matches_nice_to_haves(recruiter, client):
    await recruiter.post("/jobs", json={
        **JOB_BODY, "title": "Rust Role",
        "required_skills": ["Rust"], "nice_to_have_skills": ["React"],
    })
    found = await client.get("/jobs", params={"skill": "React"})
    assert "Rust Role" in [j["title"] for j in found.json()["items"]]


async def test_job_embeds_the_company_profile(recruiter, client):
    await recruiter.put("/auth/me", json={
        "avatar_url": "https://example.com/logo.png",
        "industry": "Developer tooling",
        "about": "What we do.",
    })
    job = (await recruiter.post("/jobs", json=JOB_BODY)).json()
    detail = (await client.get(f"/jobs/{job['id']}")).json()
    assert detail["company"]["name"] == "Acme Corp"
    assert detail["company"]["avatar_url"] == "https://example.com/logo.png"
    assert detail["company"]["industry"] == "Developer tooling"
    # The flat field is kept for older callers.
    assert detail["company_name"] == "Acme Corp"


async def test_invalid_job_enums_are_rejected(recruiter):
    for bad in ({"job_type": "remote"},          # moved to work_mode
                {"work_mode": "telepathic"},
                {"experience_level": "wizard"},
                {"min_years_experience": -1}):
        resp = await recruiter.post("/jobs", json={**JOB_BODY, **bad})
        assert resp.status_code == 422, f"{bad} should have been rejected"
