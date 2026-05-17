# Feature Specification: AgentTutor Phase 2 — Hybrid Intelligence

**Feature Branch**: `002-hybrid-intelligence`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: User description: "AgentTutor Phase 2 — two premium hybrid intelligence features: LLM Graded Assessment and AI Mentor Agent, isolated from Phase 1, gated behind premium tier, user-initiated only."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Premium Student Gets Intelligent Assessment (Priority: P1)

A premium-tier student completes reading a chapter and writes a free-form answer to a chapter question. They submit it and receive personalised AI-graded feedback showing their score, what they got right, what they missed, and how to improve — feedback that captures partial understanding, not just keyword matching.

**Why this priority**: This directly replaces the limitation of rule-based grading and is the primary reason Phase 2 exists. Without it, nuanced student understanding cannot be evaluated. It can be deployed and demonstrated standalone.

**Independent Test**: Fully testable by POSTing to `/hybrid/assess` with a premium user's credentials and a written answer — the response must contain score, grade, structured feedback, and a cost field.

**Acceptance Scenarios**:

1. **Given** a premium user submits a chapter question and a partially correct written answer, **When** the assessment endpoint processes the request, **Then** the response includes a numeric score (0–10), a letter grade, specific feedback on what was correct, what was missing, an improvement tip, and an estimated cost field.
2. **Given** a free-tier user calls the assessment endpoint, **When** the system checks their tier, **Then** the system returns a 403 error with a `premium_required` error code and no grading is performed.
3. **Given** a premium user submits an answer for a chapter that does not exist on the file system, **When** the system attempts to fetch chapter content, **Then** the system returns a 404 error with a descriptive message.
4. **Given** a premium user submits an empty or blank student answer, **When** the request is received, **Then** the system returns a 422 validation error without calling the AI grader.

---

### User Story 2 - Premium Student Gets AI Mentor Guidance (Priority: P2)

A premium-tier student is confused about a concept and types a natural-language question. An AI Mentor Agent fetches relevant chapter content and the student's progress record, then responds with a Socratic, personalised explanation — guiding the student to understanding rather than just presenting the answer.

**Why this priority**: This is the higher-complexity feature and depends on the same infrastructure as Story 1. It can be deployed independently once the premium gate and LLM client are established.

**Independent Test**: Fully testable by POSTing to `/hybrid/mentor` with a premium user's question — the response must contain a mentor response, the list of chapters referenced, the tools the agent used, and a cost field.

**Acceptance Scenarios**:

1. **Given** a premium user asks a question about a course concept, **When** the AI Mentor Agent runs, **Then** the agent fetches at least one relevant chapter and the student's progress before composing its response, and the final response reflects both sources.
2. **Given** a free-tier user calls the mentor endpoint, **When** the system checks their tier, **Then** the system returns a 403 error with a `premium_required` error code and no agent is created or run.
3. **Given** a premium user submits a question, **When** the agent finishes reasoning, **Then** the response lists which chapters were referenced, which tools were invoked, and the estimated session cost.
4. **Given** a premium user sends an empty question string, **When** the request is received, **Then** the system returns a 422 validation error without invoking the agent.

---

### User Story 3 - Free-Tier Users Are Clearly Blocked (Priority: P3)

A free-tier student attempts to access either the assessment or mentor endpoints. The system must reject the request immediately with a clear, actionable error rather than silently degrading or returning an empty result.

**Why this priority**: Correct tier enforcement is a non-functional correctness requirement. Both premium features depend on it. It must pass before any other hybrid endpoint can be trusted in production.

**Independent Test**: POST to either `/hybrid/assess` or `/hybrid/mentor` with a known free-tier user ID — must return HTTP 403 with `{"error": "premium_required"}`.

**Acceptance Scenarios**:

1. **Given** a free-tier user calls `/hybrid/assess`, **When** the tier check runs, **Then** the response is HTTP 403 with error code `premium_required` and the AI grader is never invoked.
2. **Given** a free-tier user calls `/hybrid/mentor`, **When** the tier check runs, **Then** the response is HTTP 403 with error code `premium_required` and no agent is created.

---

### Edge Cases

- What happens when the AI grader returns a response that cannot be parsed into the expected structured format (score, grade, feedback fields)?
- What happens when the Gemini API call times out or returns an error mid-agent-run?
- What happens when `get_student_progress` returns no completed chapters (brand-new student)?
- What happens when the chapter file exists but is empty or malformed markdown?
- What happens when the same user sends concurrent requests to `/hybrid/mentor`?
- How does the system handle a `chapter_id` with path-traversal characters (e.g., `../../etc/passwd`)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a `POST /hybrid/assess` endpoint that accepts `user_id`, `chapter_id`, `question`, and `student_answer` fields.
- **FR-002**: System MUST expose a `POST /hybrid/mentor` endpoint that accepts `user_id` and `question` fields.
- **FR-003**: Both endpoints MUST check the requesting user's tier as the first operation; free-tier users MUST receive an HTTP 403 with `premium_required` error before any AI call is made.
- **FR-004**: `/hybrid/assess` MUST fetch chapter content from the local file system using the same mechanism as Phase 1 before invoking the grader.
- **FR-005**: `/hybrid/assess` MUST use an AI model to evaluate the student's answer against the chapter content and return: `score` (integer 0–10), `max_score` (10), `grade` (letter), `feedback` (string), `what_was_correct` (string), `what_was_missing` (string), `improvement_tip` (string), and `estimated_cost_usd` (float fixed at 0.014).
- **FR-006**: `/hybrid/mentor` MUST create an AI agent equipped with two tools: one that retrieves chapter content by chapter ID from the local file system, and one that retrieves a student's completed chapters and quiz scores from the database.
- **FR-007**: The AI Mentor agent MUST invoke at least one tool before producing its final response; a response produced without tool use is considered invalid.
- **FR-008**: `/hybrid/mentor` MUST return: `mentor_response` (string), `chapters_referenced` (list of chapter IDs), `tools_used` (list of tool names called), and `estimated_cost_usd` (float fixed at 0.090).
- **FR-009**: All Phase 2 code MUST reside exclusively in `backend/routers/hybrid.py`; no Phase 1 router files may be modified.
- **FR-010**: The hybrid router MUST be registered in `main.py` under the URL prefix `/hybrid`.
- **FR-011**: The `GEMINI_API_KEY` environment variable MUST be consumed from the environment (never hardcoded) and documented in `.env.example`.
- **FR-012**: `openai-agents` MUST be added to `requirements.txt`.
- **FR-013**: Both endpoints MUST log the estimated token cost per request at INFO level.
- **FR-014**: Integration tests MUST exist for both endpoints verifying: free-user 403, premium-user valid response, required fields present, `estimated_cost_usd` field present.

### Key Entities

- **AssessmentRequest**: Submitted by a premium student — contains `user_id`, `chapter_id`, `question`, `student_answer`.
- **AssessmentResponse**: Returned to the student — contains `score`, `max_score`, `grade`, `feedback`, `what_was_correct`, `what_was_missing`, `improvement_tip`, `estimated_cost_usd`.
- **MentorRequest**: Submitted by a premium student — contains `user_id`, `question`.
- **MentorResponse**: Returned to the student — contains `mentor_response`, `chapters_referenced`, `tools_used`, `estimated_cost_usd`.
- **User**: Identified by `user_id`; has a `tier` attribute (`free` | `premium`) that governs access.
- **Chapter**: A markdown file on the local file system identified by `chapter_id`; same source used by Phase 1.
- **StudentProgress**: A record from the database containing the student's list of completed chapters and associated quiz scores.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A premium student receives a fully structured assessment response (all 7 fields populated) within 30 seconds of submitting their written answer.
- **SC-002**: A free-tier user attempting either hybrid endpoint receives a 403 response in under 500 ms — no AI call is made.
- **SC-003**: The AI Mentor agent uses at least one tool in 100% of successful mentor sessions, ensuring personalised rather than generic responses.
- **SC-004**: Both integration test files pass fully (4 test cases each: 403 for free user, valid response for premium user, required fields check, cost field check) with zero failures on a clean run.
- **SC-005**: Estimated cost is logged and returned for every successful hybrid request, enabling cost tracking from day one.
- **SC-006**: Phase 1 test suite passes without modification after Phase 2 is integrated — zero regressions in existing endpoints.

## Assumptions

- The user tier lookup mechanism (free vs. premium) already exists in the Phase 1 codebase and can be reused by importing it into `hybrid.py`.
- Chapter content files are stored as markdown on the local file system in the same directory structure Phase 1 uses; `chapter_id` maps directly to a filename/path.
- The student progress data (completed chapters, quiz scores) is already persisted in the Phase 1 database and is queryable by `user_id`.
- `Runner.run_sync()` from the OpenAI Agents SDK is appropriate for the synchronous FastAPI request-response model used in Phase 1.
- The fixed cost values ($0.014 for assessment, $0.090 for mentor) are product-defined estimates, not calculated from actual token counts — they are returned as constants in every response.
- Tests use test-fixture users where one has `tier=free` and another has `tier=premium`; no real Gemini API calls are made in integration tests (mocked at the runner level).

## Out of Scope

- Modifying any Phase 1 router, model, or migration file.
- Streaming responses or WebSocket-based mentor sessions.
- Actual per-request token metering or dynamic cost calculation.
- Frontend UI changes.
- Rate limiting or per-user quota enforcement for hybrid endpoints.
- Caching of AI grader or mentor responses.
