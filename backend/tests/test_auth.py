"""EP-1 — registration, login, refresh, profile."""
import pytest

from app.core.security import create_access_token, hash_password, verify_password
from tests.conftest import make_actor, unique_email


async def test_register_hashes_password_and_creates_profile(client, session_factory):
    from sqlalchemy import select
    from app.models.user import User

    email = unique_email("new")
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": "correct-horse-battery", "role": "candidate",
              "full_name": "Casey"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "candidate"
    assert body["candidate_profile"]["full_name"] == "Casey"
    assert "password" not in body and "password_hash" not in body

    async with session_factory() as db:
        user = await db.scalar(select(User).where(User.email == email))
    assert user.password_hash != "correct-horse-battery"
    assert user.password_hash.startswith("$2")


async def test_duplicate_email_rejected(client):
    email = unique_email("dupe")
    body = {"email": email, "password": "correct-horse-battery", "role": "candidate"}
    assert (await client.post("/auth/register", json=body)).status_code == 201
    assert (await client.post("/auth/register", json=body)).status_code == 409


async def test_login_returns_token_pair_and_rejects_bad_password(client):
    email = unique_email("login")
    await client.post("/auth/register",
                      json={"email": email, "password": "correct-horse-battery", "role": "candidate"})

    ok = await client.post("/auth/login", json={"email": email, "password": "correct-horse-battery"})
    assert ok.status_code == 200
    assert {"access_token", "refresh_token"} <= ok.json().keys()

    bad = await client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert bad.status_code == 401


async def test_refresh_issues_new_access_token(client):
    email = unique_email("refresh")
    await client.post("/auth/register",
                      json={"email": email, "password": "correct-horse-battery", "role": "recruiter"})
    tokens = (await client.post("/auth/login",
                                json={"email": email, "password": "correct-horse-battery"})).json()

    resp = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_access_token_is_not_accepted_as_refresh_token(client):
    """A stolen access token must not be exchangeable for a fresh session."""
    email = unique_email("swap")
    await client.post("/auth/register",
                      json={"email": email, "password": "correct-horse-battery", "role": "recruiter"})
    tokens = (await client.post("/auth/login",
                                json={"email": email, "password": "correct-horse-battery"})).json()

    resp = await client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


async def test_me_requires_auth_and_returns_profile(client, candidate):
    assert (await client.get("/auth/me")).status_code == 401
    resp = await candidate.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["candidate_profile"]["skills"] == ["React", "Node.js", "PostgreSQL"]


async def test_profile_update_is_role_scoped(client, candidate, recruiter):
    resp = await candidate.put("/auth/me", json={"headline": "Frontend dev", "company_name": "Sneaky"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["candidate_profile"]["headline"] == "Frontend dev"
    # A candidate has no recruiter profile to write company_name into.
    assert body["recruiter_profile"] is None

    resp = await recruiter.put("/auth/me", json={"company_website": "https://acme.test"})
    assert resp.json()["recruiter_profile"]["company_website"] == "https://acme.test"


async def test_unknown_user_token_is_rejected(client):
    import uuid
    token = create_access_token(str(uuid.uuid4()))
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_password_hashing_roundtrip():
    h = hash_password("correct-horse-battery")
    assert verify_password("correct-horse-battery", h)
    assert not verify_password("wrong", h)


def test_overlong_password_is_rejected_rather_than_truncated():
    with pytest.raises(ValueError):
        hash_password("x" * 73)
