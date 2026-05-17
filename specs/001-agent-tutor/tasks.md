# Tasks: AgentTutor — AI Agent Learning Companion (Phase 1)

**Input**: Design documents from `/specs/001-agent-tutor/`
**Branch**: `001-agent-tutor`
**Date**: 2026-05-01
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/openapi.yaml ✅ | quickstart.md ✅

**Tests**: Included per Constitution Principle VII (TDD mandatory — tests written before implementation, Red-Green-Refactor enforced).

**Organization**: Tasks grouped by user story (US1–US6) matching spec.md priorities P1–P6.

## Format: `- [ ] [ID] [P?] [Story?] Description — file/path`

- **[P]**: Can run in parallel (different files, no conflicting dependencies)
- **[USN]**: Maps to User Story N from spec.md
- **Tests first**: Test tasks precede implementation tasks within each story (TDD)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create project skeleton, config files, and tooling. No business logic.

- [x] T001 Create full project folder structure per plan.md: `backend/` (routers/, models/, db/, storage/), `skills/`, `content/`, `chatgpt-app/`, `docs/`, `tests/` (unit/, integration/, contract/) with `__init__.py` in each Python package
- [x] T002 Create `backend/requirements.txt` listing all deps — fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg, boto3, pydantic[email], pytest, pytest-asyncio, httpx, python-dotenv, pyyaml (no openai, no anthropic)
- [x] T003 [P] Create `backend/.env.example` with all 8 required env vars: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL, DATABASE_URL, APP_ENV, ALLOWED_ORIGINS — each with inline description comment
- [x] T004 [P] Create `backend/Dockerfile` using `python:3.12-slim` base, installing requirements.txt, exposing port 8080, CMD `uvicorn backend.main:app --host 0.0.0.0 --port 8080 --workers 2`
- [x] T005 [P] Create `backend/fly.toml` with app name `agenttutor-backend`, port 8080, `[http_service]` block, `auto_stop_machines = false`

**Checkpoint**: Directory tree matches plan.md Project Structure exactly. `requirements.txt` contains no LLM packages.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on. No story can begin until this phase is complete.

**⚠️ CRITICAL**: Complete and verify T006–T013 before any Phase 3+ task.

- [x] T006 Create `backend/config.py` — `class Settings(BaseSettings)` loading all 8 env vars from `.env`; export singleton `settings = Settings()`
- [x] T007 Create `backend/db/connection.py` — async SQLAlchemy engine using `settings.DATABASE_URL`, `AsyncSession` factory, `get_db()` dependency, `create_all_tables()` coroutine for lifespan startup
- [x] T008 Create `backend/db/tables.py` — SQLAlchemy `Table` definitions for all 5 tables (users, chapters, progress, quiz_results, quiz_bank) exactly matching data-model.md migration SQL; include `Index` definitions
- [x] T009 Create `backend/db/seed.py` — async seeder with three functions: `seed_chapters()` inserts all 10 chapter rows from data-model.md chapter mapping; `seed_quiz_bank()` inserts 50 quiz questions (5 per chapter, placeholder content for dev); `load_search_text()` fetches each chapter from R2 and writes plaintext to `chapters.search_text`; CLI entry `python -m db.seed --create-tables --quiz-bank`
- [x] T010 Create `backend/storage/r2_client.py` — `boto3.client("s3", endpoint_url=...)` using settings; async `fetch_chapter_content(key: str) -> str` wrapping sync fetch with `asyncio.to_thread()`; raise `HTTPException(404)` on `ClientError` with `Code == "NoSuchKey"`
- [x] T011 Create `backend/main.py` — top-of-file comment `# Zero-Backend-LLM Architecture — No LLM calls permitted in this codebase.`; `FastAPI` app with lifespan calling `create_all_tables()`; `CORSMiddleware` from `settings.ALLOWED_ORIGINS`; register all 6 routers (chapters, quizzes, progress, search, access, users) with `/` prefix; health endpoint `GET /health -> {"status": "ok", "llm_calls": 0}`
- [x] T012 [P] Create `tests/conftest.py` — pytest fixtures: `async_engine` (test SQLite or test Postgres), `async_session` (transaction-rolled-back per test), `test_client` (httpx `AsyncClient` pointed at app), `free_user` (UUID user with tier="free"), `premium_user` (UUID user with tier="premium"), `sample_chapters` (3 free + 1 premium chapter rows), `sample_quiz_bank` (5 questions for chapter-01)
- [x] T013 Write `tests/unit/test_zero_llm_invariant.py` — three tests: (1) AST-scan all `.py` files under `backend/` asserting zero `import openai` / `from openai` nodes; (2) same for `anthropic`; (3) assert neither `openai` nor `anthropic` appears in `backend/requirements.txt`; this test MUST pass before any other test runs (mark with `pytest.mark.first` or place first in conftest order)

**Checkpoint**: `pytest tests/unit/test_zero_llm_invariant.py -v` — all 3 PASS. `GET /health` returns `{"status":"ok","llm_calls":0}`. All 5 DB tables exist after `seed.py --create-tables`.

---

## Phase 3: User Story 1 — Free Student Learns Chapter Content (Priority: P1) 🎯 MVP

**Goal**: Serve chapter content from R2 verbatim. Enforce freemium gate (chapters 1–3 free, 4–10 premium). User management (create/get). All access-denied cases return structured 403.

**Independent Test**: `pytest tests/integration/test_chapters_api.py tests/integration/test_users_api.py tests/unit/test_access_logic.py -v`

### Tests — User Story 1 (write first, verify they FAIL before T017)

- [x] T014 [P] [US1] Write `tests/unit/test_access_logic.py` — unit tests for `FREE_CHAPTERS` constant (assert chapter-01/02/03 in set, chapter-04 not in set); test access gate function for free user on free chapter (allowed), free user on premium chapter (denied), premium user on premium chapter (allowed)
- [x] T015 [P] [US1] Write `tests/integration/test_users_api.py` — async tests: `POST /users` creates new user (201, returns UUID); `POST /users` same email returns existing user (200); `GET /users/{id}` returns profile; `GET /users/nonexistent` returns 404
- [x] T016 [P] [US1] Write `tests/integration/test_chapters_api.py` — async tests: `GET /chapters?user_id=free` returns 10 chapters with `is_accessible=True` for 1–3 and `False` for 4–10; `GET /chapters/chapter-01/content?user_id=free` returns markdown content; `GET /chapters/chapter-04/content?user_id=free` returns 403 with `error="premium_required"`; `GET /chapters/chapter-04/content?user_id=premium` returns content; `GET /chapters/chapter-99/content?user_id=free` returns 404

### Implementation — User Story 1

- [x] T017 [P] [US1] Create `backend/models/user.py` — Pydantic v2 models: `UserCreate(email: EmailStr, name: str)`, `User(id: UUID, email, name, tier: Literal["free","premium"], streak_days: int, last_active: date | None, created_at: datetime)`
- [x] T018 [P] [US1] Create `backend/models/chapter.py` — `ChapterSummary(id, number, title, tier_required, is_accessible: bool)`, `ChapterContent(id, number, title, content: str, next_chapter, previous_chapter)`, `ChapterNavigation(id, number, title, tier_required, is_accessible) | None`
- [x] T019 [P] [US1] Create `backend/models/access.py` — `AccessCheck(user_id, chapter_id, allowed: bool, reason: Literal["free_chapter","premium_user","premium_required"], upgrade_message: str | None)`, `TierInfo(user_id, tier, free_chapters_count: int, total_chapters_accessible: int, locked_chapters_count: int)`
- [x] T020 [US1] Create `backend/routers/users.py` — `POST /users` upsert by email (INSERT … ON CONFLICT DO NOTHING, then SELECT); `GET /users/{user_id}` select by UUID; return 404 if not found; no LLM calls
- [x] T021 [US1] Create `backend/routers/chapters.py` — define `FREE_CHAPTERS = {"chapter-01","chapter-02","chapter-03"}`; `GET /chapters?user_id` lists all 10 with `is_accessible` flag; `GET /chapters/{chapter_id}/content?user_id` checks free gate then fetches from R2 via `fetch_chapter_content()`; return 403 `{"error":"premium_required","message":"..."}` for tier violation; register router in main.py

**Checkpoint US1**: All Phase 3 tests PASS. `GET /chapters/chapter-01/content` returns markdown. `GET /chapters/chapter-04/content` as free user returns 403. Zero LLM invariant still passes.

---

## Phase 4: User Story 2 — Student Takes a Chapter Quiz (Priority: P2)

**Goal**: Serve 5 MCQ questions per chapter (options only, no answers). Accept answer submissions and grade by stored answer key. Return score, pass/fail, wrong question numbers. Correct answers never sent to client.

**Independent Test**: `pytest tests/integration/test_quiz_api.py tests/unit/test_quiz_grading.py -v`

### Tests — User Story 2 (write first, verify they FAIL before T024)

- [x] T022 [P] [US2] Write `tests/unit/test_quiz_grading.py` — unit tests for `grade_quiz()`: all correct → score=5, passed=True, wrong=[]; 3 correct → score=3, passed=False, wrong=[q2,q4]; all wrong → score=0, passed=False, wrong=[1,2,3,4,5]; verify correct answers NOT in return dict; test `QUIZ_PASS_THRESHOLD = 4`; test score=4 is passing, score=3 is failing
- [x] T023 [P] [US2] Write `tests/integration/test_quiz_api.py` — async tests: `GET /quizzes/chapter-01/questions?user_id` returns 5 questions with options A–D but no `correct_answer` field; `POST /quizzes/chapter-01/submit` with all correct answers returns passed=True, wrong=[]; partial correct answers returns correct score and wrong list; `GET /quizzes/chapter-04/questions?user_id=free` returns 403; `POST /quizzes/chapter-01/submit` records result in quiz_results table

### Implementation — User Story 2

- [x] T024 [P] [US2] Create `backend/models/quiz.py` — `Question(question_number: int, question: str, options: dict[str,str])` (no correct_answer field), `QuizQuestions(chapter_id, chapter_title, total_questions, questions)`, `QuizSubmission(answers: dict[str, Literal["A","B","C","D"]])`, `QuizResult(chapter_id, score, total, percentage, passed, wrong_question_numbers: list[int])`
- [x] T025 [US2] Create `backend/routers/quizzes.py` — implement `grade_quiz(student_answers, correct_answers) -> dict` with `QUIZ_PASS_THRESHOLD = 4`; `GET /quizzes/{chapter_id}/questions?user_id` fetches from quiz_bank, strips correct_answer, enforces tier gate; `POST /quizzes/{chapter_id}/submit?user_id` fetches correct answers from quiz_bank, calls `grade_quiz()`, saves QuizResult row, returns `QuizResult` — correct answers never included in response
- [x] T026 [US2] Update `backend/db/seed.py` to insert complete quiz bank: 5 meaningful multiple-choice questions per chapter (50 total) covering the chapter topic — questions about AI Agents, Claude SDK, MCP, etc. matching chapter titles from data-model.md

**Checkpoint US2**: All Phase 4 tests PASS. Submitting all correct answers to chapter-01 quiz returns `passed=true`. Correct answers absent from all API responses. Free user gets 403 on chapter-04 quiz.

---

## Phase 5: User Story 3 — Student Tracks Learning Progress and Streaks (Priority: P3)

**Goal**: Record chapter completions. Update daily learning streak on each completion. Return full progress summary (chapters completed, quiz scores, streak, last active, completion %).

**Independent Test**: `pytest tests/integration/test_progress_api.py tests/unit/test_streak_calculation.py -v`

### Tests — User Story 3 (write first, verify they FAIL before T029)

- [x] T027 [P] [US3] Write `tests/unit/test_streak_calculation.py` — unit tests for `update_streak()`: first-time (last_active=None) → streak=1; same day → streak unchanged; consecutive day → streak+1; 2-day gap → streak=1; 30-day gap → streak=1; verify returns (streak_days, new_last_active) tuple
- [x] T028 [P] [US3] Write `tests/integration/test_progress_api.py` — async tests: `GET /progress/{user_id}` for new user returns 0 completions, streak=0; `POST /progress/{user_id}/chapters/chapter-01/complete` returns streak_days=1; second completion same day is idempotent (streak stays 1); `GET /progress/{user_id}` after 2 completions shows chapters_completed=2, completion_percentage > 0; `POST /progress` with premium chapter as free user returns 403

### Implementation — User Story 3

- [x] T029 [P] [US3] Create `backend/models/progress.py` — `ChapterProgressItem(chapter_id, chapter_title, completed: bool, completed_at: datetime | None, best_quiz_score: int | None)`, `ProgressSummary(user_id, chapters_completed, total_accessible_chapters, completion_percentage, streak_days, last_active, chapter_progress: list[ChapterProgressItem])`, `StreakUpdate(user_id, chapter_id, streak_days, chapters_completed, message: str)`
- [x] T030 [US3] Create `backend/routers/progress.py` — implement `update_streak(last_active, streak_days)` function per data-model.md logic; `GET /progress/{user_id}` fetches progress rows + best quiz scores per chapter, builds ProgressSummary; `POST /progress/{user_id}/chapters/{chapter_id}/complete` upserts progress row, calls `update_streak()`, updates users table, returns StreakUpdate with motivational message field (message string, NOT an LLM call — use hardcoded templates like "Great work! 🔥 {streak} day streak!")

**Checkpoint US3**: All Phase 5 tests PASS. Completing chapter-01 then chapter-02 on consecutive days results in streak=2. Progress summary shows correct completion count and percentage.

---

## Phase 6: User Story 4 — Student Navigates Sequentially (Priority: P4)

**Goal**: Return next/previous chapter metadata including accessibility flag for the requesting user. Signal "no previous" for chapter-01 and "course complete" for chapter-10.

**Independent Test**: `pytest tests/integration/test_chapters_api.py -k "navigation" -v`

### Tests — User Story 4 (write first, verify they FAIL before T032)

- [x] T031 [P] [US4] Add navigation tests to `tests/integration/test_chapters_api.py` — `GET /chapters/chapter-03/next?user_id=free` returns chapter-04 metadata with `is_accessible=False`; `GET /chapters/chapter-01/previous?user_id=free` returns `null` (first chapter); `GET /chapters/chapter-10/next?user_id=premium` returns `null` (last chapter); `GET /chapters/chapter-05/next?user_id=premium` returns chapter-06 with `is_accessible=True`; verify `ChapterNavigation` schema matches openapi.yaml

### Implementation — User Story 4

- [x] T032 [US4] Add navigation endpoints to `backend/routers/chapters.py` — `GET /chapters/{chapter_id}/next?user_id` queries chapters table for `number = current_number + 1`, sets `is_accessible` based on user tier, returns `ChapterNavigation` or `null`; `GET /chapters/{chapter_id}/previous?user_id` queries for `number = current_number - 1`, returns `ChapterNavigation` or `null`

**Checkpoint US4**: All navigation tests PASS. Free user on chapter-03 gets chapter-04 next-link with `is_accessible=false`. Chapter-01 previous returns null.

---

## Phase 7: User Story 5 — Student Searches for a Topic (Priority: P5)

**Goal**: Keyword search across chapter `search_text` in DB. Results scoped to user's accessible tiers. Return matching excerpts (300 chars) with chapter title and number. Empty array for no matches (not an error).

**Independent Test**: `pytest tests/integration/test_search_api.py -v`

### Tests — User Story 5 (write first, verify they FAIL before T034)

- [x] T033 [P] [US5] Write `tests/integration/test_search_api.py` — async tests: `GET /search?user_id=free&q=agent` returns results only from chapters 1–3; `GET /search?user_id=premium&q=A2A` returns results including premium chapters; `GET /search?user_id=free&q=zzznomatch999` returns `{"query":"...","results":[],"total":0}` not an error; each result has `chapter_id`, `chapter_title`, `chapter_number`, `excerpt`; `GET /search` without `q` param returns 422; `q` shorter than 2 chars returns 422

### Implementation — User Story 5

- [x] T034 [P] [US5] Create `backend/models/search.py` — `SearchResult(chapter_id, chapter_title, chapter_number, excerpt)`, `SearchResponse(query: str, results: list[SearchResult], total: int)`
- [x] T035 [US5] Create `backend/routers/search.py` — `GET /search?user_id&q&limit=10`; determine allowed tiers based on user tier (free → ["free"], premium → ["free","premium"]); SQL query: `SELECT id, title, number, SUBSTRING(search_text, ...) AS excerpt FROM chapters WHERE tier_required = ANY(:tiers) AND LOWER(search_text) LIKE LOWER(:pattern) ORDER BY number LIMIT :limit`; return `SearchResponse`; enforce `len(q) >= 2` validation

**Checkpoint US5**: All search tests PASS. Free user search returns only free chapters. Premium user sees all chapters. Empty results return empty array.

---

## Phase 8: User Story 6 — Freemium Gate Access Endpoints (Priority: P6)

**Goal**: Dedicated endpoints for access check (returns structured allow/deny with upgrade_message) and tier info (counts of accessible vs locked chapters). Freemium gate logic already exists in chapters router — these endpoints expose it explicitly for ChatGPT to query.

**Independent Test**: `pytest tests/integration/test_access_api.py -v`

### Tests — User Story 6 (write first, verify they FAIL before T037)

- [x] T036 [P] [US6] Write `tests/integration/test_access_api.py` — async tests: `GET /access/check?user_id=free&chapter_id=chapter-01` returns `allowed=True, reason="free_chapter"`; `GET /access/check?user_id=free&chapter_id=chapter-04` returns `allowed=False, reason="premium_required", upgrade_message != null`; `GET /access/check?user_id=premium&chapter_id=chapter-04` returns `allowed=True, reason="premium_user"`; `GET /access/{user_id}/tier` for free user returns `tier="free", total_chapters_accessible=3, locked_chapters_count=7`; `GET /access/{user_id}/tier` for premium user returns `total_chapters_accessible=10, locked_chapters_count=0`

### Implementation — User Story 6

- [x] T037 [US6] Create `backend/routers/access.py` — `GET /access/check?user_id&chapter_id` uses `FREE_CHAPTERS` constant and DB tier check (import from chapters router); returns `AccessCheck` with `upgrade_message` only when `allowed=False`; `GET /access/{user_id}/tier` queries chapters table counts by `tier_required` and user tier, returns `TierInfo`; hardcoded upgrade_message: "Upgrade to Premium to unlock chapters 4–10 and the full quiz bank."

**Checkpoint US6**: All access tests PASS. Free user on chapter-04 gets `allowed=false` with non-null upgrade message. Premium user on chapter-04 gets `allowed=true`.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: SKILL.md files, ChatGPT App manifest, sample content, documentation, contract tests, end-to-end validation.

- [x] T038 Write `tests/contract/test_api_contracts.py` — load `specs/001-agent-tutor/contracts/openapi.yaml`; for each endpoint, make a real HTTP call to the test client and assert response schema matches the OpenAPI contract using `jsonschema.validate()`; cover all 16 endpoints
- [x] T039 [P] Create `skills/concept-explainer/SKILL.md` — metadata (name, version, trigger keywords: "explain","what is","how does"); purpose (explain AI Agent concepts using only content from backend); workflow (fetch chapter, extract relevant section, explain at student's level); response templates (definition template, analogy template, step-by-step template); key principles (only use fetched content, never invent facts, ask which chapter when ambiguous)
- [x] T040 [P] Create `skills/quiz-master/SKILL.md` — metadata (trigger: "quiz","test me","practice"); purpose (guide students through 5 questions one at a time); workflow (fetch questions from `/quizzes/{chapter_id}/questions`, present Q1, wait for answer, call `/quizzes/{chapter_id}/submit` after all 5, deliver results); response templates (question presentation, encouragement, score reveal); key principles (one question at a time, wait for each answer, celebrate passes, encourage retries on fail)
- [x] T041 [P] Create `skills/socratic-tutor/SKILL.md` — metadata (trigger: "help me think","I'm stuck","I don't understand"); purpose (guide discovery through questions, never give direct answers); workflow (identify the concept student is stuck on, ask a narrowing question, respond to student's answer with a follow-up that leads closer to the insight, reveal answer only if student gives up after 3 attempts); response templates (opening question, follow-up question, hint after wrong direction, final reveal); key principles (never state the answer in first 2 turns, use analogies from chapter content, celebrate the "aha moment")
- [x] T042 [P] Create `skills/progress-motivator/SKILL.md` — metadata (trigger: "my progress","streak","how am I doing","completed"); purpose (celebrate achievements and maintain learning momentum); workflow (fetch `/progress/{user_id}`, interpret streak and completion data, generate encouraging message calibrated to progress level); response templates (first chapter celebration, streak milestone at 3/7/30 days, completion celebration, gentle nudge for zero streak); key principles (always accurate to actual data, specific numbers in celebration, suggest next chapter as call-to-action)
- [x] T043 [P] Create `chatgpt-app/manifest.yaml` — OpenAI App manifest with `schema_version: v1`, `name_for_human: AgentTutor`, `description_for_human`, `description_for_model` (instructs ChatGPT to use SKILL.md files, never call LLMs itself, only use content from backend), `api` block pointing to deployed backend URL with OpenAPI spec path, `auth: {type: none}` for Phase 1
- [x] T044 [P] Create sample chapter content: `content/chapter-01.md` ("What is an AI Agent" — 500+ word markdown with sections on definition, components, examples), `content/chapter-02.md` ("Claude Agent SDK Basics"), `content/chapter-03.md` ("Building Your First Agent") — all with proper markdown headings, code examples, and quiz-relevant content that the seed quiz questions reference
- [x] T045 [P] Create `docs/architecture.md` — text description of the Zero-Backend-LLM architecture with ASCII diagram (User → ChatGPT App → Backend → R2/PostgreSQL), component responsibilities, Phase 1 data flow
- [x] T046 [P] Create `docs/cost-analysis.md` — Phase 1 cost table: Fly.io ~$4/mo, Neon free tier $0, R2 ~$5/mo at 10K users, domain $1/mo; total ~$10/mo at 10K users = $0.001/user/month (well within $0.004 budget); ChatGPT cost = $0 to developer; comparison table vs human tutor
- [x] T047 Run full test suite from repo root: `pytest tests/ -v --tb=short --cov=backend --cov-report=term` and fix any failures until all tests PASS; target coverage ≥ 80% for backend/
- [x] T048 Validate `quickstart.md` end-to-end on clean Python 3.12 environment: follow all 12 steps, verify `GET /health` returns ok, smoke test all 6 feature areas, confirm zero-LLM invariant test still passes

**Final Checkpoint**: `pytest tests/ -v` — all tests PASS. Zero-LLM invariant confirmed. All 16 OpenAPI contract tests PASS. All 4 SKILL.md files complete. `GET /health` → `{"status":"ok","llm_calls":0}`.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────► Start immediately
       │
       ▼
Phase 2 (Foundational) ───────────────────────────────► Blocks ALL user stories
       │
       ├──► Phase 3 (US1: Content + Access Gate) ────► P1 — start here
       │           │
       │           ▼ (US1 complete unlocks these)
       ├──► Phase 4 (US2: Quiz System) ─────────────► P2
       ├──► Phase 5 (US3: Progress + Streaks) ───────► P3
       ├──► Phase 6 (US4: Navigation) ──────────────► P4
       ├──► Phase 7 (US5: Search) ───────────────────► P5
       └──► Phase 8 (US6: Access Endpoints) ─────────► P6
                   │
                   ▼
       Phase 9 (Polish) ─────────────────────────────► After all stories done
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|---|---|---|
| US1 (P1) — Content + Gate | Foundation complete | T013 ✅ |
| US2 (P2) — Quiz | Foundation complete | T013 ✅ (quiz_bank seeded in T009) |
| US3 (P3) — Progress | Foundation + US1 (users exist) | T021 ✅ |
| US4 (P4) — Navigation | Foundation + US1 (chapters router) | T021 ✅ |
| US5 (P5) — Search | Foundation + chapters.search_text seeded | T009 ✅ |
| US6 (P6) — Access Endpoints | Foundation + US1 (FREE_CHAPTERS logic) | T021 ✅ |

### Within Each User Story

1. **Write tests** (all [P] test tasks launch in parallel) → Verify they FAIL
2. **Create models** ([P] model tasks launch in parallel)
3. **Implement router** (depends on models)
4. **Run tests** → Verify they PASS

### Parallel Opportunities per Story

**US1 parallel launch** (after T013):
```
T014 (unit tests)  T015 (user tests)  T016 (chapter tests)  T017 (user model)
T018 (chapter model)  T019 (access model)
→ then: T020 (users router) || T021 (chapters router — after models)
```

**US2 parallel launch** (after T013):
```
T022 (quiz unit tests)  T023 (quiz integration tests)  T024 (quiz models)
→ then: T025 (quiz router)  T026 (seed quiz content)
```

**US3–US6 parallel launch** (each after their own tests + models):
```
Phase 5: T027 || T028 || T029 → T030
Phase 6: T031 → T032
Phase 7: T033 || T034 → T035
Phase 8: T036 → T037
```

**Phase 9 parallel launch** (all SKILL.md and docs):
```
T039 || T040 || T041 || T042 || T043 || T044 || T045 || T046
→ then: T038 (contract tests) → T047 (full suite) → T048 (quickstart validation)
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundation)
2. Complete Phase 3 (US1: Content Delivery + User Management + Access Gate)
3. **STOP and VALIDATE**: Can a free user read chapter 1? Does chapter-04 return 403?
4. Zero-LLM invariant passes? → **Demo-ready MVP**

### Incremental Delivery

```
Foundation ──► US1 (MVP) ──► US2 (Quizzes) ──► US3 (Progress) ──► US4+US5+US6 ──► Polish
Each step is independently deployable and demonstrable.
```

### Parallel Team Strategy

Once Foundation (Phase 2) is done:
- **Developer A**: US1 + US4 (Content + Navigation — same router file)
- **Developer B**: US2 (Quiz system)
- **Developer C**: US3 + US6 (Progress + Access endpoints)
- **Developer D**: US5 + Phase 9 Skills (Search + SKILL.md files)

---

## Task Count Summary

| Phase | Tasks | Notes |
|---|---|---|
| Phase 1: Setup | T001–T005 (5) | Create project skeleton |
| Phase 2: Foundation | T006–T013 (8) | DB, R2, main.py, zero-LLM test |
| Phase 3: US1 Content | T014–T021 (8) | 3 test tasks + 5 impl tasks |
| Phase 4: US2 Quiz | T022–T026 (5) | 2 test tasks + 3 impl tasks |
| Phase 5: US3 Progress | T027–T030 (4) | 2 test tasks + 2 impl tasks |
| Phase 6: US4 Navigation | T031–T032 (2) | 1 test task + 1 impl task |
| Phase 7: US5 Search | T033–T035 (3) | 1 test task + 2 impl tasks |
| Phase 8: US6 Access | T036–T037 (2) | 1 test task + 1 impl task |
| Phase 9: Polish | T038–T048 (11) | Skills, manifest, docs, validation |
| **TOTAL** | **48 tasks** | |

---

## Notes

- **[P] tasks** = different files, safe to run in parallel (no write conflicts)
- **[USN] label** maps each task to its user story for traceability
- **TDD enforced**: All test tasks precede implementation tasks within each story
- **Zero-LLM gate** (T013) must pass before any other test; re-run after each phase
- Commit after each checkpoint; PR gate checks zero-LLM invariant
- Stop at any checkpoint to demo the current increment independently
- Do NOT move to Phase 9 Polish until all US1–US6 checkpoints pass
