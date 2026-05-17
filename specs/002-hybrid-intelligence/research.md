# Research: AgentTutor Phase 2 — Hybrid Intelligence

**Feature**: 002-hybrid-intelligence | **Date**: 2026-05-17 | **Status**: Complete

All NEEDS CLARIFICATION items resolved. No open questions remain before implementation.

---

## R1 — Runner.run_sync() in Async FastAPI Context

- **Decision**: `await asyncio.to_thread(Runner.run_sync, agent, message)`
- **Rationale**: Offloads the blocking call to a thread-pool executor, preserving FastAPI's async event loop. Zero new dependencies.
- **Alternatives considered**: `Runner.run()` async (cleaner but contradicts spec mandate); direct call (blocks event loop — rejected).

## R2 — Database Access Inside Synchronous Agent Tools

- **Decision**: Pre-fetch student progress in the async FastAPI endpoint using the existing `get_db` session; pass as a string closure into the sync tool function.
- **Rationale**: Agent tools called by `Runner.run_sync()` cannot `await`. Pre-fetching before agent creation avoids a sync DB engine dependency.
- **Alternatives considered**: Sync SQLAlchemy engine (requires `psycopg2`; dual engine); `asyncio.run()` inside tool (illegal when event loop already running).

## R3 — Shared LLM Client Location

- **Decision**: `backend/agents/llm_client.py` with a single `get_llm_model()` factory function imported by both agents.
- **Rationale**: Placing it in `mentor_agent.py` (as originally planned) causes `assessor_agent.py` to import a non-assessor module for a shared concern — asymmetric coupling. One additional file eliminates this.
- **Alternatives considered**: In `mentor_agent.py` (causes cross-module coupling); inline in both agents (duplicates client init code).

## R4 — JSON Extraction from LLM Assessment Response

- **Decision**: Attempt `json.loads(raw)` first; on failure, strip markdown fencing with regex, then retry.
- **Rationale**: Gemini reliably wraps JSON in ` ```json ... ``` ` even when instructed not to. Two-attempt extraction with zero LLM calls handles all real-world cases.
- **Alternatives considered**: Second LLM call for reformatting (doubles cost + latency); accept only raw JSON (too fragile in production).

## R5 — Tracking Tool Calls in Mentor RunResult

- **Decision**: Iterate `result.new_messages`, filter for assistant messages with `tool_use` content blocks, collect `block.name` and `block.input["chapter_id"]`.
- **Rationale**: `RunResult.new_messages` is the canonical source of the agent's message trace in the OpenAI Agents SDK. No instrumentation or monkey-patching needed.
- **Alternatives considered**: Wrapping tools with decorators to record calls (adds indirection); using `result.raw_responses` (lower-level, less stable API).

## R6 — Test Mocking Strategy

- **Decision**: Patch `asyncio.to_thread` in tests to call the wrapped function synchronously with a controlled return value (a `MagicMock` with `final_output` and `new_messages` attributes).
- **Rationale**: Avoids real Gemini API calls in CI; tests remain fast and deterministic; follows the existing `conftest.py` pattern of `app.dependency_overrides`.
- **Alternatives considered**: VCR cassettes for recorded HTTP responses (brittle to SDK internals); integration tests against real API (requires credentials in CI; slow; costly).
