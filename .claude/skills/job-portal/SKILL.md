---
name: job-portal
description: Conventions and architecture for this job-portal codebase (FastAPI + React + Neon Postgres + Groq). Use when adding or changing endpoints, models, migrations, React pages, or the AI suggestion engine in this repo.
---

# Job Portal — project conventions

One FastAPI monolith, one React SPA, one Postgres database, one external AI call.
The guiding principle from the spec is **simple > clever**: no microservices, no
queue, no vector DB, no agent framework. Before adding infrastructure, check
whether Postgres already does the job.

Source of truth for requirements: `job-portal-spec.md`. Build status per story:
`PLAN.md` — tick boxes there when a story lands.

## Layout

```
backend/app/
  core/       config.py (pydantic-settings), security.py (bcrypt + JWT)
  db/         base.py (DeclarativeBase, column helpers), session.py (async engine)
  models/     SQLAlchemy models — one file per aggregate
  schemas/    Pydantic request/response — one file per router
  api/        deps.py (auth + role gates) then one router per epic
  services/   matcher.py (SQL shortlist), ai_suggestions.py (Groq + fallback)
```

## Backend rules

- **Every endpoint carries its story id in the docstring** (`US-3.2`, `FR-5`) so
  the code traces back to the spec.
- **Authorization lives in dependencies, not handlers.** Use `get_current_user`,
  `require_candidate`, `require_recruiter` from `api/deps.py`. Ownership checks
  that need a row go in a small `_owned_job` / `load_application_for_party`
  helper — never inline in each handler, so the rule has one implementation.
- **Never trust a client-supplied identity field.** The message receiver is
  derived server-side from the application's two parties; a `receiver_id` in a
  request body would be a bug.
- **Status transitions are validated against `RECRUITER_TRANSITIONS`** in
  `models/application.py`, which mirrors the state machine in spec §11.2. Add new
  states there, not in the router.
- **Enums are `String` + a `CheckConstraint`**, not native Postgres enum types —
  they migrate without an `ALTER TYPE` dance. Keep the Python tuple and the
  constraint in sync.
- **404 over 403 when acknowledging existence leaks information.** A candidate
  probing someone else's application gets 404; a recruiter touching another
  recruiter's job gets 403 (they already know it exists — it's public).
- Async everywhere. `await db.scalar(select(...))`, never sync sessions.

## Database rules

- `timestamptz` for every timestamp (`DateTime(timezone=True)`).
- Index every foreign key — Postgres does not do it for you, and `ON DELETE
  CASCADE` scans without one.
- **Partial indexes where the query always filters the same way**:
  `ix_jobs_open_created_at` covers only `status = 'open'`;
  `ix_messages_receiver_unread` covers only `read_at IS NULL`.
- `required_skills` and `skills` are `TEXT[]` with a **GIN index**. Skill matching
  uses the overlap operator (`Job.required_skills.overlap(...)`), never a join
  table. Array overlap is case-sensitive, so probe with both the original and
  normalized casing and do exact ranking in Python.
- Neon's pooled endpoint runs PgBouncer in transaction mode: keep
  `statement_cache_size=0` in `connect_args`, or asyncpg's prepared statements
  break across checkouts.
- Migrations: `alembic revision --autogenerate -m "..."`, then **read the
  generated file** — autogenerate misses partial-index predicates and check
  constraints often enough to matter.

## AI suggestion rules

- **The SQL shortlist is the source of truth.** The model reorders and explains;
  it cannot introduce a job. Drop unknown job ids, backfill omitted ones.
- **`ai_suggestions` never raises for an AI problem.** Every failure path returns
  the SQL ranking with `source="fallback"`. If you add a code path that can raise
  out of that module, it is a bug (FR-9).
- **One Groq call per regeneration, never per page load.** The cache key is
  candidate id + `skills_hash`, so a profile edit invalidates it implicitly.
  Don't add explicit cache-busting where a hash change would do.
- The frontend never calls Groq (FR-8). The key stays server-side.

## Frontend rules

- **Server state is React Query; only form drafts are `useState`.** No manual
  loading booleans around fetches.
- Query keys: `['jobs', filters]`, `['job', id]`, `['my-applications']`,
  `['applicants', jobId]`, `['thread', id]`, `['suggestions']`, `['unread']`.
  Invalidate the ones a mutation actually affects.
- **Auth token handling lives entirely in `api/client.ts`** — request interceptor
  attaches the bearer, response interceptor refreshes once on 401 and coalesces
  parallel refreshes onto one call. Pages never touch `localStorage`.
- Use `errorMessage(err)` for every caught error; it unwraps FastAPI's `detail`
  including the array form from Pydantic validation.
- UI primitives come from `components/ui/index.tsx`. Extend that file rather than
  hand-rolling a one-off button.
- Ternaries, not `&&`, for conditional JSX (`0 &&` renders a stray zero).
- Never define a component inside another component.
- The UI only offers status transitions the API will accept — `NEXT_STATES` in
  `pages/Applicants.tsx` mirrors the backend state machine. Change both together.

## The skill catalogue

`frontend/src/lib/skills.ts` is the single source of skill spellings. It exists
because Postgres array overlap is an **exact** match: "postgres" typed by a
candidate and "PostgreSQL" typed by a recruiter never meet, and the candidate's
dashboard silently comes up empty.

- Every skill field goes through `SkillInput` (multi) or `SkillFilterInput`
  (single) from `components/SkillInput.tsx`. Never wire a bare `<Input>` to a
  skill field.
- `canonicalize()` maps an alias or casing variant onto the catalogue spelling on
  the way in. Unknown skills pass through untouched — the catalogue is a
  convenience, not a whitelist (spec §18 keeps skills free-text).
- Adding a skill: append an `s('Name', 'Category', ...aliases)` row. Aliases are
  what people actually type, lowercase. Nothing derives from the list, so this is
  always safe.
- `scripts/data.py` must use catalogue spellings.
  `tests/test_seed_data.py::test_seed_skills_use_catalogue_spellings` parses the
  `.ts` file and fails if they drift. If you rename a catalogue entry, that test
  tells you what to update.

## Seed data

`python -m scripts.seed` (`--reset` to start over) — 15 recruiters, 15
candidates, 15 jobs, 21 applications, 4 threads. Password `password123`.

- Idempotent by email, so re-running is safe and never duplicates.
- `--reset` deletes only seeded accounts; the `ON DELETE CASCADE` from `users`
  takes their jobs, applications and messages. Hand-created data survives.
- The seed deliberately covers every application status and leaves the last
  message of each thread unread, so the status controls and the unread badge are
  both visible without clicking anything first.
- If you add a candidate, keep at least one skill overlapping a seeded job —
  `test_every_candidate_matches_at_least_one_job` enforces it, because an empty
  dashboard reads as a broken feature.

## Adding a feature — the order that works

1. Model + migration, run `alembic upgrade head` against a scratch database.
2. Pydantic schemas.
3. Router, with the story id in the docstring and the role gate in the signature.
4. A test per acceptance criterion, including the refusal cases.
5. `endpoints.ts` + types, then the page.
6. Tick the box in `PLAN.md`.

## Gotchas already hit

- `pydantic-settings` JSON-decodes `List[str]` fields straight from `.env`, so a
  comma-separated `CORS_ORIGINS` crashes at import. Read it as `str` and split in
  a property.
- Don't `import app.models` into a module that also holds the FastAPI object
  named `app` — the package shadows it.
- bcrypt silently truncates past 72 bytes; `hash_password` raises instead.
- **Never register a broad `@app.exception_handler(ValueError)`.** `ssl.SSLCert\
  VerificationError` subclasses `ValueError` (via `OSError`), so such a handler
  turns a dead database connection into a 422 "validation error" on every
  endpoint and hides the real traceback. Pydantic already returns 422 for
  request validation; let everything else surface as a 500.
- **Build the TLS context from certifi, not `ssl=True`.** `ssl=True` defers to
  the OS trust store, and a python.org build on macOS ships without one wired
  up — every connection fails with `CERTIFICATE_VERIFY_FAILED`. See
  `app/db/connection.py`, which both the app engine and Alembic use.
