# AgentTutor — Architecture Document

## System Overview

AgentTutor is a Phase 1 Zero-Backend-LLM Course Companion FTE built for the Panaversity Agent Factory Hackathon IV.

**Core constraint:** The FastAPI backend makes ZERO LLM API calls. All AI intelligence (explanations, Socratic dialogue, quiz guidance, motivational responses) is delivered by the ChatGPT App frontend using SKILL.md behavioral specifications.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Student)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CHATGPT APP (Intelligence Layer)               │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ concept-explainer│  │   quiz-master    │                │
│  │   SKILL.md       │  │   SKILL.md       │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ socratic-tutor   │  │progress-motivator│                │
│  │   SKILL.md       │  │   SKILL.md       │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                             │
│              GPT Actions (HTTP calls)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Data Layer)                   │
│                   Fly.io — Singapore                        │
│                                                             │
│  /users      /chapters    /quizzes                          │
│  /progress   /search      /access                          │
│  /health                                                    │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  backend/content/chapters/  (10 .md files)  │          │
│  │  Local filesystem — served by FastAPI        │          │
│  └──────────────────────────────────────────────┘          │
└───────────────────────────┬─────────────────────────────────┘
                            │ asyncpg + SSL
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              NEON POSTGRESQL (Persistence Layer)            │
│                                                             │
│  users          chapters       progress                     │
│  quiz_bank      quiz_results                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | 3.12 | Latest stable, built-in `list`/`dict` generics |
| Web framework | FastAPI | 0.115+ | Async-native, auto OpenAPI docs |
| ASGI server | Uvicorn | 0.30+ | Production-grade async server |
| ORM | SQLAlchemy | 2.0 async | Type-safe, async query API |
| DB driver | asyncpg | 0.29+ | Fastest async PostgreSQL driver |
| Test DB driver | aiosqlite | 0.20+ | SQLite for unit/integration tests |
| Validation | Pydantic | v2 | Fast, schema-based validation |
| Database | Neon PostgreSQL | — | Serverless, free tier, SSL |
| Content storage | Local filesystem | — | Replaces Cloudflare R2; zero cost, zero latency |
| Deployment | Fly.io | — | Global edge, free tier |
| Testing | pytest + pytest-asyncio | 8.0+ | Async test support |
| HTTP client (tests) | HTTPX | 0.27+ | ASGI transport for integration tests |

---

## Data Model

### users
```
id          UUID PK
email       TEXT UNIQUE NOT NULL
name        TEXT NOT NULL
tier        TEXT ('free'|'premium') DEFAULT 'free'
streak_days INT DEFAULT 0
last_active DATE
created_at  TIMESTAMPTZ DEFAULT now()
```

### chapters
```
id            TEXT PK  (e.g. 'chapter-01')
number        INT UNIQUE NOT NULL
title         TEXT NOT NULL
tier_required TEXT ('free'|'premium')
search_text   TEXT  (denormalized for ILIKE search)
```

### progress
```
id           UUID PK
user_id      UUID FK → users
chapter_id   TEXT FK → chapters
completed    BOOL DEFAULT false
completed_at TIMESTAMPTZ
```

### quiz_bank
```
id              UUID PK
chapter_id      TEXT FK → chapters
question_number INT
question        TEXT
option_a/b/c/d  TEXT
correct_answer  TEXT  (never returned to client)
```

### quiz_results
```
id              UUID PK
user_id         UUID FK → users
chapter_id      TEXT FK → chapters
score           INT
total_questions INT
answers         JSONB
attempted_at    TIMESTAMPTZ DEFAULT now()
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /users | Create/upsert user by email |
| GET | /users/{id} | Get user profile |
| GET | /chapters | List all chapters with accessibility flags |
| GET | /chapters/{id}/content | Get chapter markdown content |
| GET | /chapters/{id}/next | Next chapter navigation |
| GET | /chapters/{id}/previous | Previous chapter navigation |
| GET | /quizzes/{id}/questions | Get quiz questions (no answers) |
| POST | /quizzes/{id}/submit | Submit answers, get graded result |
| GET | /progress/{user_id} | Full progress summary |
| POST | /progress/{user_id}/chapters/{id}/complete | Mark chapter complete, update streak |
| GET | /search | Tier-scoped content search |
| GET | /access/check | Check chapter access for user |
| GET | /access/{user_id}/tier | Get tier info and chapter counts |
| GET | /health | Health check — always returns llm_calls: 0 |

---

## Freemium Access Control

```python
FREE_CHAPTERS = {"chapter-01", "chapter-02", "chapter-03"}

def is_accessible(chapter_tier: str, user_tier: str, chapter_id: str) -> bool:
    if chapter_id in FREE_CHAPTERS:
        return True          # Always free
    return user_tier == "premium"
```

Chapters 1–3 are universally accessible. Chapters 4–10 require `tier = "premium"`.

---

## Zero-Backend-LLM Enforcement

The invariant is enforced at two levels:

1. **Architecture:** No openai/anthropic/langchain packages in `requirements.txt`
2. **Automated test:** `tests/unit/test_zero_llm_invariant.py` uses AST scanning to detect any LLM SDK imports across the entire `backend/` directory. This test fails CI if violated.

---

## Key Design Decisions

1. **Local filesystem over Cloudflare R2** — Eliminates cloud storage cost and complexity for Phase 1. Chapter `.md` files live at `backend/content/chapters/`. Upgrade path to R2 exists for Phase 2.

2. **Denormalized `search_text`** — PostgreSQL full-text search using a pre-populated `chapters.search_text` column with ILIKE queries. Avoids complexity of `tsvector` for Phase 1 scope.

3. **asyncpg over psycopg3** — asyncpg is the fastest async PostgreSQL driver; battle-tested for high-concurrency FastAPI applications.

4. **aiosqlite for tests** — SQLite in-memory databases for unit/integration tests means zero external dependencies when running the test suite locally.

5. **Upsert user creation** — `POST /users` uses `ON CONFLICT DO UPDATE` so the same user can be registered multiple times without error — important for stateless ChatGPT App clients.
