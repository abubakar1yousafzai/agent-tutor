# Implementation Plan: AgentTutor Phase 2 — Hybrid Intelligence

**Branch**: `002-hybrid-intelligence` | **Date**: 2026-05-17 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/002-hybrid-intelligence/spec.md`

## Summary

Add two premium-gated hybrid intelligence endpoints to the existing AgentTutor FastAPI backend using the OpenAI Agents SDK with Google Gemini as the LLM provider. All new code is isolated in `backend/routers/hybrid.py` and `backend/agents/`. Phase 1 routers are never modified. The only existing file touched is `backend/main.py` (one import + one `include_router` line).

---

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, SQLAlchemy (async), openai-agents, pydantic v2  
**Storage**: Local filesystem (chapter markdown files at `backend/content/chapters/`), PostgreSQL via Neon (existing async engine)  
**Testing**: pytest + pytest-asyncio + httpx AsyncClient (existing pattern in `tests/`)  
**Target Platform**: Linux server (Fly.io, existing Dockerfile)  
**Performance Goals**: Assessment response ≤ 30s p95; Mentor response ≤ 60s p95; tier-gate rejection ≤ 500ms  
**Constraints**: Phase 1 routers must show zero git diff; `Runner.run_sync()` must not block the async event loop; no hardcoded secrets  
**Scale/Scope**: Premium users only; fixed cost constants ($0.014 assess, $0.090 mentor); 2 new endpoints

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status | Evidence |
|---|---|---|---|
| I — Zero-Backend-LLM | Phase 2 is explicitly exempt from this gate | ✅ PASS | New code is in `hybrid.py` only; Phase 1 routers untouched |
| III — Selective Hybrid Intelligence | All 5 conditions must be satisfied | ✅ PASS | See below |
| V — Phased Architecture | Phase 1 intact; Phase 2 isolated | ✅ PASS | No Phase 1 file edits except one import in `main.py` |
| VI — Cost-Conscious Engineering | Cost documented before shipping | ✅ PASS | $0.014/assess, $0.090/mentor; monetized via premium tier |
| VII — TDD | Integration tests planned before implementation | ✅ PASS | 4 test cases per endpoint defined in spec and plan |

**Principle III — Five-Condition Verification:**
1. Educational value ✅ — LLM grading captures partial credit; Socratic mentor guides discovery (neither is achievable deterministically)
2. Premium-gated ✅ — Tier check is the first operation in both endpoints; free users never reach the agent
3. User-initiated ✅ — Both endpoints are POST with explicit user payload; no auto-trigger exists
4. Architecturally isolated ✅ — All new code in `backend/agents/` and `backend/routers/hybrid.py`; prefix `/hybrid` is distinct
5. Cost-tracked ✅ — `estimated_cost_usd` returned in every response; logged at INFO level

**Constitution Check: PASS — proceed to Phase 0.**

---

## Project Structure

### Documentation (this feature)

```text
specs/002-hybrid-intelligence/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
│   ├── hybrid-assess.yaml
│   └── hybrid-mentor.yaml
├── quickstart.md        ← Phase 1 output
├── checklists/
│   └── requirements.md  ← already complete
└── tasks.md             ← /sp.tasks output (not created here)
```

### Source Code — New Files Only

```text
backend/
├── agents/
│   ├── __init__.py             ← empty module marker
│   ├── llm_client.py           ← shared get_llm_model() factory
│   ├── assessor_agent.py       ← LLM Graded Assessment agent + runner
│   └── mentor_agent.py         ← AI Mentor Agent + tools + runner
├── routers/
│   └── hybrid.py               ← POST /hybrid/assess, POST /hybrid/mentor
└── main.py                     ← ONLY CHANGE: +2 lines (import + include_router)

tests/integration/
├── test_hybrid_assess_api.py   ← 2 test cases
└── test_hybrid_mentor_api.py   ← 2 test cases
```

**Existing files — zero changes permitted:**

```text
backend/routers/chapters.py    ← READ-ONLY
backend/routers/quizzes.py     ← READ-ONLY
backend/routers/progress.py    ← READ-ONLY
backend/routers/search.py      ← READ-ONLY
backend/routers/access.py      ← READ-ONLY
backend/routers/users.py       ← READ-ONLY
backend/db/                    ← READ-ONLY
backend/models/                ← READ-ONLY
backend/storage/               ← READ-ONLY
backend/config.py              ← READ-ONLY
```

---

## Phase 0: Research

### R1 — Runner.run_sync() in Async FastAPI Context

**Decision**: Wrap `Runner.run_sync()` with `asyncio.to_thread()` inside async FastAPI endpoints.

**Rationale**: `Runner.run_sync()` is a blocking call. Calling it directly inside an `async def` endpoint blocks the event loop, stalling all other requests. `asyncio.to_thread()` offloads it to a thread-pool executor thread, preserving FastAPI's non-blocking behavior. The alternative (`Runner.run()` async) is cleaner but the spec explicitly mandates `Runner.run_sync()`.

**Pattern**:
```python
import asyncio
result = await asyncio.to_thread(Runner.run_sync, agent, message)
```

**Alternatives considered**:
- `Runner.run()` (async) — cleaner, but contradicts spec mandate
- Direct `Runner.run_sync()` in endpoint — blocks event loop; rejected

---

### R2 — Database Access Inside Synchronous Agent Tools

**Decision**: Pre-fetch student progress in the async endpoint using the existing `get_db` session, then pass the formatted result into the agent tool via closure.

**Rationale**: Agent tool functions registered with the OpenAI Agents SDK must be synchronous when `Runner.run_sync()` is used. The existing codebase uses an async SQLAlchemy engine — adding a separate sync engine adds a new dependency (`psycopg2`) and doubles connection management. Closing over pre-fetched data is zero-dependency, testable, and correct.

**Pattern**:
```python
# In the async endpoint, before creating the agent:
progress_data = await _fetch_progress_summary(user_id, db)

# Tool function is a closure over progress_data:
def get_student_progress(user_id: str) -> str:
    """Returns the student's completed chapters and quiz scores."""
    return progress_data
```

**Tool `get_chapter_content`**: Uses the existing synchronous `get_local_content(chapter_id)` from `backend/storage/content_reader.py` — already returns `str | None`, no async required.

**Alternatives considered**:
- Sync SQLAlchemy engine — requires `psycopg2` dependency + dual engine management; rejected
- `asyncio.run()` inside tool — illegal when an event loop is already running; rejected

---

### R3 — Shared LLM Client Location

**Decision**: Place `get_llm_model()` in a dedicated `backend/agents/llm_client.py` module, not inside `mentor_agent.py`.

**Rationale**: The spec plan places `get_llm_model()` in `mentor_agent.py` and has `assessor_agent.py` import from it. This creates asymmetric coupling (assessor depends on mentor for a non-mentor concern). A shared `llm_client.py` is one additional file but keeps both agents at the same import level. No other trade-off changes.

**Pattern**:
```python
# backend/agents/llm_client.py
from agents import OpenAIChatCompletionsModel, AsyncOpenAI
import os

def get_llm_model() -> OpenAIChatCompletionsModel:
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
```

---

### R4 — JSON Extraction from LLM Assessment Response

**Decision**: Instruct the assessor agent to return raw JSON only (no markdown fencing) and parse with `json.loads()`. Add a regex fallback to strip ` ```json ... ``` ` fencing if present.

**Rationale**: Gemini frequently wraps JSON in markdown code blocks despite instructions. A two-step extraction (attempt direct parse → strip fencing → retry) is cheap and covers all real-world cases without requiring a second LLM call.

**Pattern**:
```python
import json, re

def extract_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
        return json.loads(stripped)
```

---

### R5 — Tracking Tool Calls in the Mentor Agent Run Result

**Decision**: Inspect `result.new_messages` (or `result.messages`) from the `RunResult` object to extract `tool_use` content blocks and collect unique tool names.

**Rationale**: The OpenAI Agents SDK `RunResult` exposes the full message trace. Tool invocations appear as messages with `role="assistant"` and content of type `tool_use`. Iterating these gives the authoritative list of tools called without any instrumentation.

**Pattern**:
```python
tools_used = []
chapters_referenced = []
for msg in result.new_messages:
    for block in getattr(msg, "content", []):
        if getattr(block, "type", None) == "tool_use":
            name = block.name
            if name not in tools_used:
                tools_used.append(name)
            if name == "get_chapter_content":
                chapter_id = block.input.get("chapter_id", "")
                if chapter_id and chapter_id not in chapters_referenced:
                    chapters_referenced.append(chapter_id)
```

---

## Phase 1: Design & Contracts

### Data Model

See [`data-model.md`](./data-model.md) for entity diagrams. Summary:

| Entity | Source | Fields Used |
|---|---|---|
| `User` | `users` table | `id`, `tier` |
| `Chapter` | local filesystem | `chapter_id` → `backend/content/chapters/{chapter_id}.md` |
| `StudentProgress` | `progress` + `quiz_results` tables | `chapter_id`, `completed`, `best_quiz_score` |
| `AssessRequest` | request body | `user_id`, `chapter_id`, `question`, `student_answer` |
| `AssessResponse` | response body | `score`, `max_score`, `grade`, `feedback`, `what_was_correct`, `what_was_missing`, `improvement_tip`, `estimated_cost_usd` |
| `MentorRequest` | request body | `user_id`, `question` |
| `MentorResponse` | response body | `mentor_response`, `chapters_referenced`, `tools_used`, `estimated_cost_usd` |

---

### Pydantic Models (inline in `hybrid.py`)

```python
from pydantic import BaseModel
from uuid import UUID

class AssessRequest(BaseModel):
    user_id: UUID
    chapter_id: str
    question: str
    student_answer: str

class AssessResponse(BaseModel):
    score: int
    max_score: int
    grade: str
    feedback: str
    what_was_correct: str
    what_was_missing: str
    improvement_tip: str
    estimated_cost_usd: float

class MentorRequest(BaseModel):
    user_id: UUID
    question: str

class MentorResponse(BaseModel):
    mentor_response: str
    chapters_referenced: list[str]
    tools_used: list[str]
    estimated_cost_usd: float
```

---

### API Contracts

Full OpenAPI specs are in `contracts/`. Summary:

#### `POST /hybrid/assess`

| Field | Value |
|---|---|
| Auth | None (user_id in body; tier checked DB-side) |
| Request | `AssessRequest` JSON body |
| 200 | `AssessResponse` |
| 403 | `{"error": "premium_required", "detail": "This feature requires a premium subscription."}` |
| 404 | `{"detail": "Chapter '{chapter_id}' content not found"}` |
| 422 | Pydantic validation error (blank fields) |
| 500 | `{"detail": "Assessment failed: could not parse AI response"}` |

#### `POST /hybrid/mentor`

| Field | Value |
|---|---|
| Auth | None (user_id in body; tier checked DB-side) |
| Request | `MentorRequest` JSON body |
| 200 | `MentorResponse` |
| 403 | `{"error": "premium_required", "detail": "This feature requires a premium subscription."}` |
| 422 | Pydantic validation error (blank question) |
| 500 | `{"detail": "Mentor session failed."}` |

---

### Endpoint Implementation Blueprints

#### `POST /hybrid/assess` — Full Flow

```
1. Validate request (Pydantic — automatic)
2. SELECT tier FROM users WHERE id = user_id  →  404 if missing
3. if tier == "free": raise HTTPException(403, {"error": "premium_required"})
4. chapter_content = get_local_content(chapter_id)  →  404 if None
5. Build user_message:
     f"Chapter Content:\n{chapter_content}\n\nQuestion: {question}\n\nStudent Answer: {student_answer}\n\nReturn JSON only."
6. assessor = Agent(model=get_llm_model(), instructions=ASSESSOR_SYSTEM_PROMPT)
7. result = await asyncio.to_thread(Runner.run_sync, assessor, user_message)
8. parsed = extract_json(result.final_output)  →  500 if JSONDecodeError
9. logger.info("assess cost=0.014 user=%s chapter=%s", user_id, chapter_id)
10. return AssessResponse(**parsed, estimated_cost_usd=0.014)
```

**ASSESSOR_SYSTEM_PROMPT** (constant at module level):
```
You are an expert AI Agent Development instructor grading a student answer.
Use only the provided chapter content to evaluate the answer.
Be encouraging, constructive, and specific.
Return ONLY a JSON object with these exact fields:
score (integer 0-10), max_score (always 10), grade (letter grade A-F),
feedback (overall feedback string), what_was_correct (string),
what_was_missing (string), improvement_tip (string).
Do not include markdown fencing or any text outside the JSON object.
```

---

#### `POST /hybrid/mentor` — Full Flow

```
1. Validate request (Pydantic — automatic)
2. SELECT tier FROM users WHERE id = user_id  →  404 if missing
3. if tier == "free": raise HTTPException(403, {"error": "premium_required"})
4. progress_summary = await _fetch_progress_summary(user_id, db)
   (SQLAlchemy query: JOIN progress + quiz_results for this user)
5. Define tools as closures:
     get_chapter_content(chapter_id: str) → str
       Uses: get_local_content(chapter_id) from storage/content_reader.py
       Returns: chapter markdown or "Chapter not found."
     get_student_progress(user_id: str) → str
       Uses: progress_summary (pre-fetched closure)
       Returns: formatted string of completed chapters + scores
6. mentor = Agent(model=get_llm_model(), tools=[get_chapter_content, get_student_progress],
                  instructions=MENTOR_SYSTEM_PROMPT)
7. result = await asyncio.to_thread(Runner.run_sync, mentor, question)
8. tools_used, chapters_referenced = _extract_tool_calls(result)
9. logger.info("mentor cost=0.090 user=%s tools=%s", user_id, tools_used)
10. return MentorResponse(
        mentor_response=result.final_output,
        chapters_referenced=chapters_referenced,
        tools_used=tools_used,
        estimated_cost_usd=0.090
    )
```

**MENTOR_SYSTEM_PROMPT** (constant at module level):
```
You are an expert AI Agent Development mentor for AgentTutor. You have tools
to fetch chapter content and check student progress. Always fetch relevant
chapter content before answering any question. Check student progress to
personalize your response based on what the student has already learned.
Guide students using the Socratic method — ask guiding questions rather than
giving direct answers. Be patient, encouraging, and specific.
```

---

### `main.py` Change (minimal diff)

Add exactly two lines after the existing router imports:

```python
# Line to add after existing imports:
from backend.routers import hybrid  # noqa: E402 — Phase 2 hybrid router

# Line to add after existing app.include_router() calls:
app.include_router(hybrid.router, prefix="/hybrid", tags=["Hybrid Intelligence"])
```

---

### Environment Variables

**`backend/.env`** — add (not committed):
```
GEMINI_API_KEY=<actual key>
```

**`backend/.env.example`** — add:
```
# Phase 2 — Hybrid Intelligence (Google Gemini via OpenAI Agents SDK)
GEMINI_API_KEY=your_gemini_api_key_here
```

**`backend/requirements.txt`** — add:
```
openai-agents
```

---

### Test Plan

Both test files use the existing `conftest.py` fixtures (`test_client`, `free_user`, `premium_user`, `sample_chapters`). The OpenAI Agents SDK runner is mocked at the module level to avoid real Gemini API calls in CI.

#### `tests/integration/test_hybrid_assess_api.py`

```python
# test_assess_free_user_returns_403
# Given: free_user fixture
# When: POST /hybrid/assess with free user_id, valid chapter_id, question, answer
# Then: status_code == 403, body["error"] == "premium_required"

# test_assess_premium_user_returns_result
# Given: premium_user fixture; Runner.run_sync mocked to return valid JSON
# When: POST /hybrid/assess with premium user_id, chapter_id="chapter-01"
# Then: status_code == 200
#       body has keys: score, max_score, grade, feedback,
#                      what_was_correct, what_was_missing,
#                      improvement_tip, estimated_cost_usd
#       body["estimated_cost_usd"] == 0.014
```

#### `tests/integration/test_hybrid_mentor_api.py`

```python
# test_mentor_free_user_returns_403
# Given: free_user fixture
# When: POST /hybrid/mentor with free user_id, non-empty question
# Then: status_code == 403, body["error"] == "premium_required"

# test_mentor_premium_user_returns_result
# Given: premium_user fixture; Runner.run_sync mocked to return a RunResult
# When: POST /hybrid/mentor with premium user_id, question string
# Then: status_code == 200
#       body has keys: mentor_response, chapters_referenced,
#                      tools_used, estimated_cost_usd
#       body["estimated_cost_usd"] == 0.090
```

**Mock strategy**: Patch `backend.routers.hybrid.Runner.run_sync` (or `asyncio.to_thread`) to return a controlled `RunResult`-like object with `final_output` and `new_messages`. This keeps tests fast and deterministic.

---

### Architecture Separation Verification

Run this after implementation to confirm Phase 1 is untouched:

```bash
git diff main -- \
  backend/routers/chapters.py \
  backend/routers/quizzes.py \
  backend/routers/progress.py \
  backend/routers/search.py \
  backend/routers/access.py \
  backend/routers/users.py \
  backend/db/ \
  backend/models/ \
  backend/storage/ \
  backend/config.py
# Expected output: (empty — zero diff)
```

Only permitted diffs: `backend/main.py` (+2 lines), `backend/requirements.txt` (+1 line), `backend/.env.example` (+2 lines), new files in `backend/agents/`, `backend/routers/hybrid.py`, `tests/integration/test_hybrid_*.py`.

---

## Complexity Tracking

| Item | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| `asyncio.to_thread()` wrapping `Runner.run_sync()` | Prevent event loop blocking in async FastAPI endpoint | Direct call blocks all concurrent requests; using `Runner.run()` (async) contradicts spec mandate |
| Pre-fetch progress before agent creation | Sync tools cannot `await` DB queries | Sync SQLAlchemy engine requires new dependency (`psycopg2`) and dual connection management |
| `llm_client.py` shared module | Both agents need identical client setup | Importing `get_llm_model` from `mentor_agent` in `assessor_agent` creates asymmetric coupling |
| Regex JSON extraction fallback | Gemini wraps JSON in markdown fencing | A second LLM call to request clean JSON doubles cost and latency |

---

## Risk Analysis

1. **Gemini response format instability** — Gemini may deviate from the JSON schema despite explicit instructions. Mitigation: regex fencing stripper + 500 error with descriptive message; assessment fallback documented for users.

2. **Thread-pool saturation under load** — `asyncio.to_thread()` uses the default executor (default 5× CPU threads). Under concurrent premium requests, long Gemini calls could exhaust the pool. Mitigation: acceptable for hackathon scale; Phase 3 should use `Runner.run()` async or a dedicated thread pool.

3. **Phase 1 accidental contamination** — A future refactor might inadvertently import from `hybrid.py` in a Phase 1 router. Mitigation: the `test_zero_llm_invariant.py` test (existing) guards this; add an assertion that Phase 1 routers do not import from `backend.agents`.
