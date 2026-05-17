---
id: "002"
title: AgentTutor Backend Implementation Plan
stage: plan
date: 2026-05-01
surface: agent
model: claude-sonnet-4-6
feature: agent-tutor
branch: 001-agent-tutor
user: Abu Bakar
command: /sp.plan
labels: ["plan","agent-tutor","fastapi","zero-backend-llm","postgresql","cloudflare-r2","openapi"]
links:
  spec: specs/001-agent-tutor/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-agent-tutor/plan.md
  - specs/001-agent-tutor/research.md
  - specs/001-agent-tutor/data-model.md
  - specs/001-agent-tutor/quickstart.md
  - specs/001-agent-tutor/contracts/openapi.yaml
  - history/prompts/agent-tutor/002-agenttutor-backend-implementation-plan.plan.prompt.md
tests:
  - N/A (plan authoring task; test strategy defined in plan.md)
---

## Prompt

Create a detailed technical implementation plan for the AgentTutor FastAPI backend
based on the spec. The plan should cover folder structure, API design, database
schema, and storage integration.

Folder Structure: backend/ (routers/, models/, db/, storage/), skills/, content/,
chatgpt-app/, docs/. API Endpoints: Chapters (list, content, next, prev), Search,
Quizzes (questions, submit), Progress (summary, complete, %), Access (check, tier),
Users (upsert). Database: users, progress, quiz_results, quiz_bank tables.
R2 Integration: boto3 with custom endpoint. Env vars: R2 credentials, DATABASE_URL,
APP_ENV, ALLOWED_ORIGINS. Freemium gate: FREE_CHAPTERS constant + DB tier check.
Quiz grading: rule-based, score/5, pass=4+, no correct answers returned.
Strict constraint: no openai/anthropic imports; Zero-LLM comment in main.py.

## Response snapshot

Ran `setup-plan.ps1 -Json` → copied plan template to specs/001-agent-tutor/plan.md.

Produced 5 plan artifacts:

**plan.md**: Full implementation plan with Technical Context (Python 3.12, FastAPI,
SQLAlchemy 2.0 async, asyncpg, boto3), Constitution Check (all 7 gates PASS),
complete project folder structure, and 7 key design decisions:
D1 SQLAlchemy 2.0 async; D2 per-request R2 fetch (no cache); D3 PostgreSQL
full-text search on cached search_text column; D4 X-User-ID header auth;
D5 UTC streak calculation; D6 FREE_CHAPTERS constant + DB tier check;
D7 quiz pass threshold = 4/5.

**research.md**: 8 research decisions — DB driver (asyncpg), R2 client (boto3),
search strategy (DB cached search_text + ILIKE), async R2 wrapping
(asyncio.to_thread), CORS config, env var table, Fly.io deployment, Zero-LLM
invariant static analysis test.

**data-model.md**: 5 table definitions (users, chapters, progress, quiz_results,
quiz_bank) with full migration SQL, chapter ID mapping table (10 chapters),
streak calculation logic (Python), quiz grading logic (Python).

**contracts/openapi.yaml**: Full OpenAPI 3.1 spec with 16 endpoints across 6 tags
(Users, Chapters, Search, Quizzes, Progress, Access), all schemas, error models.

**quickstart.md**: Step-by-step local dev guide covering venv setup, .env config,
DB migration, R2 upload, seeding, running, zero-LLM invariant test, smoke tests,
Fly.io deployment, and common issue table.

Agent context updated via update-agent-context.ps1 (CLAUDE.md updated with
Python 3.12, FastAPI, SQLAlchemy, asyncpg, boto3, Neon, R2).

## Outcome

- ✅ Impact: Complete Phase 1 implementation plan; all 7 constitution gates pass; 5 design artifacts ready for /sp.tasks
- 🧪 Tests: Test structure defined in plan.md; zero-LLM invariant test strategy in research.md (R8); integration test file list in project structure
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml (all created/updated)
- 🔁 Next prompts: `/sp.tasks` to generate implementation task list; `/sp.adr` for Zero-LLM enforcement strategy decision
- 🧠 Reflection: The user's plan prompt was extremely detailed — no NEEDS CLARIFICATION items generated. The search strategy (DB-cached search_text instead of per-request R2 fetch) was the most important architectural decision, as it avoids N R2 HTTP calls per search query.

## Evaluation notes (flywheel)

- Failure modes observed: update-agent-context.ps1 ran successfully; setup-plan.ps1 ran successfully
- Graders run and results (PASS/FAIL): Constitution Check — 7/7 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding a chapters table `search_vector TSVECTOR` generated column to enable ranked search (Phase 1.5 improvement)
