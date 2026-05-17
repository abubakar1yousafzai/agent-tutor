# Quickstart: AgentTutor Backend (Local Development)

**Feature**: 001-agent-tutor
**Date**: 2026-05-01

## Prerequisites

- Python 3.12+
- Docker (optional, for local PostgreSQL)
- A Neon PostgreSQL account (free tier) — or local Postgres 15+
- A Cloudflare R2 bucket with API token
- Git

## 1. Clone and Setup

```bash
git clone <repo-url>
cd Hackathon-4
git checkout 001-agent-tutor
```

## 2. Create Virtual Environment

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Configure Environment Variables

Copy the example env file:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# Cloudflare R2
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=agenttutor-content
R2_PUBLIC_URL=https://pub-xxxx.r2.dev   # optional CDN URL

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/agenttutor

# App
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:3000,https://chatgpt.com,https://chat.openai.com
```

## 4. Set Up Database

**Option A: Neon (recommended for production)**
1. Create a new Neon project at [neon.tech](https://neon.tech)
2. Copy the connection string → set as `DATABASE_URL` (replace `postgresql://` with
   `postgresql+asyncpg://`)

**Option B: Local PostgreSQL with Docker**
```bash
docker run -d \
  --name agenttutor-db \
  -e POSTGRES_DB=agenttutor \
  -e POSTGRES_USER=agenttutor \
  -e POSTGRES_PASSWORD=agenttutor \
  -p 5432:5432 \
  postgres:15-alpine
# Then: DATABASE_URL=postgresql+asyncpg://agenttutor:agenttutor@localhost:5432/agenttutor
```

## 5. Run Database Migrations

```bash
# From backend/ directory
python -m db.seed --create-tables
```

This creates all 5 tables (`users`, `chapters`, `progress`, `quiz_results`, `quiz_bank`)
and seeds the chapters metadata.

## 6. Upload Sample Chapter Content to R2

```bash
# From repo root — upload free tier sample files
python backend/storage/upload_samples.py --folder content/
```

Or manually upload `content/chapter-01.md`, `content/chapter-02.md`,
`content/chapter-03.md` to your R2 bucket under the path `chapters/`.

## 7. Seed Quiz Bank

```bash
# From backend/ directory
python -m db.seed --quiz-bank
```

This populates the `quiz_bank` table with 5 questions per chapter (50 total).
It also loads `search_text` from R2 content into the `chapters` table.

## 8. Run the Backend

```bash
# Development (auto-reload)
uvicorn backend.main:app --reload --port 8000

# Production
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --workers 2
```

API available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs` (Swagger UI)

## 9. Verify Zero-LLM Invariant

```bash
cd ..   # repo root
pytest tests/unit/test_zero_llm_invariant.py -v
```

Expected output:
```
PASSED tests/unit/test_zero_llm_invariant.py::test_no_openai_imports
PASSED tests/unit/test_zero_llm_invariant.py::test_no_anthropic_imports
PASSED tests/unit/test_zero_llm_invariant.py::test_requirements_no_llm_packages
```

## 10. Run All Tests

```bash
# From repo root
pytest tests/ -v --tb=short
```

## 11. Quick API Smoke Test

```bash
# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test Student"}'

# List chapters (copy user_id from above response)
curl "http://localhost:8000/chapters?user_id=<user_id>"

# Get chapter 1 content
curl "http://localhost:8000/chapters/chapter-01/content?user_id=<user_id>"

# Try chapter 4 as free user (expect 403)
curl "http://localhost:8000/chapters/chapter-04/content?user_id=<user_id>"
```

## 12. Deploy to Fly.io

```bash
# Install flyctl: https://fly.io/docs/getting-started/install-flyctl/
fly auth login

# From backend/ directory
fly launch --name agenttutor-backend --region sin --no-deploy
fly secrets set \
  R2_ACCOUNT_ID=... \
  R2_ACCESS_KEY_ID=... \
  R2_SECRET_ACCESS_KEY=... \
  R2_BUCKET_NAME=... \
  DATABASE_URL=... \
  APP_ENV=production \
  ALLOWED_ORIGINS=https://chatgpt.com,https://chat.openai.com

fly deploy
```

## Common Issues

| Issue | Solution |
|---|---|
| `asyncpg.exceptions.ConnectionFailure` | Check DATABASE_URL; ensure Neon allows connections from your IP |
| `botocore.exceptions.ClientError: NoSuchKey` | Chapter file not uploaded to R2; check content_key path |
| `422 Unprocessable Entity` | Missing `user_id` query param; all content endpoints require it |
| `CORS error in ChatGPT App` | Add `https://chatgpt.com` to `ALLOWED_ORIGINS` env var |
| `ImportError: openai` or `anthropic` | Violation of Zero-LLM constraint — remove the import immediately |
