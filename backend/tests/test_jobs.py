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
