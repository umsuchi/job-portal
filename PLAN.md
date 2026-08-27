# Job Portal — Build Plan

Derived from `job-portal-spec.md` v1.0. Build order follows spec §17.
Status legend: `[ ]` todo · `[~]` in progress · `[x]` done

**Status: all phases complete.** Backend, frontend and 50 tests are in the repo;
the migration has been applied to a Postgres 16 instance and the full flow
verified end to end. See `README.md` for how to run it and the note at the
bottom of this file for the one step still outstanding.

**Stack:** FastAPI (async SQLAlchemy 2.0 + Alembic) · React 18 + Vite + TS + Tailwind · Neon Postgres · Groq `openai/gpt-oss-20b`

---

## Phase 0 — Foundation

- [x] **F-1** Backend skeleton: `app/main.py`, CORS, `/health`, Swagger at `/docs`
- [x] **F-2** `core/config.py` — pydantic-settings reading spec §13 env vars; normalize Neon URL for asyncpg
- [x] **F-3** `db/session.py` — async engine + `AsyncSession` dependency; `db/base.py` declarative base
- [x] **F-4** `core/security.py` — bcrypt hash/verify (direct, not passlib) + JWT sign/decode
- [x] **F-5** Alembic wired to the async engine; `.env.example`, `.gitignore`, `requirements.txt`

---

## EP-1 — Authentication & Account Management

| Story | Task | Acceptance |
|---|---|---|
| US-1.1 | **1.1a** `users` table (uuid pk, unique email, password_hash, role, created_at) | Email unique at DB level |
| US-1.1 | **1.1b** `candidate_profiles` / `recruiter_profiles`, 1:1 on user_id | Role-appropriate profile row created at register |
| US-1.1 | **1.1c** `POST /auth/register` | bcrypt hash before insert; `role` required; 409 on duplicate email |
| US-1.2 | **1.2a** `POST /auth/login` | Access token 30 min, refresh token 7 days; generic error on bad creds |
| US-1.3 | **1.3a** `POST /auth/refresh` | Rejects access tokens used as refresh (token `typ` claim) |
| US-1.4 | **1.4a** `GET /auth/me` | Returns user + the profile matching their role |
| US-1.4 | **1.4b** `PUT /auth/me` | Candidate: full_name, headline, skills[], resume_url · Recruiter: company_name, company_website |
| FR-2/3 | **1.5** `api/deps.py` — `current_user`, `require_candidate`, `require_recruiter` | 401 vs 403 distinguished |

**Definition of done:** register → login → `/auth/me` → update profile works end to end in Swagger.

---

## EP-2 — Recruiter: Job Posting

| Story | Task | Acceptance |
|---|---|---|
| US-2.1 | **2.1a** `jobs` table; `required_skills TEXT[]` + GIN index | title, description, required_skills, location, job_type required; salary optional |
| US-2.1 | **2.1b** `POST /jobs` (recruiter only) | 403 for candidates |
| US-2.2 | **2.2a** `PUT /jobs/{id}` owner-guarded | 403 if not owner (FR-4) |
| US-2.2 | **2.2b** `DELETE /jobs/{id}` → sets `status='closed'` | Closed jobs reject new applications |
| US-3.1 | **2.3a** `GET /jobs` — keyword, skill, location, job_type filters + pagination | Public; only `open` jobs by default |
| US-3.1 | **2.3b** `GET /jobs/{id}` | Public; includes recruiter company name |
| US-2.3 | **2.4a** `GET /jobs/{id}/applications` | Owner only; candidate name, skills, cover note, date, status |
| US-2.4 | **2.4b** `PATCH /applications/{id}/status` | Enum enforced server-side + legal transitions only (§11.2) |

**Definition of done:** recruiter posts, edits, closes a job; a second recruiter is refused on both.

---

## EP-3 — Candidate: Discovery & Application

| Story | Task | Acceptance |
|---|---|---|
| US-3.2 | **3.1a** `applications` table, unique `(job_id, candidate_id)` | FR-5: second apply → 409 |
| US-3.2 | **3.1b** `POST /applications` (candidate only) | 400 if job closed or missing |
| US-3.3 | **3.2a** `GET /applications/me` | Sorted by `applied_at DESC`, joined with job title/company |
| US-3.4 | **3.3a** `DELETE /applications/{id}` → `withdrawn` | Blocked once status is `hired` or `rejected` |

**Definition of done:** apply, see it listed, withdraw; duplicate apply rejected.

---

## EP-4 — Messaging

| Story | Task | Acceptance |
|---|---|---|
| US-4.1 | **4.1a** `messages` table scoped to `application_id` | sender/receiver ids, `sent_at`, nullable `read_at` |
| US-4.1/4.2 | **4.1b** `POST /applications/{id}/messages` | Receiver derived server-side (the other party); 403 for anyone else (FR-7) |
| US-4.2 | **4.2a** `GET /applications/{id}/messages` | Two parties only; marks the caller's inbound messages read |
| US-4.3 | **4.3a** `GET /messages/unread-count` | Cheap endpoint for 20s frontend polling |

**Definition of done:** a third user gets 403 on both endpoints of someone else's thread.

---

## EP-5 — AI Job Suggestions

| Story | Task | Acceptance |
|---|---|---|
| — | **5.1a** `services/matcher.py` — SQL shortlist via `required_skills && :skills`, ranked by overlap, top 10 | Deterministic, no API call |
| US-5.2 | **5.1b** `services/ai_suggestions.py` — one Groq call, strict JSON out | System prompt per spec §12; ~8s timeout |
| FR-9 | **5.1c** Fallback to raw SQL ranking on error/timeout/bad JSON | Never surfaces an error to the UI |
| FR-10 / US-5.3 | **5.2a** `suggestion_caches` table keyed by candidate + skills hash, 1h TTL | Skills change → hash changes → auto-invalidated |
| US-5.1 | **5.3a** `GET /suggestions` | Up to 10 jobs, each with rank + one-line reason + `source: ai\|fallback` |

**Definition of done:** works with a valid key; still returns ranked jobs with the key removed.

---

## Phase 6 — Frontend

- [x] **FE-1** Vite + React 18 + TS + Tailwind; shadcn-style primitives (Button, Input, Textarea, Card, Badge, Select, Dialog, Spinner, EmptyState)
- [x] **FE-2** `api/client.ts` — axios + auto refresh-on-401 interceptor; `context/AuthContext`; React Query provider; protected + role-gated routes
- [x] **FE-3** Login · Register (role picker) · Profile
- [x] **FE-4** Jobs list with filter bar · Job detail with Apply dialog
- [x] **FE-5** Recruiter: My Jobs · Post/Edit Job · Applicants with status control
- [x] **FE-6** Candidate: My Applications with withdraw
- [x] **FE-7** Messages thread (polled) + unread badge in nav
- [x] **FE-8** Candidate dashboard: "Recommended for you" cards with AI reason
- [x] **FE-9** Loading skeletons, empty states, error toasts, responsive layout
- [x] **FE-10** `vercel.json` SPA rewrite + `.env.example`

---

## Phase 7 — Verification

- [x] **V-1** Pytest: auth happy path + duplicate email
- [x] **V-2** Pytest: job ownership (FR-4), role gates (FR-3)
- [x] **V-3** Pytest: duplicate apply 409 (FR-5), illegal status transition rejected (FR-6)
- [x] **V-4** Pytest: third-party message access 403 (FR-7)
- [x] **V-5** Pytest: suggestions fall back cleanly with Groq disabled (FR-9)
- [x] **V-6** Manual smoke: register both roles → post job → apply → message → status → suggestions
- [x] **V-7** README with local setup + deploy steps (spec §14/§15)

---

## Out of scope (spec §8)

Admin role · email verification / password reset · resume upload & parsing · WebSocket chat · billing · notifications · embedding-based matching.

---

## Outstanding

- [ ] **Run `alembic upgrade head` against Neon.** The migration is written and
  verified against Postgres 16, but this build environment's network policy
  blocks outbound connections to `neon.tech` (both direct Postgres on 5432 and
  the HTTPS SQL endpoint), so it could not be applied to the live database from
  here. One command from your machine finishes it.
- [ ] **Confirm the Groq path end to end.** `api.groq.com` is blocked from here
  too, so the AI branch was verified with mocked responses and the fallback
  branch was verified for real. With a working key the dashboard badge should
  read "AI-ranked" instead of "Skill-match ranking".
- [x] ~~Delete the stray `backend/.venv`~~ — replaced by a working Python 3.13
  virtualenv.

## Fixed after first run

- [x] **TLS to Neon failed on macOS + Python 3.13.** asyncpg was asked for
  `ssl=True`, which defers to the OS trust store; a python.org build has none
  wired up, so the handshake died with `CERTIFICATE_VERIFY_FAILED`. The context
  is now built from certifi's CA bundle in `app/db/connection.py`, shared by the
  app engine and Alembic.
- [x] **Every endpoint returned 422 instead of the real error.** `main.py` had a
  catch-all `@app.exception_handler(ValueError)`, and
  `ssl.SSLCertVerificationError` subclasses `ValueError` — so the failed database
  connection above was reported as a validation error on `/jobs` and
  `/auth/register` alike, with the traceback swallowed. Handler removed;
  infrastructure failures now surface as 500s. Verified with a test that points
  the app at a dead database and asserts 500.

## Added after handover

- [x] **Seed script** — `backend/scripts/seed.py` + `data.py`. 15 recruiters, 15
  candidates, 15 jobs, plus 21 applications covering every status and 4 message
  threads. Idempotent; `--reset` removes only seeded accounts.
- [x] **Skill catalogue and autocomplete** — `frontend/src/lib/skills.ts`, 263
  skills across 10 categories with aliases, drawn from the 2025 Stack Overflow
  Developer Survey technology tables plus standard UI/UX and engineering-practice
  vocabulary. `SkillInput` and `SkillFilterInput` are keyboard-navigable
  comboboxes; free-text entry still works.
- [x] **8 seed tests** — structure, uniqueness, status coverage, and a
  cross-language check that seed skills match the catalogue's spellings exactly.
  58 tests total.
