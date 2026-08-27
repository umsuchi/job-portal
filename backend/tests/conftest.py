"""Test fixtures.

Each test gets a fresh schema on the configured database so ordering never
matters. Point TEST_DATABASE_URL (or DATABASE_URL) at a throwaway Postgres —
never a database with real data.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("ENV", "test")

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
import app.models  # noqa: F401,E402  (registers tables before app import)
from app.main import app as fastapi_app  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    connect_args = {"ssl": True, "statement_cache_size": 0} if settings.requires_ssl else {}
    engine = create_async_engine(settings.async_database_url, connect_args=connect_args)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine):
    return async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        async with session_factory() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    fastapi_app.dependency_overrides.clear()


# ------------------------------------------------------------------ helpers

def unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


class Actor:
    """A registered user plus a ready-to-use auth header."""

    def __init__(self, client: AsyncClient, user: dict, token: str):
        self._client = client
        self.user = user
        self.id = user["id"]
        self.email = user["email"]
        self.headers = {"Authorization": f"Bearer {token}"}

    async def get(self, url, **kw):
        return await self._client.get(url, headers=self.headers, **kw)

    async def post(self, url, **kw):
        return await self._client.post(url, headers=self.headers, **kw)

    async def put(self, url, **kw):
        return await self._client.put(url, headers=self.headers, **kw)

    async def patch(self, url, **kw):
        return await self._client.patch(url, headers=self.headers, **kw)

    async def delete(self, url, **kw):
        return await self._client.delete(url, headers=self.headers, **kw)


async def make_actor(client: AsyncClient, role: str, **profile) -> Actor:
    email = unique_email(role)
    password = "correct-horse-battery"
    body = {"email": email, "password": password, "role": role, **profile}
    reg = await client.post("/auth/register", json=body)
    assert reg.status_code == 201, reg.text
    login = await client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return Actor(client, reg.json(), login.json()["access_token"])


@pytest_asyncio.fixture
async def candidate(client) -> Actor:
    actor = await make_actor(client, "candidate", full_name="Casey Candidate")
    await actor.put("/auth/me", json={"skills": ["React", "Node.js", "PostgreSQL"]})
    return actor


@pytest_asyncio.fixture
async def recruiter(client) -> Actor:
    return await make_actor(client, "recruiter", company_name="Acme Corp")


@pytest_asyncio.fixture
async def other_recruiter(client) -> Actor:
    return await make_actor(client, "recruiter", company_name="Rival Inc")


JOB_BODY = {
    "title": "Senior React Engineer",
    "description": "Build and ship our customer-facing web application.",
    "required_skills": ["React", "TypeScript", "Node.js"],
    "location": "Remote",
    "job_type": "remote",
    "salary_min": 90000,
    "salary_max": 140000,
}


@pytest_asyncio.fixture
async def job(recruiter) -> dict:
    resp = await recruiter.post("/jobs", json=JOB_BODY)
    assert resp.status_code == 201, resp.text
    return resp.json()
