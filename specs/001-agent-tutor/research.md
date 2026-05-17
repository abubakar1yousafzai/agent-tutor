# Phase 0 Research: AgentTutor Backend

**Feature**: 001-agent-tutor
**Date**: 2026-05-01
**Branch**: 001-agent-tutor

## Research Questions Resolved

All technical context was fully specified in the user's plan prompt. No NEEDS
CLARIFICATION items were raised. Decisions documented below for audit trail.

---

## R1 — Database Driver: SQLAlchemy 2.0 Async + asyncpg

**Decision**: Use SQLAlchemy 2.0 with the `asyncpg` driver for all PostgreSQL
operations.

**Rationale**:
- FastAPI is fully async; blocking DB calls under load degrade throughput severely
- SQLAlchemy 2.0 provides a clean `async with AsyncSession` API matching FastAPI's
  dependency injection pattern
- asyncpg is the fastest pure-async PostgreSQL driver for Python (2–3× faster than
  psycopg2 in benchmarks for high-concurrency workloads)
- Neon PostgreSQL is fully compatible with asyncpg connection strings

**Alternatives considered**:
- psycopg3 (async): newer, less community documentation; no advantage over asyncpg
  for this use case
- SQLAlchemy sync + `run_in_executor`: works but defeats the purpose of async FastAPI;
  adds boilerplate

**Required packages**: `sqlalchemy[asyncio]>=2.0`, `asyncpg>=0.29`

---

## R2 — R2 Storage Client: boto3 with S3-Compatible Endpoint

**Decision**: Use `boto3` S3 client pointed at Cloudflare R2's S3-compatible endpoint
`https://{ACCOUNT_ID}.r2.cloudflarestorage.com`.

**Rationale**:
- Cloudflare R2 is fully S3-compatible; boto3 requires only a custom `endpoint_url`
- boto3 handles request signing (AWS SigV4), retries, and error normalisation
- `NoSuchKey` exception maps cleanly to HTTP 404 response

**Configuration**:
```python
boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)
```

**Chapter file key format**: `chapters/chapter-{NN}.md` (e.g., `chapters/chapter-01.md`)

**Error handling**: Catch `ClientError` with `Code == "NoSuchKey"` → raise HTTP 404.

**Alternatives considered**:
- httpx direct requests to R2 public URL: no auth headers needed for public objects,
  but public R2 buckets expose all objects; private bucket + signed URLs adds complexity
- cloudflare-python SDK: no S3 compatibility layer; requires Cloudflare Workers for
  serving, not appropriate here

**Required packages**: `boto3>=1.35`

---

## R3 — Search Strategy: PostgreSQL Text Search on Cached Column

**Decision**: Store each chapter's plaintext content in a `search_text TEXT` column
(populated at seed time from R2). Run `ILIKE '%keyword%'` search scoped by user tier.

**Rationale**:
- R2 is object storage, not a search engine; fetching all chapters per search query
  would mean N R2 requests (N = accessible chapters)
- Caching search_text in PostgreSQL keeps search to a single query
- `ILIKE` is sufficient for Phase 1 keyword search; full PostgreSQL `tsvector` ranking
  can be added in Phase 2 if needed
- Scope enforcement (free vs premium) is a natural SQL `WHERE tier_required IN (...)` clause

**Search query pattern**:
```sql
SELECT id, title, number,
       SUBSTRING(search_text FROM
         GREATEST(1, POSITION(LOWER(:q) IN LOWER(search_text)) - 100)
         FOR 300) AS excerpt
FROM chapters
WHERE tier_required IN (:allowed_tiers)
  AND LOWER(search_text) LIKE LOWER(:pattern)
ORDER BY number
LIMIT :limit;
```

**Alternatives considered**:
- PostgreSQL `tsvector`: better ranking and stemming; overkill for Phase 1 exact-keyword
  search; can be added in Phase 2
- Elasticsearch / MeiliSearch: massive overkill for 10 chapters; violates cost constraint
- Fetch from R2 per search: N R2 HTTP requests per search; unacceptable latency

---

## R4 — Async R2 Client: Synchronous boto3 in Thread Pool

**Decision**: boto3 is synchronous. Wrap R2 calls with `asyncio.to_thread()` to avoid
blocking the FastAPI event loop.

```python
import asyncio

async def fetch_chapter_content(key: str) -> str:
    return await asyncio.to_thread(_sync_fetch, key)
```

**Rationale**: boto3 has no native async support. `asyncio.to_thread` delegates blocking
I/O to a thread pool without blocking the event loop, preserving FastAPI's concurrency.

**Alternative rejected**: `aiobotocore` / `aioboto3`: additional dependency; API
differences from boto3 increase maintenance burden for marginal gain at Phase 1 scale.

---

## R5 — CORS Configuration for ChatGPT App

**Decision**: Accept `ALLOWED_ORIGINS` as a comma-separated env var. Default includes
ChatGPT plugin origins.

```
ALLOWED_ORIGINS=https://chatgpt.com,https://chat.openai.com,http://localhost:3000
```

FastAPI `CORSMiddleware` applied in `main.py` with `allow_credentials=False` (no cookie
auth in Phase 1).

---

## R6 — Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `R2_ACCOUNT_ID` | Cloudflare account ID for R2 endpoint | `abc123def456` |
| `R2_ACCESS_KEY_ID` | R2 API token (access key) | `key_id_here` |
| `R2_SECRET_ACCESS_KEY` | R2 API token (secret) | `secret_here` |
| `R2_BUCKET_NAME` | R2 bucket storing course content | `agenttutor-content` |
| `R2_PUBLIC_URL` | Optional CDN URL for direct public links | `https://cdn.agenttutor.io` |
| `DATABASE_URL` | Neon async connection string | `postgresql+asyncpg://user:pw@host/db` |
| `APP_ENV` | Environment flag | `development` or `production` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `https://chatgpt.com,...` |

---

## R7 — Deployment: Fly.io with Docker

**Decision**: Single Docker container deployed to Fly.io `fly.io/apps/agenttutor-backend`.

**Dockerfile base**: `python:3.12-slim`
**Process**: `uvicorn backend.main:app --host 0.0.0.0 --port 8080 --workers 2`
**fly.toml**: `[http_service]` on port 8080, auto_stop_machines = false for Phase 1 demo.

**Cost estimate**: Fly.io shared-cpu-1x (256MB RAM) = ~$1.94/mo. With 2 machines for
HA: ~$4/mo. Well within Phase 1 cost budget.

---

## R8 — Zero-LLM Invariant Test Strategy

**Decision**: A dedicated unit test `tests/unit/test_zero_llm_invariant.py` scans all
`.py` files under `backend/` using Python's `ast` module to assert:
1. No `import openai` or `import anthropic` statements
2. No `from openai` or `from anthropic` imports
3. `requirements.txt` does not contain `openai` or `anthropic`

This test is the first test in CI and blocks all further tests if it fails.

**Rationale**: Static analysis catches accidental LLM imports before code review;
cannot be bypassed by dynamic imports (those would be a deliberate violation, not
an accident).
