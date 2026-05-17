# Implementation Plan: AgentTutor — AI Agent Learning Companion (Phase 1)

**Branch**: `001-agent-tutor` | **Date**: 2026-05-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-agent-tutor/spec.md`

## Summary

AgentTutor Phase 1 delivers a Zero-Backend-LLM Course Companion: a deterministic
FastAPI backend serving 10-chapter AI Agent Development content from Cloudflare R2,
grading quizzes by stored answer key, tracking progress and daily streaks in
PostgreSQL, enforcing freemium access control, and exposing keyword search — all
without any LLM inference. A ChatGPT App (OpenAI Apps SDK) acts as the conversational
front end; four SKILL.md files encode the FTE's educational pedagogy.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0 (async), asyncpg, boto3,
  pydantic v2, uvicorn, pytest, pytest-asyncio, httpx
**Storage**: Neon PostgreSQL (async via asyncpg), Cloudflare R2 (S3-compatible, via boto3)
**Testing**: pytest + pytest-asyncio + httpx (async API tests); pytest-cov for coverage
**Target Platform**: Linux server (Fly.io deployment); Docker containerised
**Project Type**: Multi-component web application
  — `backend/` (FastAPI), `skills/` (SKILL.md files), `chatgpt-app/` (manifest),
    `content/` (local dev samples), `docs/` (arch + cost), `tests/` (all tests)
**Performance Goals**: Content retrieval ≤ 2s; quiz grading ≤ 1s; search ≤ 1s at
  1,000 concurrent sessions
**Constraints**:
  - Zero LLM API calls in backend (FR-018, Constitution Principle I — NON-NEGOTIABLE)
  - No `openai` or `anthropic` packages in backend `requirements.txt` or imports
  - Cost ≤ $0.004/user/month at 10K users (Constitution Principle VI)
  - All secrets via `.env`; no hardcoded credentials (Constitution Technical Stack)
**Scale/Scope**: 10 chapters, ~50 quiz questions (5 per chapter), 2 access tiers,
  1K concurrent users Phase 1; horizontally scalable to 100K via stateless API

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Zero-Backend-LLM | No LLM imports, no inference endpoints, no RAG. Verified by: import scan test + API audit. | ✅ PASS |
| II. Spec-Driven Dev | Approved spec.md exists at `specs/001-agent-tutor/spec.md`. Plan derived from spec only. | ✅ PASS |
| III. Selective Hybrid | Phase 1 only. Zero hybrid routes planned. Phase 2 endpoints not scaffolded. | ✅ PASS |
| IV. Agent Skills-First | All 4 SKILL.md files planned in `skills/` before implementation begins. | ✅ PASS |
| V. Phased Architecture | This plan covers Phase 1 scope only. Phase 2 layers (Kafka, Dapr, Claude SDK) not introduced. | ✅ PASS |
| VI. Cost-Conscious | Phase 1 infra: Fly.io ~$10/mo + Neon free + R2 ~$5/mo = ~$15/mo at 10K users = $0.0015/user. | ✅ PASS |
| VII. TDD | Tests in `tests/unit/` and `tests/integration/` written before implementation. Zero-LLM invariant test mandatory. | ✅ PASS |

**Constitution Check: ALL GATES PASS — proceed to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-tutor/
├── plan.md              # This file
├── research.md          # Phase 0: decisions and rationale
├── data-model.md        # Phase 1: DB schema and entity relationships
├── quickstart.md        # Phase 1: local dev setup guide
├── contracts/
│   └── openapi.yaml     # Phase 1: full OpenAPI 3.1 spec
└── tasks.md             # Phase 2 output (via /sp.tasks — NOT created here)
```

### Source Code (repository root)

```text
backend/
├── main.py                          # App entrypoint; Zero-Backend-LLM header comment
├── config.py                        # Pydantic Settings from env vars
├── requirements.txt                 # Python deps (no openai, no anthropic)
├── .env.example                     # All required env var names with descriptions
├── Dockerfile                       # Production container (python:3.12-slim)
├── fly.toml                         # Fly.io deployment config
├── routers/
│   ├── __init__.py
│   ├── chapters.py                  # Content delivery + navigation + access gate
│   ├── quizzes.py                   # Quiz questions (no answers) + rule-based grading
│   ├── progress.py                  # Progress summary + chapter completion + streak
│   ├── search.py                    # Keyword search scoped by access tier
│   ├── access.py                    # Access check + tier info endpoints
│   └── users.py                     # User upsert + profile
├── models/
│   ├── __init__.py
│   ├── chapter.py                   # ChapterSummary, ChapterContent, ChapterNavigation
│   ├── quiz.py                      # Question, QuizQuestions, QuizSubmission, QuizResult
│   ├── progress.py                  # ProgressSummary, StreakUpdate
│   ├── search.py                    # SearchQuery, SearchResult
│   ├── access.py                    # AccessCheck, TierInfo
│   └── user.py                      # UserCreate, User
├── db/
│   ├── __init__.py
│   ├── connection.py                # Async SQLAlchemy engine, session factory, lifespan
│   ├── tables.py                    # SQLAlchemy Table definitions (all 5 tables)
│   └── seed.py                      # Quiz bank + chapters metadata seeder script
└── storage/
    ├── __init__.py
    └── r2_client.py                 # boto3 R2 client; fetch_chapter_content(key) -> str

skills/
├── concept-explainer/
│   └── SKILL.md
├── quiz-master/
│   └── SKILL.md
├── socratic-tutor/
│   └── SKILL.md
└── progress-motivator/
    └── SKILL.md

content/
├── chapter-01.md                    # "What is an AI Agent" — sample for local dev
├── chapter-02.md                    # "Claude Agent SDK Basics" — sample
└── chapter-03.md                    # "Building Your First Agent" — sample

chatgpt-app/
└── manifest.yaml                    # OpenAI App manifest (schema_version, auth, api, etc.)

docs/
├── architecture.md                  # Architecture diagram + system description
└── cost-analysis.md                 # Phase 1 cost breakdown (infra + per-user)

tests/
├── conftest.py                      # pytest fixtures: test DB, test client, sample data
├── unit/
│   ├── test_access_logic.py         # Free vs premium chapter access rules
│   ├── test_quiz_grading.py         # Rule-based scoring: correct/incorrect/pass/fail
│   ├── test_streak_calculation.py   # Streak increment, reset, same-day idempotency
│   └── test_zero_llm_invariant.py   # Import scan: assert no openai/anthropic in backend/
├── integration/
│   ├── test_chapters_api.py         # Content delivery, navigation, access gate
│   ├── test_quiz_api.py             # Questions, submission, grading
│   ├── test_progress_api.py         # Summary, completion, streak update
│   ├── test_search_api.py           # Keyword search, tier scoping
│   ├── test_access_api.py           # Access check + tier info
│   └── test_users_api.py            # Upsert, profile retrieval
└── contract/
    └── test_api_contracts.py        # Validates live responses against openapi.yaml
```

**Structure Decision**: Multi-component layout (backend/, skills/, chatgpt-app/, content/,
docs/, tests/) following the user's plan prompt. `tests/` lives at repo root to cover all
components. `backend/` is a self-contained Python package deployable to Fly.io.

## Complexity Tracking

No constitution violations. All design decisions within spec scope.

## Key Design Decisions

### D1 — Database Access Pattern: SQLAlchemy 2.0 Async + asyncpg

FastAPI's async request handling requires an async DB driver. SQLAlchemy 2.0's native
async API with asyncpg provides connection pooling, clean session management via
dependency injection, and full Neon PostgreSQL compatibility.

**Alternative rejected**: Synchronous psycopg2 — blocks the event loop under load;
not compatible with async FastAPI without `run_in_executor` workaround.

### D2 — R2 Content Serving: Per-Request Fetch via boto3 (No Cache)

Chapter content is fetched from R2 on every `/chapters/{id}/content` request using
`boto3` S3-compatible client. No Redis or in-memory cache in Phase 1.

**Rationale**: R2 content is small (<50KB per chapter), served over Cloudflare's
global CDN edge. Per-request fetch keeps Phase 1 infrastructure minimal ($0 cache
cost) and acceptable under the ≤2s SLA.

**Alternative rejected**: Cache in Fly.io process memory — state not shared across
instances; cache in Redis — adds $15–25/mo cost, violates Phase 1 cost budget.

### D3 — Search Implementation: PostgreSQL Full-Text Search on Cached search_text

Chapter markdown content is loaded into a `search_text TEXT` column in the `chapters`
table at seed time. Search uses PostgreSQL `tsvector`/`tsquery` or `ILIKE` pattern
matching, scoped by `tier_required` vs. user tier.

**Rationale**: Avoids loading all R2 chapter files on every search request. DB-side
search is fast, transactional, and tier-scoped in a single query.

**Alternative rejected**: Fetch all accessible chapters from R2 per search — N R2
requests per search query; unacceptable latency at scale.

### D4 — User Identification: X-User-ID Header (No Auth in Phase 1)

Backend trusts the `X-User-ID` UUID header passed by ChatGPT App. Full authentication
(JWT, OAuth2, session) is out of scope for Phase 1 per spec Assumptions section.

**Rationale**: Minimal friction for hackathon demo; ChatGPT App manages conversation
context and passes user ID. Allows easy Phase 2 migration to Bearer token auth.

### D5 — Streak Calculation: UTC Date Comparison on Progress Write

On every `POST /progress/{user_id}/chapters/{chapter_id}/complete`:
1. Fetch `last_active` from users table
2. Compare with `today` (UTC date)
3. If `today == last_active`: streak unchanged (idempotent)
4. If `today == last_active + 1 day`: `streak_days += 1`
5. Otherwise: `streak_days = 1`
6. Set `last_active = today`

**Rationale**: Simple, correct, no background jobs required in Phase 1.

### D6 — Freemium Gate: Hardcoded Free Chapter List + DB Tier Check

```python
FREE_CHAPTERS = {"chapter-01", "chapter-02", "chapter-03"}
```

Access gate logic in `chapters.py` router (before R2 fetch):
1. If `chapter_id in FREE_CHAPTERS` → allow all users
2. Else → fetch user tier from DB
3. If tier == "premium" → serve content
4. If tier == "free" → return 403 `{"error": "premium_required", "message": "..."}`

**Rationale**: Constant-time check for free chapters avoids a DB query on 60% of
requests. Only premium chapters require a DB tier lookup.

### D7 — Quiz Pass Threshold: 4/5 Correct (80%)

Pass criterion: `score >= 4` where total questions per chapter = 5.
Stored in constant `QUIZ_PASS_THRESHOLD = 4`.

Response includes: `score`, `total`, `percentage`, `passed`, `wrong_question_numbers`.
Correct answers are NOT returned in the response (ChatGPT explains using chapter content).
