# Feature Specification: AgentTutor — AI Agent Learning Companion

**Feature Branch**: `001-agent-tutor`
**Created**: 2026-05-01
**Status**: Draft
**Input**: User description: AgentTutor Phase 1 — Zero-Backend-LLM Course Companion FTE

## Overview

AgentTutor is a production-ready Digital Full-Time Equivalent (FTE) educational
tutor for the Panaversity Agent Factory Hackathon IV. It teaches students AI Agent
Development — covering the Claude Agent SDK, Model Context Protocol (MCP), Agent
Skills, and the Agent Factory Architecture — through a conversational ChatGPT App
backed by a deterministic content and progress service.

The system has two parts:

1. **Deterministic Backend** — serves course content, grades quizzes by answer key,
   tracks student progress, and enforces freemium access. It performs zero LLM
   inference; all data flows are rule-based and predictable.
2. **ChatGPT App** — the conversational front end where students interact. ChatGPT
   handles all intelligent tutoring: explaining concepts, motivating students,
   adapting tone, and answering questions using content fetched from the backend.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Free Student Learns Chapter Content (Priority: P1)

A student signs up for free and starts learning about AI Agents. They ask AgentTutor
to show them the first chapter. The system confirms their free tier, retrieves the
chapter content verbatim, and ChatGPT presents and explains it conversationally.
The student then asks a follow-up question and ChatGPT answers using only the fetched
content — no external knowledge.

**Why this priority**: Content delivery is the core value proposition. Without it,
no other feature matters. It also demonstrates the Zero-Backend-LLM invariant
directly.

**Independent Test**: A free-tier user can request chapter 1, 2, or 3 and receive
the full content. Verifiable by checking the backend serves unmodified markdown and
makes zero LLM calls during the request lifecycle.

**Acceptance Scenarios**:

1. **Given** a free-tier user, **When** they request chapter 1, **Then** the system
   returns the full chapter markdown content unchanged within 2 seconds.
2. **Given** a free-tier user, **When** they request chapter 4, **Then** the system
   returns an access-denied response and does not return any content.
3. **Given** a premium user, **When** they request any of the 10 chapters, **Then**
   the full content is returned.

---

### User Story 2 — Student Takes a Chapter Quiz (Priority: P2)

After reading a chapter, a student wants to test their knowledge. They ask AgentTutor
to quiz them. The backend serves multiple-choice questions for that chapter. ChatGPT
presents the questions one at a time. The student submits their answers, the backend
grades them against a stored answer key, and ChatGPT delivers the result with
encouragement.

**Why this priority**: Quizzes are the primary engagement and retention mechanism.
They also directly validate the rule-based grading constraint — no LLM must be
involved in scoring.

**Independent Test**: Request quiz questions for chapter 1 and submit answers; verify
the backend returns correct/incorrect based on the answer key, with no LLM call.

**Acceptance Scenarios**:

1. **Given** a student on chapter 2, **When** they request the quiz, **Then** the
   system returns all questions for that chapter.
2. **Given** a student submitting quiz answers, **When** all answers are correct,
   **Then** the system records a 100% score and ChatGPT celebrates.
3. **Given** a student submitting wrong answers, **When** graded, **Then** the
   system returns which answers were incorrect (no explanations from backend —
   ChatGPT explains using chapter content).
4. **Given** a free-tier student, **When** they request the chapter 5 quiz,
   **Then** the system returns an access-denied error.

---

### User Story 3 — Student Tracks Learning Progress and Streaks (Priority: P3)

A returning student wants to know how far they've come. They ask "how am I doing?"
ChatGPT fetches their progress profile: completed chapters, quiz scores, current
streak, and last active date. ChatGPT motivates them based on this data.

**Why this priority**: Progress visibility drives re-engagement and streak
maintenance. It is the feedback loop that keeps students returning.

**Independent Test**: Complete chapter 1 as a user, then retrieve progress;
verify completion, score, streak count, and last-active date are persisted and
returned correctly.

**Acceptance Scenarios**:

1. **Given** a student who completed chapter 1 yesterday and chapter 2 today,
   **When** they check progress, **Then** the system returns 2 chapters complete
   and a 2-day streak.
2. **Given** a student who missed 2 consecutive days, **When** they return,
   **Then** the streak resets to 1 on the new active day.
3. **Given** a brand-new student, **When** they check progress, **Then** the system
   returns 0 chapters complete and streak = 0.

---

### User Story 4 — Student Navigates Sequentially (Priority: P4)

A student finishes a chapter and wants to continue to the next one without manually
looking it up. ChatGPT calls the navigation endpoint to retrieve the next chapter
reference and guides the student forward.

**Why this priority**: Sequential navigation is the standard learning path. It
reduces friction and keeps students in the flow state.

**Independent Test**: Call the navigation endpoint for chapter 3; verify it returns
chapter 4 metadata (or an access-upgrade prompt for free users), with chapter 2 as
previous.

**Acceptance Scenarios**:

1. **Given** a student on chapter 3, **When** they ask for the next chapter,
   **Then** the system returns metadata for chapter 4 (title, access required).
2. **Given** a student on chapter 1, **When** they ask for the previous chapter,
   **Then** the system indicates there is no previous chapter.
3. **Given** a student on the final chapter (10), **When** they ask for next,
   **Then** the system indicates the course is complete.

---

### User Story 5 — Student Searches for a Topic (Priority: P5)

A student wants to find all sections mentioning "MCP" or "tool use". They ask
AgentTutor to search. The backend performs a keyword search across their accessible
chapters and returns matching excerpts. ChatGPT presents the results contextually.

**Why this priority**: Search provides direct, non-linear access to specific
knowledge, especially valuable for students who return to review a topic.

**Independent Test**: Search for "Model Context Protocol" as a free-tier user;
verify only chapters 1–3 content is searched and relevant excerpts are returned.

**Acceptance Scenarios**:

1. **Given** a free-tier student, **When** they search for "AI Agent", **Then**
   the system returns matching excerpts from chapters 1–3 only.
2. **Given** a premium student, **When** they search for "A2A Protocol", **Then**
   the system returns matching excerpts from all relevant chapters.
3. **Given** a search query with no matches, **When** submitted, **Then** the
   system returns an empty result set (not an error).

---

### User Story 6 — Free User Hits Paywall and Sees Upgrade Path (Priority: P6)

A curious free student tries to open chapter 5. The system returns a clear
access-denied response. ChatGPT explains what premium unlocks and guides the
student toward upgrading.

**Why this priority**: Graceful paywall handling converts free users to premium.
The user experience at the gate determines conversion rate.

**Independent Test**: Attempt to access chapter 4 as a free user; verify a
structured denial response is returned with the premium tier requirement stated.

**Acceptance Scenarios**:

1. **Given** a free-tier student, **When** they try to access chapter 4–10,
   **Then** the system returns an access-denied response indicating premium is
   required.
2. **Given** a free-tier student, **When** they try to search chapter 4–10 content,
   **Then** the search scope is silently limited to chapters 1–3 (no error, just
   scoped results).

---

### Edge Cases

- What happens when a student requests a chapter that does not exist (e.g., chapter 11)?
- How does the system handle a duplicate quiz submission for the same chapter?
- What if a student's streak break occurs exactly at midnight (timezone boundary)?
- What happens if content storage is temporarily unavailable when a chapter is requested?
- What if a user submits a quiz with partial answers (some questions unanswered)?
- How are quiz questions ordered — always the same or randomised per session?

## Requirements *(mandatory)*

### Functional Requirements

**Content & Navigation**

- **FR-001**: The system MUST serve chapter content verbatim without modification,
  summarization, or transformation.
- **FR-002**: The system MUST check a student's subscription tier before serving
  any chapter; chapters 1–3 are free, chapters 4–10 require premium.
- **FR-003**: The system MUST return a structured access-denied response (not an
  error) when a free-tier student requests a premium chapter, clearly indicating
  premium is required.
- **FR-004**: The system MUST return navigation metadata (title, chapter number,
  access tier) for the next and previous chapters relative to a given chapter.
- **FR-005**: The system MUST indicate "no previous chapter" for chapter 1 and
  "course complete" for chapter 10 in navigation responses.

**Search**

- **FR-006**: The system MUST support keyword search across chapter content.
- **FR-007**: Search results MUST be scoped to chapters the requesting student
  is authorised to access; premium chapters MUST NOT appear in free-user results.
- **FR-008**: Search MUST return matching excerpts (not full chapters) alongside
  chapter title and number.

**Quiz System**

- **FR-009**: The system MUST serve multiple-choice quiz questions for each chapter.
- **FR-010**: The system MUST grade submitted quiz answers against a stored answer
  key using rule-based logic only; no LLM or inference engine may be used for grading.
- **FR-011**: The grading response MUST indicate which answers were correct and which
  were incorrect, along with the overall score.
- **FR-012**: Quiz access MUST be gated by the same tier rules as content
  (free quiz for chapters 1–3, premium quiz for 4–10).

**Progress Tracking**

- **FR-013**: The system MUST record chapter completion events per student, including
  the completion timestamp.
- **FR-014**: The system MUST record quiz attempt results (score, timestamp) per
  student per chapter.
- **FR-015**: The system MUST maintain a daily learning streak counter per student,
  incrementing on each day the student completes at least one chapter or quiz.
- **FR-016**: The system MUST reset the streak counter to 1 when a student resumes
  after missing one or more calendar days.
- **FR-017**: The system MUST expose a progress summary endpoint returning total
  chapters completed, average quiz score, current streak, and last active date.

**Zero-LLM Invariant**

- **FR-018**: The backend MUST NOT call any LLM API (OpenAI, Anthropic, or any
  other) under any circumstances. All content is served verbatim; all grading is
  rule-based; all data is deterministic.

**Agent Skills**

- **FR-019**: Four SKILL.md files MUST be authored defining the ChatGPT App's
  educational behaviors:
  - `concept-explainer` — explains AI Agent concepts using only content served
    by the backend
  - `quiz-master` — guides students through quiz questions one at a time with
    encouragement
  - `socratic-tutor` — helps stuck students discover answers through guided
    questions, never giving answers directly
  - `progress-motivator` — celebrates completions, tracks streaks, and maintains
    learning momentum

**User Management**

- **FR-020**: Each student MUST be identified by a unique persistent identifier.
- **FR-021**: Student records MUST store: name, email, subscription tier
  (free/premium), streak count, and last active date.
- **FR-022**: The system MUST support tier updates (free → premium) without data loss.

### Key Entities

- **Student**: A learner with a unique identifier, name, email, subscription tier
  (free or premium), daily streak count, and last active date.
- **Chapter**: A course content unit with a sequential number (1–10), title, access
  tier requirement, and markdown content stored in object storage.
- **Quiz**: A set of multiple-choice questions associated with a chapter, each with
  four options and a stored correct answer. Graded by answer key only.
- **Progress Record**: A log entry per student per chapter recording completion
  status, quiz score, and timestamp.
- **Skill**: A SKILL.md behavioral guide defining how the ChatGPT App tutors
  students for a specific interaction pattern.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can retrieve any accessible chapter's content in under
  2 seconds under normal load.
- **SC-002**: Quiz answers are graded and results returned in under 1 second.
- **SC-003**: Keyword search returns results within 1 second for queries across
  accessible chapters.
- **SC-004**: 100% of backend request handlers make zero LLM API calls
  (verified by code review and API audit log).
- **SC-005**: All 6 core features (content delivery, navigation, search, quiz,
  progress tracking, freemium gate) are functional and independently testable.
- **SC-006**: Progress data (completions, scores, streaks) is persisted and
  retrievable across separate student sessions without loss.
- **SC-007**: 100% of attempts to access premium content as a free user receive
  a structured access-denied response with an upgrade prompt — never a raw error.
- **SC-008**: The system supports at least 1,000 concurrent student sessions
  without performance degradation.
- **SC-009**: All 4 SKILL.md files are authored, triggerable by their defined
  keywords, and produce consistent educational behavior.
- **SC-010**: The freemium tier model is correctly enforced: free students access
  exactly chapters 1–3; premium students access all 10 chapters.

## Assumptions

- Quiz questions per chapter: assumed 5–10 multiple-choice questions each with
  4 options (A–D). Exact counts to be defined in content creation.
- Streak timezone: server-side UTC date used for streak calculations;
  per-user timezone support is out of scope for Phase 1.
- Authentication: students are identified by UUID passed in requests; full auth/login
  is out of scope for Phase 1 (backend trusts the provided user ID).
- Content updates: course markdown files are authored and uploaded to storage
  before launch; live editing is out of scope for Phase 1.
- Quiz randomisation: questions served in fixed order per chapter; random ordering
  is out of scope for Phase 1.
- Tech stack (recorded here for planning reference, not spec constraint):
  backend = FastAPI/Python 3.12; database = Neon PostgreSQL; content storage =
  Cloudflare R2; ChatGPT frontend = OpenAI Apps SDK; hosting = Fly.io.

## Out of Scope (Phase 1)

- Backend LLM calls of any kind (hard constraint, not just out of scope)
- Adaptive learning paths or personalised recommendations
- LLM-graded free-form assessments
- User registration / login UI
- Payment processing or subscription billing
- Admin dashboard or content management interface
- Mobile native apps
- Phase 2 hybrid intelligence features
