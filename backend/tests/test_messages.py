"""EP-4 — thread access control (FR-7), read receipts, unread counts."""
import pytest_asyncio

from tests.conftest import make_actor


@pytest_asyncio.fixture
async def application(candidate, job):
    resp = await candidate.post("/applications", json={"job_id": job["id"]})
    return resp.json()


async def test_both_parties_can_talk(candidate, recruiter, application):
    app_id = application["id"]

    sent = await candidate.post(f"/applications/{app_id}/messages",
                                json={"body": "Is this role remote-friendly?"})
    assert sent.status_code == 201
    # The receiver is derived server-side, never supplied by the client.
    assert sent.json()["receiver_id"] == recruiter.id
    assert sent.json()["is_mine"] is True

    reply = await recruiter.post(f"/applications/{app_id}/messages",
                                 json={"body": "Fully remote within the EU."})
    assert reply.status_code == 201
    assert reply.json()["receiver_id"] == candidate.id

    thread = await candidate.get(f"/applications/{app_id}/messages")
    body = thread.json()
    assert body["job_title"] == "Senior React Engineer"
    assert body["counterpart_name"] == "Acme Corp"
    assert [m["body"] for m in body["messages"]] == [
        "Is this role remote-friendly?", "Fully remote within the EU."
    ]


async def test_third_party_is_locked_out(client, candidate, application, other_recruiter):
    app_id = application["id"]
    intruder = await make_actor(client, "candidate", full_name="Nosy")

    assert (await intruder.get(f"/applications/{app_id}/messages")).status_code == 403
    assert (await intruder.post(f"/applications/{app_id}/messages",
                                json={"body": "hi"})).status_code == 403
    assert (await other_recruiter.get(f"/applications/{app_id}/messages")).status_code == 403


async def test_anonymous_is_locked_out(client, application):
    assert (await client.get(f"/applications/{application['id']}/messages")).status_code == 401


async def test_unread_count_and_read_receipts(candidate, recruiter, application):
    app_id = application["id"]
    await recruiter.post(f"/applications/{app_id}/messages", json={"body": "Are you available?"})

    assert (await candidate.get("/messages/unread-count")).json()["unread"] == 1
    # The sender's own message never counts against them.
    assert (await recruiter.get("/messages/unread-count")).json()["unread"] == 0

    # Reading the thread marks the caller's inbound messages read.
    await candidate.get(f"/applications/{app_id}/messages")
    assert (await candidate.get("/messages/unread-count")).json()["unread"] == 0

    mine = await candidate.get("/applications/me")
    assert mine.json()[0]["unread_messages"] == 0


async def test_unread_surfaces_on_the_applicants_list(candidate, recruiter, application, job):
    await candidate.post(f"/applications/{application['id']}/messages", json={"body": "Ping"})
    applicants = await recruiter.get(f"/jobs/{job['id']}/applications")
    assert applicants.json()[0]["unread_messages"] == 1


async def test_empty_message_rejected(candidate, application):
    resp = await candidate.post(f"/applications/{application['id']}/messages", json={"body": "   "})
    assert resp.status_code == 422
