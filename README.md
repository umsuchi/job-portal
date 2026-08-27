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

Every seeded record is fully populated: jobs carry responsibilities, requirements,
benefits, nice-to-have skills, seniority and work mode; candidates carry a bio,
years of experience, preferences and an avatar; companies carry a logo, industry
and description. Avatars come from DiceBear's initials endpoint, so no image files
are checked in. All three work modes and several seniority levels appear, so the
filters and the ranking signals are visible without editing anything.

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
pytest                   # 106 tests
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

`tests/test_matching.py` isolates each ranking signal: two jobs identical on
skills, differing only in the thing under test. If the ranking stopped weighing
work mode, or seniority, or salary, exactly one of those tests would fail.

## What a job post holds

Beyond title, description and skills:

| Field | Why it exists |
|---|---|
| `work_mode` — on-site / hybrid / remote | Separate from employment type, so a full-time remote role can say so |
| `job_type` — full-time / part-time / contract / internship / temporary | How the role is contracted |
| `experience_level` + `min_years_experience` | Ranked against the candidate's own seniority |
| `nice_to_have_skills` | Widens the match without excluding anyone; scored below required skills |
| `responsibilities`, `requirements`, `benefits` | Structured lists rather than one prose blob |
| `salary_min` / `salary_max` / `salary_currency` | Scored against what the candidate wants |
| `application_deadline` | Optional, inclusive — after it the post expires |

### Deadlines and expiry

`application_deadline` is a **date, not a timestamp**, and it is **inclusive** —
applications are accepted all through that day, and the post expires the day
after. A job with no deadline never expires.

The server derives `is_expired`, `days_until_deadline` and `accepts_applications`
and returns them on every job, so no client repeats the date arithmetic and every
client agrees on where the boundary sits. The frontend never recomputes expiry
from the date string, because the viewer's timezone would shift the answer by a
day either side of midnight.

What expiry does:

| | Behaviour |
|---|---|
| Applying | Rejected with a 400 naming the date — enforced in the API, not only the UI |
| Browse | Hidden by default; an "include roles past their deadline" checkbox brings them back |
| Direct link | Always works, showing an Expired badge and a banner — a bookmark never 404s |
| Recruiter's own list | Always visible, badged, and still editable so a deadline can be extended |
| Suggestions | Never recommended, and dropped on rehydration if they expired since caching |
| Existing applications | Untouched — expiry stops new applications, it does not void the ones already in |

A past deadline is rejected when **creating** a post (it would be dead on
arrival) but allowed when **editing** one, otherwise an expired post could never
be corrected or revived.

The UI shows four states: `Closes 15 March` (routine), `Closes in 3 days` (amber,
within a week), `Closes today` (red), and `Expired` (red, card dimmed).

> **Schema note.** The original spec's `job_type` mixed employment type with work
> arrangement — "remote" sat alongside "full_time", so a full-time remote role
> could not describe itself. Work arrangement now lives in `work_mode`. The
> migration rewrites existing `job_type='remote'` rows to
> `full_time` + `work_mode='remote'` before tightening the constraint.

## What a candidate profile holds

Identity (name, headline, bio, avatar, location, resume link) plus the inputs the
ranking scores against: `skills`, `years_experience`, `experience_level`,
`preferred_job_types`, `preferred_work_modes`, `preferred_locations` and
`desired_salary_min`.

All optional. A field left blank simply stops being scored — it never empties the
dashboard. The candidate dashboard nudges toward whichever ones are still unset.

Recruiters get an avatar/logo, plus `about`, `industry` and `headquarters`, which
appear on every job they post.

## How the suggestions work

Two stages, one external call — no vector DB, no agent framework (spec §12):

**1. Deterministic shortlist and scoring.** Postgres narrows the field with the
GIN indexes: a job qualifies if it shares a skill with the candidate on *either*
the required or the nice-to-have list. Each survivor is then scored in Python on
several signals:

| Signal | Weight | Effect |
|---|---:|---|
| Required skill overlap | 10 each | The dominant term |
| Requirement coverage | 6 | A 2-of-3 match beats a 2-of-9 |
| Nice-to-have overlap | 3 each | Widens without dominating |
| Seniority fit | 6 | Full at the same level, less per step away |
| Work arrangement | 5 | Matches a stated preference, or costs half that |
| Location | 4 | Substring both ways; remote always satisfies |
| Employment type | 4 | Against preferred types |
| Salary | 3 | Job's ceiling against the candidate's floor |
| Recency | 1.5 | A nudge, never a decider |

Every signal that fires also produces a short label — "Remote — as you prefer",
"5+ years — you have 6" — which becomes a chip on the dashboard and grounding for
the prompt. A score is never an unexplained number.

Why more than skills: a senior on-site role in Berlin and a junior remote role
overlap identically on skills, but they are not equally good matches for someone
with eight years who only works remotely.

**2. One Groq call.** The candidate's profile — bio, seniority, preferences — and
the shortlisted jobs with their descriptions, modes and salary bands go into a
single prompt. The model returns strict JSON: a rank and a one-sentence reason
per job.

The shortlist is the source of truth for *which* jobs exist — the model can only
reorder and explain them. Hallucinated job ids are dropped, and any shortlisted
job the model skipped is appended with a generated reason.

**It never breaks the dashboard.** No API key, a timeout, an HTTP error or
unparseable JSON all fall through to the SQL ranking with generated reasons, and
the response says which path ran (`source: "ai" | "fallback"`).

**It calls Groq at most once per hour per candidate.** Results are cached in
`suggestion_caches`, keyed by candidate id plus a hash of *every field the ranking
reads* — so editing a location preference invalidates the cache just as a skill
change does, with no explicit delete.

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

Per spec §8: admin role, email verification and password reset, resume and avatar
**file** upload (both are URLs), WebSocket chat (polling every 15–30s stands in),
billing, notifications, and embedding-based skill matching.
