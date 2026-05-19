# Tasks: AgentTutor Phase 2 — Hybrid Intelligence

**Input**: Design documents from `specs/002-hybrid-intelligence/`  
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅  
**Branch**: `002-hybrid-intelligence`

**Tests**: Integration tests are explicitly required by FR-014 and SC-004. TDD approach: write failing tests before implementation.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description — file path`

- **[P]**: Parallelizable (different files, no shared-state dependencies)
- **[US#]**: Maps to user story in spec.md
- Tests MUST be written and confirmed FAILING before implementation begins

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the new dependency and environment variable before any code is written.

- [X] T001 Add `openai-agents` to `backend/requirements.txt` (new line after `jsonschema>=4.0.0`)
- [X] T002 [P] Add `GEMINI_API_KEY=your_gemini_api_key_here` block to `backend/.env.example` with a `# Phase 2 — Hybrid Intelligence` comment header

**Checkpoint**: `pip install -r backend/requirements.txt` completes without error; `backend/.env.example` shows the new key.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure that BOTH user story endpoints depend on — must be complete before any endpoint work begins.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [X] T003 Create `backend/agents/__init__.py` as an empty file (module marker only — no content)
- [X] T004 Create `backend/agents/llm_client.py` with a single `get_llm_model()` function that builds `AsyncOpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")` and returns `OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)`; import `Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI` from `agents` and `os`
- [X] T005 Create `backend/routers/hybrid.py` with: (a) `APIRouter(prefix="", tags=["Hybrid Intelligence"])`, (b) four Pydantic models — `AssessRequest(user_id: UUID, chapter_id: str, question: str, student_answer: str)`, `AssessResponse(score: int, max_score: int, grade: str, feedback: str, what_was_correct: str, what_was_missing: str, improvement_tip: str, estimated_cost_usd: float)`, `MentorRequest(user_id: UUID, question: str)`, `MentorResponse(mentor_response: str, chapters_referenced: list[str], tools_used: list[str], estimated_cost_usd: float)`, (c) async helper `_require_premium(user_id, db)` that SELECTs tier from users table and raises `HTTPException(403, {"error": "premium_required", "detail": "This feature requires a premium subscription."})` if tier is `"free"` or user not found, (d) async helper `_fetch_progress_summary(user_id, db)` that JOINs progress + quiz_results tables and returns a formatted multiline string listing completed chapters and best quiz scores
- [X] T006 Add hybrid router import and registration to `backend/main.py`: add `from backend.routers import hybrid` after the existing router imports, and `app.include_router(hybrid.router, prefix="/hybrid", tags=["Hybrid Intelligence"])` after the existing `app.include_router(access.router)` line — these are the ONLY two changes to `main.py`

**Checkpoint**: Server starts with `uvicorn backend.main:app --reload`; `/docs` shows a "Hybrid Intelligence" section; `/hybrid/assess` and `/hybrid/mentor` appear (returning 422 since they have no implementations yet).

---

## Phase 3: User Story 1 — Premium LLM Graded Assessment (Priority: P1) 🎯 MVP

**Goal**: A premium student can POST a written answer and receive AI-graded structured feedback with score, grade, and improvement tip.

**Independent Test**: `POST /hybrid/assess` with a premium user returns 200 with all 8 required fields; with a free user returns 403 with `premium_required`.

### Tests for User Story 1 ⚠️ Write FIRST — confirm FAILING before T010

- [X] T007 [US1] Create `tests/integration/test_hybrid_assess_api.py` with two test cases using existing conftest fixtures: `test_assess_free_user_returns_403` — POST to `/hybrid/assess` with `free_user` fixture, assert status 403 and `response.json()["error"] == "premium_required"`; `test_assess_premium_user_returns_result` — patch `asyncio.to_thread` to return a mock `RunResult` with `final_output='{"score":8,"max_score":10,"grade":"B+","feedback":"Good.","what_was_correct":"X","what_was_missing":"Y","improvement_tip":"Z"}'` and `new_messages=[]`, POST to `/hybrid/assess` with `premium_user` fixture and `chapter_id="chapter-01"`, assert status 200, all 8 fields present in response, and `response.json()["estimated_cost_usd"] == 0.014`

### Implementation for User Story 1

- [X] T008 [P] [US1] Create `backend/agents/assessor_agent.py` with: (a) module-level constant `ASSESSOR_SYSTEM_PROMPT` containing the exact grading system prompt from `plan.md` Section "ASSESSOR_SYSTEM_PROMPT", (b) `extract_json(raw: str) -> dict` function that tries `json.loads(raw)` first then strips ` ```json ... ``` ` markdown fencing with `re.sub` and retries, (c) `run_assessment(chapter_content: str, question: str, student_answer: str) -> dict` function that creates `Agent(model=get_llm_model(), instructions=ASSESSOR_SYSTEM_PROMPT)`, builds a user message combining the three inputs with clear labels, calls `Runner.run_sync(agent, message)`, and returns `extract_json(result.final_output)`; import `Agent, Runner` from `agents`, `json`, `re`, and `get_llm_model` from `backend.agents.llm_client`
- [X] T009 [US1] Implement `POST /hybrid/assess` endpoint in `backend/routers/hybrid.py`: call `await _require_premium(body.user_id, db)`, then `content = get_local_content(body.chapter_id)` (import from `backend.storage.content_reader`) raising 404 if `None`, then `parsed = await asyncio.to_thread(run_assessment, content, body.question, body.student_answer)` (import `run_assessment` from `backend.agents.assessor_agent`), add `logger.info("assess cost=0.014 user=%s chapter=%s", body.user_id, body.chapter_id)`, return `AssessResponse(**parsed, estimated_cost_usd=0.014)` wrapped in try/except `json.JSONDecodeError` → 500; add `import asyncio, logging` and `logger = logging.getLogger(__name__)` at module top
- [X] T010 [US1] Run `pytest tests/integration/test_hybrid_assess_api.py -v` and confirm both tests pass (green); fix any issues before proceeding

**Checkpoint**: `test_assess_free_user_returns_403` ✅ and `test_assess_premium_user_returns_result` ✅ — User Story 1 independently complete.

---

## Phase 4: User Story 2 — AI Mentor Agent (Priority: P2)

**Goal**: A premium student can POST any question and receive a personalised Socratic response from an agent that fetches chapter content and checks student progress before answering.

**Independent Test**: `POST /hybrid/mentor` with a premium user returns 200 with `mentor_response`, `chapters_referenced`, `tools_used`, and `estimated_cost_usd`; with a free user returns 403 with `premium_required`.

### Tests for User Story 2 ⚠️ Write FIRST — confirm FAILING before T014

- [X] T011 [US2] Create `tests/integration/test_hybrid_mentor_api.py` with two test cases using existing conftest fixtures: `test_mentor_free_user_returns_403` — POST to `/hybrid/mentor` with `free_user` fixture, assert status 403 and `response.json()["error"] == "premium_required"`; `test_mentor_premium_user_returns_result` — patch `asyncio.to_thread` to return a mock `RunResult` with `final_output="Great question! Let me check the chapter."` and `new_messages=[]`, POST to `/hybrid/mentor` with `premium_user` fixture and non-empty question, assert status 200 and all four response fields present (`mentor_response`, `chapters_referenced`, `tools_used`, `estimated_cost_usd`), and `response.json()["estimated_cost_usd"] == 0.090`

### Implementation for User Story 2

- [X] T012 [P] [US2] Create `backend/agents/mentor_agent.py` with: (a) module-level constant `MENTOR_SYSTEM_PROMPT` containing the exact mentor system prompt from `plan.md` Section "MENTOR_SYSTEM_PROMPT", (b) `_extract_tool_calls(result) -> tuple[list[str], list[str]]` function that iterates `result.new_messages`, finds assistant messages with `content` blocks of `type == "tool_use"`, collects unique tool names into `tools_used` and unique `chapter_id` values from `get_chapter_content` calls into `chapters_referenced`, returns `(tools_used, chapters_referenced)`, (c) `run_mentor(question: str, progress_summary: str) -> tuple[str, list[str], list[str]]` function that defines two sync tool functions: `get_chapter_content(chapter_id: str) -> str` (docstring: "Fetch the full markdown content of the chapter with the given chapter_id") using `get_local_content(chapter_id)` returning `"Chapter not found."` if `None`, and `get_student_progress(user_id: str) -> str` (docstring: "Return the student's completed chapters and quiz scores") returning the `progress_summary` closure variable; creates `Agent(model=get_llm_model(), tools=[get_chapter_content, get_student_progress], instructions=MENTOR_SYSTEM_PROMPT)`; calls `Runner.run_sync(mentor_agent, question)`; calls `_extract_tool_calls(result)`; returns `(result.final_output, chapters_referenced, tools_used)`; import `Agent, Runner` from `agents`, `get_llm_model` from `backend.agents.llm_client`, `get_local_content` from `backend.storage.content_reader`
- [X] T013 [US2] Implement `POST /hybrid/mentor` endpoint in `backend/routers/hybrid.py`: call `await _require_premium(body.user_id, db)`, then `progress_summary = await _fetch_progress_summary(body.user_id, db)`, then `mentor_response, chapters_referenced, tools_used = await asyncio.to_thread(run_mentor, body.question, progress_summary)` (import `run_mentor` from `backend.agents.mentor_agent`), add `logger.info("mentor cost=0.090 user=%s tools=%s", body.user_id, tools_used)`, return `MentorResponse(mentor_response=mentor_response, chapters_referenced=chapters_referenced, tools_used=tools_used, estimated_cost_usd=0.090)` wrapped in try/except → 500
- [X] T014 [US2] Run `pytest tests/integration/test_hybrid_mentor_api.py -v` and confirm both tests pass (green); fix any issues before proceeding

**Checkpoint**: `test_mentor_free_user_returns_403` ✅ and `test_mentor_premium_user_returns_result` ✅ — User Story 2 independently complete.

---

## Phase 5: User Story 3 — Free-Tier Access Enforcement (Priority: P3)

**Goal**: Verify that free-tier users are blocked from both hybrid endpoints with a correct 403 response, and that Phase 1 is completely untouched.

**Independent Test**: Both 403 test cases pass (already validated in US1/US2); `git diff main -- backend/routers/chapters.py [...]` produces empty output; full Phase 1 test suite passes with zero regressions.

- [X] T015 [P] [US3] Run `git diff main -- backend/routers/chapters.py backend/routers/quizzes.py backend/routers/progress.py backend/routers/search.py backend/routers/access.py backend/routers/users.py backend/db/ backend/models/ backend/storage/ backend/config.py` and confirm output is empty (no Phase 1 files modified); document result
- [X] T016 [US3] Run full Phase 1 test suite `pytest tests/ -v --ignore=tests/integration/test_hybrid_assess_api.py --ignore=tests/integration/test_hybrid_mentor_api.py` and confirm zero failures (regression guard)
- [X] T017 [P] [US3] Confirm `/health` returns `{"status": "ok", "llm_calls": 0}` by calling the running server — Phase 1 invariant still holds after hybrid router registration

**Checkpoint**: Architecture separation verified ✅; zero Phase 1 regressions ✅; health endpoint invariant preserved ✅ — User Story 3 complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation completeness, and OpenAPI verification.

- [X] T018 [P] Confirm `logger.info` cost-logging calls are present in `backend/routers/hybrid.py` for both endpoints (grep for `"assess cost"` and `"mentor cost"`)
- [X] T019 [P] Run `pytest tests/ -v` (all tests including hybrid) and confirm 100% pass rate
- [X] T020 Run quickstart.md validation: install `openai-agents`, set `GEMINI_API_KEY` in `backend/.env`, start server, verify `/docs` shows both hybrid endpoints under "Hybrid Intelligence" tag with correct request/response schemas
- [X] T021 [P] Confirm `backend/.env` is listed in `.gitignore` (GEMINI_API_KEY must never be committed)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup          → No dependencies; start immediately
Phase 2: Foundational   → Requires Phase 1 complete; BLOCKS all user story phases
Phase 3: US1 (P1)       → Requires Phase 2 complete
Phase 4: US2 (P2)       → Requires Phase 2 complete; can run in parallel with US1 after Phase 2
Phase 5: US3 (P3)       → Requires Phase 3 AND Phase 4 complete (validates both)
Phase 6: Polish         → Requires Phase 5 complete
```

### User Story Dependencies

- **US1 (P1)**: Depends only on Phase 2 Foundational — no dependency on US2 or US3
- **US2 (P2)**: Depends only on Phase 2 Foundational — no dependency on US1 or US3
- **US3 (P3)**: Validates both US1 and US2 are complete and correct — depends on both

### Within Each User Story

```
Tests (T007/T011) → MUST be written and FAILING before implementation
Assessor/Mentor module (T008/T012) → Can be written in parallel with tests
Endpoint wiring (T009/T013) → Requires agent module complete
Verification (T010/T014) → Final green-phase confirmation
```

### Parallel Opportunities Per Story

**US1 (Phase 3)**:
```bash
# Run in parallel (different files):
Task T007: Write tests/integration/test_hybrid_assess_api.py
Task T008: Create backend/agents/assessor_agent.py
# Then sequentially:
Task T009: Wire endpoint in hybrid.py (needs T007 + T008)
Task T010: Run tests green (needs T009)
```

**US2 (Phase 4)**:
```bash
# Run in parallel (different files):
Task T011: Write tests/integration/test_hybrid_mentor_api.py
Task T012: Create backend/agents/mentor_agent.py
# Then sequentially:
Task T013: Wire endpoint in hybrid.py (needs T011 + T012)
Task T014: Run tests green (needs T013)
```

**US3 (Phase 5)**: T015, T016, T017 can all run in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T006)
3. Complete Phase 3: User Story 1 (T007–T010)
4. **STOP and VALIDATE** — `POST /hybrid/assess` works end-to-end for premium users; 403 for free users
5. Demo if needed — full assessment feature is independently shippable

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready (server starts, `/hybrid/*` routes registered)
2. Phase 3 (US1) → Assessment endpoint live → Demo MVP
3. Phase 4 (US2) → Mentor endpoint live → Full Phase 2 feature set
4. Phase 5 (US3) → Architecture separation confirmed → Production-safe
5. Phase 6 → Polish and final validation → Submission-ready

### Parallel Team Strategy

With two developers after Phase 2 completes:
```
Developer A: Phase 3 (US1 — assessor_agent.py + /assess endpoint)
Developer B: Phase 4 (US2 — mentor_agent.py + /mentor endpoint)
→ Merge and run Phase 5 together
```

---

## Task Summary

| Phase | Tasks | Parallelizable | Story |
|---|---|---|---|
| Phase 1: Setup | T001–T002 | T002 [P] | — |
| Phase 2: Foundational | T003–T006 | T003, T004 [P] | — |
| Phase 3: US1 Assessment | T007–T010 | T007, T008 [P] | US1 |
| Phase 4: US2 Mentor | T011–T014 | T011, T012 [P] | US2 |
| Phase 5: US3 Tier Gate | T015–T017 | T015, T017 [P] | US3 |
| Phase 6: Polish | T018–T021 | T018, T019, T021 [P] | — |

**Total tasks**: 21  
**Parallelizable**: 10 tasks marked [P]  
**Test tasks**: T007, T010, T011, T014, T016, T019 (TDD red→green cycle enforced)

---

## Notes

- Never modify Phase 1 router files — any git diff against them is a build-blocker
- `backend/.env` must be in `.gitignore` before committing `GEMINI_API_KEY`
- `asyncio.to_thread()` is the correct wrapper for `Runner.run_sync()` in async FastAPI — do not call `Runner.run_sync()` directly in an async endpoint
- Mock `asyncio.to_thread` in tests, not the agent or runner directly — this tests the endpoint wiring correctly without hitting Gemini
- Progress summary pre-fetch in `_fetch_progress_summary()` must run BEFORE the agent is created — the closure captures the value at creation time
- `extract_json()` regex pattern: `re.sub(r"^` + "```" + r"(?:json)?\s*|\s*` + "```" + r"$", "", raw.strip(), flags=re.MULTILINE)`
