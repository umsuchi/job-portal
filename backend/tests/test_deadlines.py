"""Application deadlines and the expired state (EP-6).

The deadline is inclusive: a job whose deadline is today still accepts
applications, and only becomes expired tomorrow. Most of these tests sit on that
boundary, because that is where an off-by-one would live.
"""
from __future__ import annotations

from datetime import timedelta

import pytest
import pytest_asyncio

from app.models.job import today
from tests.conftest import JOB_BODY, make_actor


def in_days(days: int) -> str:
    return (today() + timedelta(days=days)).isoformat()


async def post(recruiter, **overrides):
    resp = await recruiter.post("/jobs", json={**JOB_BODY, **overrides})
    assert resp.status_code == 201, resp.text
    return resp.json()


async def expire(recruiter, job_id, days_ago: int = 1):
    """Push a deadline into the past.

    Done through the API rather than the database, which also proves the update
    path allows a past deadline — an expired post has to stay editable.
    """
    resp = await recruiter.put(
        f"/jobs/{job_id}", json={"application_deadline": in_days(-days_ago)}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ------------------------------------------------------------- the boundary

async def test_deadline_today_still_accepts_applications(candidate, recruiter):
    """Inclusive: you have all of the deadline day to apply."""
    job = await post(recruiter, application_deadline=in_days(0))
    assert job["is_expired"] is False
    assert job["days_until_deadline"] == 0
    assert job["accepts_applications"] is True

    resp = await candidate.post("/applications", json={"job_id": job["id"]})
    assert resp.status_code == 201


async def test_deadline_yesterday_is_expired(candidate, recruiter):
    job = await post(recruiter, application_deadline=in_days(7))
    job = await expire(recruiter, job["id"], days_ago=1)

    assert job["is_expired"] is True
    assert job["days_until_deadline"] == -1
    assert job["accepts_applications"] is False

    resp = await candidate.post("/applications", json={"job_id": job["id"]})
    assert resp.status_code == 400
    assert "deadline" in resp.json()["detail"].lower()


async def test_no_deadline_never_expires(candidate, recruiter):
    job = await post(recruiter, application_deadline=None)
    assert job["application_deadline"] is None
    assert job["is_expired"] is False
    assert job["days_until_deadline"] is None
    assert job["accepts_applications"] is True
    assert (await candidate.post("/applications", json={"job_id": job["id"]})).status_code == 201


# -------------------------------------------------------------- validation

async def test_a_past_deadline_is_rejected_on_create(recruiter):
    """Guards the obvious typo — posting a role that is dead on arrival."""
    resp = await recruiter.post(
        "/jobs", json={**JOB_BODY, "application_deadline": in_days(-1)}
    )
    assert resp.status_code == 422
    assert "past" in resp.text.lower()


async def test_an_expired_post_stays_editable(recruiter):
    """Otherwise a recruiter could never fix a typo on an expired post."""
    job = await post(recruiter, application_deadline=in_days(2))
    await expire(recruiter, job["id"])

    resp = await recruiter.put(f"/jobs/{job['id']}", json={"title": "Renamed While Expired"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Renamed While Expired"


async def test_extending_the_deadline_revives_the_post(candidate, recruiter):
    job = await post(recruiter, application_deadline=in_days(1))
    await expire(recruiter, job["id"])
    assert (await candidate.post("/applications", json={"job_id": job["id"]})).status_code == 400

    revived = await recruiter.put(
        f"/jobs/{job['id']}", json={"application_deadline": in_days(30)}
    )
    assert revived.json()["is_expired"] is False
    assert (await candidate.post("/applications", json={"job_id": job["id"]})).status_code == 201


# ---------------------------------------------------------------- browsing

async def test_expired_jobs_are_hidden_from_browse_but_reachable(client, recruiter):
    live = await post(recruiter, title="Live Role", application_deadline=in_days(10))
    dead = await post(recruiter, title="Dead Role", application_deadline=in_days(1))
    await expire(recruiter, dead["id"])

    titles = [j["title"] for j in (await client.get("/jobs")).json()["items"]]
    assert "Live Role" in titles
    assert "Dead Role" not in titles

    # Opting in brings it back...
    titles = [
        j["title"]
        for j in (await client.get("/jobs", params={"include_expired": True})).json()["items"]
    ]
    assert "Dead Role" in titles

    # ...and a direct link always works, so a bookmark does not 404.
    detail = await client.get(f"/jobs/{dead['id']}")
    assert detail.status_code == 200
    assert detail.json()["is_expired"] is True


async def test_a_recruiter_always_sees_their_own_expired_posts(recruiter):
    dead = await post(recruiter, title="Dead Role", application_deadline=in_days(1))
    await expire(recruiter, dead["id"])

    mine = await recruiter.get("/jobs", params={"mine": True, "include_closed": True})
    assert "Dead Role" in [j["title"] for j in mine.json()["items"]]


# ------------------------------------------------------------- suggestions

async def test_expired_jobs_are_never_recommended(client, recruiter):
    await post(recruiter, title="Live Role", application_deadline=in_days(10))
    dead = await post(recruiter, title="Dead Role", application_deadline=in_days(1))
    await expire(recruiter, dead["id"])

    seeker = await make_actor(client, "candidate", full_name="Seeker")
    await seeker.put("/auth/me", json={"skills": ["React", "TypeScript", "Node.js"]})

    body = (await seeker.get("/suggestions", params={"refresh": True})).json()
    titles = [s["job"]["title"] for s in body["suggestions"]]
    assert "Live Role" in titles
    assert "Dead Role" not in titles


async def test_a_job_that_expires_after_caching_drops_out(client, recruiter):
    """The cache holds job ids; expiry is re-checked when they are rehydrated."""
    job = await post(recruiter, title="Soon Dead", application_deadline=in_days(1))
    seeker = await make_actor(client, "candidate", full_name="Seeker")
    await seeker.put("/auth/me", json={"skills": ["React", "TypeScript", "Node.js"]})

    first = (await seeker.get("/suggestions")).json()
    assert "Soon Dead" in [s["job"]["title"] for s in first["suggestions"]]

    await expire(recruiter, job["id"])

    second = (await seeker.get("/suggestions")).json()
    assert second["cached"] is True          # the cache itself is untouched...
    assert "Soon Dead" not in [s["job"]["title"] for s in second["suggestions"]]


# -------------------------------------------------------- existing records

async def test_an_existing_application_survives_the_deadline(candidate, recruiter):
    """Expiry stops new applications; it does not void the ones already in."""
    job = await post(recruiter, application_deadline=in_days(2))
    application = (await candidate.post("/applications", json={"job_id": job["id"]})).json()
    await expire(recruiter, job["id"])

    mine = (await candidate.get("/applications/me")).json()
    row = next(a for a in mine if a["id"] == application["id"])
    assert row["status"] == "applied"
    assert row["job"]["is_expired"] is True

    # And the recruiter can still move it along.
    resp = await recruiter.patch(
        f"/applications/{application['id']}/status", json={"status": "reviewed"}
    )
    assert resp.status_code == 200


# -------------------------------------------------------------- unit level

@pytest.mark.parametrize("offset,expired,days", [
    (5, False, 5), (1, False, 1), (0, False, 0), (-1, True, -1), (-30, True, -30),
])
def test_derived_state_is_computed_from_the_offset(offset, expired, days):
    from app.models.job import Job

    job = Job(application_deadline=today() + timedelta(days=offset), status="open")
    assert job.is_expired is expired
    assert job.days_until_deadline == days
    assert job.accepts_applications is (not expired)


def test_a_closed_job_never_accepts_even_before_its_deadline():
    from app.models.job import Job

    job = Job(application_deadline=today() + timedelta(days=30), status="closed")
    assert job.is_expired is False
    assert job.accepts_applications is False
