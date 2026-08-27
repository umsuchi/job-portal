"""Populate the database with demo content.

    python -m scripts.seed              # add anything missing, leave the rest alone
    python -m scripts.seed --reset      # delete previously seeded accounts first

Creates 15 recruiters, 15 candidates and 15 job posts, plus applications spread
across the status lifecycle and a few message threads, so every page in the app
has something on it.

Safe to re-run: accounts are matched on email and skipped if they already exist.
``--reset`` only removes the accounts this script created — the cascade from
``users`` takes their jobs, applications and messages with them — so anything you
created by hand while clicking around survives.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

# Allow `python scripts/seed.py` as well as `python -m scripts.seed`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, func, select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal, engine  # noqa: E402
from app.models.application import Application  # noqa: E402
from app.models.job import Job  # noqa: E402
from app.models.message import Message  # noqa: E402
from app.models.user import (  # noqa: E402
    ROLE_CANDIDATE,
    ROLE_RECRUITER,
    CandidateProfile,
    RecruiterProfile,
    User,
)
from scripts import data  # noqa: E402

NOW = datetime.now(timezone.utc)


def ago(days: float) -> datetime:
    return NOW - timedelta(days=days)


def deadline_for(index: int) -> date | None:
    """Turn the seed's relative offsets into real dates at run time."""
    offset = data.JOB_DEADLINE_DAYS.get(index)
    return None if offset is None else (NOW + timedelta(days=offset)).date()


async def seeded_emails(db: AsyncSession) -> Dict[str, User]:
    """The seed accounts that already exist, keyed by email."""
    emails = [r["email"] for r in data.RECRUITERS] + [c["email"] for c in data.CANDIDATES]
    rows = await db.execute(select(User).where(User.email.in_(emails)))
    return {user.email: user for user in rows.scalars().all()}


async def reset(db: AsyncSession) -> int:
    """Delete the seed accounts. Everything they own cascades away with them."""
    emails = [r["email"] for r in data.RECRUITERS] + [c["email"] for c in data.CANDIDATES]
    existing = await db.scalar(
        select(func.count(User.id)).where(User.email.in_(emails))
    )
    await db.execute(delete(User).where(User.email.in_(emails)))
    await db.commit()
    return existing or 0


async def seed(db: AsyncSession) -> None:
    password_hash = hash_password(data.SEED_PASSWORD)
    existing = await seeded_emails(db)

    # ---------------------------------------------------------------- people
    recruiters: List[User] = []
    created_recruiters = 0
    for spec in data.RECRUITERS:
        user = existing.get(spec["email"])
        if user is None:
            user = User(email=spec["email"], password_hash=password_hash,
                        role=ROLE_RECRUITER, created_at=ago(90))
            db.add(user)
            await db.flush()
            db.add(RecruiterProfile(
                user_id=user.id,
                **{k: v for k, v in spec.items() if k != "email"},
            ))
            created_recruiters += 1
        recruiters.append(user)

    candidates: List[User] = []
    created_candidates = 0
    for index, spec in enumerate(data.CANDIDATES):
        user = existing.get(spec["email"])
        if user is None:
            user = User(email=spec["email"], password_hash=password_hash,
                        role=ROLE_CANDIDATE, created_at=ago(80 - index))
            db.add(user)
            await db.flush()
            db.add(CandidateProfile(
                user_id=user.id,
                **{k: v for k, v in spec.items() if k != "email"},
            ))
            created_candidates += 1
        candidates.append(user)

    await db.commit()

    # ------------------------------------------------------------------ jobs
    jobs: List[Job] = []
    created_jobs = 0
    for index, spec in enumerate(data.JOBS):
        recruiter = recruiters[spec["recruiter"]]
        job = await db.scalar(
            select(Job).where(Job.recruiter_id == recruiter.id, Job.title == spec["title"])
        )
        if job is None:
            job = Job(
                recruiter_id=recruiter.id,
                # Every key but the recruiter pointer maps straight onto a column.
                **{k: v for k, v in spec.items() if k != "recruiter"},
                application_deadline=deadline_for(index),
                # Staggered so the "newest first" browse order looks real.
                created_at=ago(30 - index * 1.5),
            )
            db.add(job)
            created_jobs += 1
        jobs.append(job)
    await db.commit()
    for job in jobs:
        await db.refresh(job)

    # ---------------------------------------------------------- applications
    applications: List[Application] = []
    created_applications = 0
    for index, (cand_i, job_i, status, note) in enumerate(data.APPLICATIONS):
        candidate, job = candidates[cand_i], jobs[job_i]
        application = await db.scalar(
            select(Application).where(
                Application.candidate_id == candidate.id, Application.job_id == job.id
            )
        )
        if application is None:
            application = Application(
                job_id=job.id,
                candidate_id=candidate.id,
                cover_note=note,
                status=status,
                applied_at=ago(20 - index * 0.7),
            )
            db.add(application)
            created_applications += 1
        applications.append(application)
    await db.commit()
    for application in applications:
        await db.refresh(application)

    # --------------------------------------------------------------- threads
    created_messages = 0
    for app_index, turns in data.THREADS:
        application = applications[app_index]
        already = await db.scalar(
            select(func.count(Message.id)).where(Message.application_id == application.id)
        )
        if already:
            continue
        job = jobs[data.APPLICATIONS[app_index][1]]
        for turn, (sender_role, body) in enumerate(turns):
            if sender_role == "candidate":
                sender_id, receiver_id = application.candidate_id, job.recruiter_id
            else:
                sender_id, receiver_id = job.recruiter_id, application.candidate_id
            db.add(Message(
                application_id=application.id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                body=body,
                sent_at=ago(5 - turn * 0.3),
                # The last message in each thread stays unread, so the badge shows.
                read_at=None if turn == len(turns) - 1 else ago(4.5 - turn * 0.3),
            ))
            created_messages += 1
    await db.commit()

    # ---------------------------------------------------------------- report
    def line(label: str, created: int, total: int) -> str:
        suffix = "" if created == total else f" ({total - created} already present)"
        return f"  {label:<14} {created} created{suffix}"

    print("Seeded:")
    print(line("recruiters", created_recruiters, len(recruiters)))
    print(line("candidates", created_candidates, len(candidates)))
    print(line("jobs", created_jobs, len(jobs)))
    print(line("applications", created_applications, len(applications)))
    print(f"  {'messages':<14} {created_messages} created")

    live = sum(1 for j in jobs if j.accepts_applications)
    soon = sum(1 for j in jobs
               if j.days_until_deadline is not None and 0 <= j.days_until_deadline <= 7)
    expired = sum(1 for j in jobs if j.is_expired)
    print(f"  {'':<14} of those jobs: {live} accepting, {soon} closing within a "
          f"week, {expired} expired")
    print()
    print(f"Every seeded account uses the password: {data.SEED_PASSWORD}")
    print(f"  recruiter: {data.RECRUITERS[0]['email']}")
    print(f"  candidate: {data.CANDIDATES[0]['email']}")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true",
                        help="delete previously seeded accounts before seeding")
    args = parser.parse_args()

    async with AsyncSessionLocal() as db:
        if args.reset:
            removed = await reset(db)
            print(f"Removed {removed} previously seeded account(s).\n")
        await seed(db)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
