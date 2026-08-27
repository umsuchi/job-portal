# Job Portal

Recruiters post jobs, candidates browse and apply, both sides message on an
application, and candidates get an AI-ranked "Recommended for you" list.

Built to [`job-portal-spec.md`](./job-portal-spec.md) v1.0 — the build plan and
story-by-story status live in [`PLAN.md`](./PLAN.md).

**Stack:** FastAPI (async SQLAlchemy 2.0 + Alembic) · React 18 + Vite + TypeScript + Tailwind ·
PostgreSQL (Neon) · Groq `openai/gpt-oss-120b`

---

## What's here

```
job-portal/
├── backend/          FastAPI monolith — auth, jobs, applications, messages, suggestions
│   └── scripts/      seed.py + data.py — demo content
├── frontend/         React SPA — 11 pages, shadcn-style component set
│   └── src/lib/skills.ts   263-skill catalogue behind the autocomplete
├── job-portal-spec.md
├── PLAN.md           epic/story breakdown with build status
└── .claude/skills/   project conventions, picked up automatically by Claude Code
```

## Quick start

### 1. Database

Create a free project at [neon.tech](https://neon.tech) and copy the **pooled**
connection string (the host with `-pooler` in it).

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # then fill in DATABASE_URL, JWT_SECRET_KEY, GROQ_API_KEY
alembic upgrade head        # creates every table, the GIN index and the partial indexes
uvicorn app.main:app --reload --port 8000
```

Swagger UI: <http://localhost:8000/docs>

> The pasted Neon URL is normalized for asyncpg at startup — `sslmode` and
> `channel_binding` query args are stripped and TLS is requested through
> `connect_args` instead, so you can paste the connection string exactly as Neon
> gives it to you. The TLS context is built from certifi's CA bundle
> (`app/db/connection.py`) rather than the OS trust store, which a python.org
> Python on macOS does not have wired up — otherwise every connection fails with
> `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

App: <http://localhost:5173>

### 4. Demo data (optional)

```bash
cd backend
python -m scripts.seed            # 15 recruiters, 15 candidates, 15 jobs
python -m scripts.seed --reset    # wipe the seeded accounts first, then re-seed
```

Also creates 21 applications spread across every status and four message threads,
so the applicants list, the status controls, the unread badge and the AI
recommendations all have something to show.

Every seeded account uses the password **`password123`**. Two to start with:

| Role | Email |
|---|---|
| Recruiter | `hiring@northwindlabs.example.com` |
| Candidate | `arif.rahman@example.com` |

Re-running is safe — accounts are matched on email and skipped if they exist.
`--reset` removes only the seeded accounts (their jobs, applications and messages
cascade away with them), so anything you created by hand survives.

## Skill catalogue

`frontend/src/lib/skills.ts` holds 263 skills across ten categories — languages,
frontend, backend, mobile, databases, cloud/DevOps, data & AI, testing, UI/UX
design, and engineering practices — with aliases for the spellings people
actually type (`postgres`, `k8s`, `a11y`, `ts`). Typing in any skill field shows a
ranked dropdown: arrow keys move, Enter or click selects, Escape closes.

Skills remain free-text at the API (spec §18) — anything not in the list is still
accepted. What the catalogue buys is *agreement*: picking "PostgreSQL" from the
list rather than typing "postgres" is what makes the Postgres array-overlap match
in the suggestion engine fire, since that operator is exact. `canonicalize()` maps
a typed alias onto the catalogue spelling on the way in.

The seed data uses these same spellings, and a test asserts it stays that way.

## Tests

```bash
cd backend
pytest                   # 58 tests
```

Tests run against the database in `DATABASE_URL` and **drop and recreate every
table** on each test. Point them at a throwaway database, never at one holding
real data:

```bash
DATABASE_URL='postgresql://…/job-portal-test' pytest
```

What they cover: password hashing and token type separation, role gates (FR-3),
job ownership (FR-4), the duplicate-application constraint (FR-5), every edge of
the status lifecycle (FR-6), third-party lockout on message threads (FR-7), the
suggestion engine's cache, invalidation and fallback behaviour (FR-9, FR-10), and
the structure of the seed data — including a cross-check that every seed skill is
spelled the way the frontend catalogue spells it.

## How the AI suggestions work

Two stages, one external call — no vector DB, no agent framework (spec §12):

1. **SQL shortlist.** `jobs.required_skills && :candidate_skills` against the GIN
   index picks the open jobs sharing at least one skill, ranked by overlap count
   and then by the share of the job's requirements met. Top 10.
2. **One Groq call.** The candidate's skills plus those 10 jobs go into a single
   prompt; the model returns strict JSON with a rank and a one-sentence reason
   per job.

The shortlist is the source of truth for *which* jobs exist — the model can only
reorder and explain them. Hallucinated job ids are dropped, and any shortlisted
job the model skipped is appended with a generated reason.

**It never breaks the dashboard.** No API key, a timeout, an HTTP error or
unparseable JSON all fall through to the SQL ranking with generated reasons, and
the response says which path ran (`source: "ai" | "fallback"`).

**It calls Groq at most once per hour per candidate.** Results are cached in
`suggestion_caches`, keyed by candidate id plus a hash of their skill list — so
editing your skills invalidates the cache for free, with no explicit delete.

## API

Full interactive reference at `/docs`. Summary:

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register` · `POST /auth/login` · `POST /auth/refresh` · `GET|PUT /auth/me` |
| Jobs | `GET /jobs` · `GET /jobs/{id}` · `POST /jobs` · `PUT /jobs/{id}` · `DELETE /jobs/{id}` · `GET /jobs/{id}/applications` |
| Applications | `POST /applications` · `GET /applications/me` · `GET /applications/{id}` · `PATCH /applications/{id}/status` · `DELETE /applications/{id}` |
| Messages | `GET|POST /applications/{id}/messages` · `GET /messages/unread-count` |
| Suggestions | `GET /suggestions` |

## Deploying

### Render (backend)

- Root directory `backend/`, runtime Python 3
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` — must use `$PORT`
- Add every variable from `.env.example`; set `ENV=production` and
  `CORS_ORIGINS` to your Vercel URL
- Run `alembic upgrade head` once from the Shell tab

Free tier sleeps after 15 minutes idle; the next request takes 30–60s to wake it.

### Vercel (frontend)

- Root directory `frontend/`, preset auto-detects Vite
- Build `npm run build`, output `dist`
- Set `VITE_API_BASE_URL` to the Render URL
- `vercel.json` already rewrites all routes to `index.html` so deep links survive a refresh

Then update `CORS_ORIGINS` on Render to include the real Vercel URL and redeploy.

## Not in this version

Per spec §8: admin role, email verification and password reset, resume upload and
parsing, WebSocket chat (polling every 15–30s stands in), billing, notifications,
and embedding-based skill matching.
