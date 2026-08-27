"""EP-3 + US-2.4 — apply, duplicate guard (FR-5), status lifecycle (FR-6), withdraw."""
from tests.conftest import JOB_BODY, make_actor


async def test_apply_once_only(candidate, job):
    first = await candidate.post("/applications",
                                 json={"job_id": job["id"], "cover_note": "Keen to help."})
    assert first.status_code == 201
    assert first.json()["status"] == "applied"

    second = await candidate.post("/applications", json={"job_id": job["id"]})
    assert second.status_code == 409


async def test_recruiters_cannot_apply(recruiter, job):
    assert (await recruiter.post("/applications", json={"job_id": job["id"]})).status_code == 403


async def test_cannot_apply_to_closed_job(candidate, recruiter, job):
    await recruiter.delete(f"/jobs/{job['id']}")
    resp = await candidate.post("/applications", json={"job_id": job["id"]})
    assert resp.status_code == 400


async def test_my_applications_sorted_and_enriched(candidate, recruiter, job):
    other = await recruiter.post("/jobs", json={**JOB_BODY, "title": "Backend Engineer"})
    await candidate.post("/applications", json={"job_id": job["id"]})
    await candidate.post("/applications", json={"job_id": other.json()["id"]})

    resp = await candidate.get("/applications/me")
    items = resp.json()
    assert len(items) == 2
    assert items[0]["applied_at"] >= items[1]["applied_at"]
    assert items[0]["job"]["company_name"] == "Acme Corp"


async def test_recruiter_sees_applicants_only_for_own_job(candidate, recruiter, other_recruiter, job):
    await candidate.post("/applications", json={"job_id": job["id"], "cover_note": "Hello"})

    mine = await recruiter.get(f"/jobs/{job['id']}/applications")
    assert mine.status_code == 200
    row = mine.json()[0]
    assert row["candidate"]["full_name"] == "Casey Candidate"
    assert row["candidate"]["skills"] == ["React", "Node.js", "PostgreSQL"]
    assert row["cover_note"] == "Hello"

    assert (await other_recruiter.get(f"/jobs/{job['id']}/applications")).status_code == 403


async def test_status_lifecycle_follows_the_state_machine(candidate, recruiter, job):
    app_id = (await candidate.post("/applications", json={"job_id": job["id"]})).json()["id"]

    # applied -> shortlisted is not a legal edge; it must go via reviewed.
    assert (await recruiter.patch(f"/applications/{app_id}/status",
                                  json={"status": "shortlisted"})).status_code == 409

    for step in ("reviewed", "shortlisted", "hired"):
        resp = await recruiter.patch(f"/applications/{app_id}/status", json={"status": step})
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == step

    # hired is terminal.
    assert (await recruiter.patch(f"/applications/{app_id}/status",
                                  json={"status": "rejected"})).status_code == 409


async def test_recruiter_cannot_set_withdrawn(candidate, recruiter, job):
    app_id = (await candidate.post("/applications", json={"job_id": job["id"]})).json()["id"]
    resp = await recruiter.patch(f"/applications/{app_id}/status", json={"status": "withdrawn"})
    assert resp.status_code == 422


async def test_foreign_recruiter_cannot_change_status(candidate, other_recruiter, job):
    app_id = (await candidate.post("/applications", json={"job_id": job["id"]})).json()["id"]
    resp = await other_recruiter.patch(f"/applications/{app_id}/status", json={"status": "reviewed"})
    assert resp.status_code == 403


async def test_withdraw_allowed_before_terminal_state(candidate, recruiter, job):
    app_id = (await candidate.post("/applications", json={"job_id": job["id"]})).json()["id"]
    await recruiter.patch(f"/applications/{app_id}/status", json={"status": "reviewed"})

    resp = await candidate.delete(f"/applications/{app_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "withdrawn"
    # And not twice.
    assert (await candidate.delete(f"/applications/{app_id}")).status_code == 409


async def test_withdraw_blocked_after_hire(candidate, recruiter, job):
    app_id = (await candidate.post("/applications", json={"job_id": job["id"]})).json()["id"]
    for step in ("reviewed", "shortlisted", "hired"):
        await recruiter.patch(f"/applications/{app_id}/status", json={"status": step})
    assert (await candidate.delete(f"/applications/{app_id}")).status_code == 409


async def test_candidate_cannot_withdraw_someone_elses_application(client, candidate, job):
    app_id = (await candidate.post("/applications", json={"job_id": job["id"]})).json()["id"]
    intruder = await make_actor(client, "candidate", full_name="Nosy")
    assert (await intruder.delete(f"/applications/{app_id}")).status_code == 404
