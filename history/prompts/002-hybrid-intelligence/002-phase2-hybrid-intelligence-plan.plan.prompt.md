---
id: "002"
title: Phase 2 Hybrid Intelligence Implementation Plan
stage: plan
date: 2026-05-17
surface: agent
model: claude-sonnet-4-6
feature: 002-hybrid-intelligence
branch: 002-hybrid-intelligence
user: Abu Bakar
command: /sp.plan
labels: ["plan","hybrid","gemini","openai-agents","fastapi","premium","asyncio","phase2"]
links:
  spec: specs/002-hybrid-intelligence/spec.md
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - specs/002-hybrid-intelligence/plan.md
  - specs/002-hybrid-intelligence/research.md
  - specs/002-hybrid-intelligence/data-model.md
  - specs/002-hybrid-intelligence/quickstart.md
  - specs/002-hybrid-intelligence/contracts/hybrid-assess.yaml
  - specs/002-hybrid-intelligence/contracts/hybrid-mentor.yaml
tests:
  - "null"
---

## Prompt

# AgentTutor Phase 2 — Create a detailed technical implementation plan for AgentTutor Phase 2 hybrid intelligence features based on the Phase 2 spec. Phase 1 code must not be touched. All new code goes into isolated files.

New files: backend/routers/hybrid.py, backend/agents/mentor_agent.py, backend/agents/assessor_agent.py, backend/agents/__init__.py, tests/integration/test_hybrid_assess_api.py, tests/integration/test_hybrid_mentor_api.py. Only main.py modified among existing files.

Shared get_llm_model() using AsyncOpenAI + Gemini via OpenAI-compatible API. Two endpoints: POST /hybrid/assess (LLM graded assessment, $0.014) and POST /hybrid/mentor (AI Mentor Agent with tools, $0.090). Both gated behind premium tier check. Runner.run_sync() used for agent execution. Pydantic models for AssessRequest/Response and MentorRequest/Response. Integration tests for both endpoints. Architecture separation verification via git diff.

## Response snapshot

Generated complete implementation plan in `specs/002-hybrid-intelligence/plan.md` covering:

**Phase 0 — Research (6 decisions resolved):**
- R1: `asyncio.to_thread(Runner.run_sync, ...)` to prevent event loop blocking
- R2: Pre-fetch student progress in async endpoint, pass to sync tool via closure
- R3: Shared `backend/agents/llm_client.py` instead of importing from mentor_agent (avoids asymmetric coupling)
- R4: Two-attempt JSON extraction (direct parse → regex fencing strip → retry)
- R5: Tool call tracking via `result.new_messages` inspection
- R6: Mock `asyncio.to_thread` in tests for deterministic CI

**Phase 1 — Design:**
- Data model: no new DB tables; read-only access to `users`, `progress`, `quiz_results`
- Pydantic models: AssessRequest, AssessResponse, MentorRequest, MentorResponse (inline in hybrid.py)
- API contracts: OpenAPI specs for both endpoints in `contracts/`
- Blueprint request flows for both endpoints (9-step each)
- System prompts defined as module-level constants
- main.py change: exactly 2 lines (import + include_router)
- Architecture separation verification command documented

**Supporting artifacts:**
- `research.md` — all 6 research decisions documented
- `data-model.md` — entity relationships and field mapping
- `contracts/hybrid-assess.yaml` — full OpenAPI 3.1 spec
- `contracts/hybrid-mentor.yaml` — full OpenAPI 3.1 spec
- `quickstart.md` — developer setup guide with curl examples
- Agent context updated via `update-agent-context.ps1`

Constitution Check: PASS on all 5 gates (Principles I, III, V, VI, VII).

## Outcome

- ✅ Impact: Complete technical plan with all architectural decisions resolved; zero Phase 1 files modified; all unknowns from spec stage are eliminated
- 🧪 Tests: 4 integration test cases fully designed (2 per endpoint); mock strategy defined
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/hybrid-assess.yaml, contracts/hybrid-mentor.yaml
- 🔁 Next prompts: /sp.tasks to generate dependency-ordered task list for implementation
- 🧠 Reflection: Key insight — Runner.run_sync() in async FastAPI needs asyncio.to_thread(); pre-fetching DB data before agent creation elegantly solves the sync-tool/async-DB mismatch without new dependencies

## Evaluation notes (flywheel)

- Failure modes observed: None — plan completed cleanly; agent context script ran successfully
- Graders run and results (PASS/FAIL): Constitution Check — all 5 gates PASS
- Prompt variant (if applicable): "null"
- Next experiment: Validate that OpenAI Agents SDK RunResult.new_messages structure matches the tool-call inspection pattern planned in R5 during red-phase implementation
