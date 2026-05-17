# Data Model: AgentTutor Phase 2 — Hybrid Intelligence

**Feature**: 002-hybrid-intelligence | **Date**: 2026-05-17

Phase 2 introduces no new database tables. All data entities either map to existing tables or are transient request/response structures.

---

## Existing Tables Used (read-only access)

### `users`
| Column | Type | Used By |
|---|---|---|
| `id` | UUID | Tier lookup in both endpoints |
| `tier` | `"free" \| "premium"` | Premium gate in both endpoints |

### `progress`
| Column | Type | Used By |
|---|---|---|
| `user_id` | UUID | `get_student_progress` tool |
| `chapter_id` | String | `get_student_progress` tool |
| `completed` | Boolean | `get_student_progress` tool |
| `completed_at` | DateTime | `get_student_progress` tool |

### `quiz_results`
| Column | Type | Used By |
|---|---|---|
| `user_id` | UUID | `get_student_progress` tool |
| `chapter_id` | String | `get_student_progress` tool |
| `score` | Integer | `get_student_progress` tool (best score per chapter) |
| `total_questions` | Integer | `get_student_progress` tool |

---

## Filesystem Entity

### `Chapter` (local file)
- **Location**: `backend/content/chapters/{chapter_id}.md`
- **Access**: `get_local_content(chapter_id)` from `backend/storage/content_reader.py`
- **Used By**: Assessor agent (chapter context), `get_chapter_content` mentor tool

---

## Transient Request/Response Models

### `AssessRequest`
```
user_id:        UUID      — identifies the submitting student
chapter_id:     str       — e.g. "chapter-01"; maps to filesystem path
question:       str       — the original question posed to the student
student_answer: str       — the free-form written response to grade
```
Validation: all fields required; `student_answer` must be non-empty.

### `AssessResponse`
```
score:           int    — 0 to 10 inclusive
max_score:       int    — always 10
grade:           str    — letter grade (A, B+, C, etc.)
feedback:        str    — overall encouraging summary
what_was_correct: str   — specific correct elements
what_was_missing: str   — gaps vs. chapter content
improvement_tip: str    — one actionable next step
estimated_cost_usd: float — fixed at 0.014
```

### `MentorRequest`
```
user_id:  UUID — identifies the student
question: str  — free-form question or "I'm stuck" statement
```
Validation: `question` must be non-empty.

### `MentorResponse`
```
mentor_response:      str        — Socratic guidance from the AI mentor
chapters_referenced:  list[str]  — chapter IDs fetched by get_chapter_content tool
tools_used:           list[str]  — tool names invoked during the agent run
estimated_cost_usd:   float      — fixed at 0.090
```

---

## Progress Summary (intermediate, not persisted)

Built by `_fetch_progress_summary()` in `hybrid.py` before agent creation:

```
Completed chapters:
  - chapter-01 (score: 8/10)
  - chapter-02 (score: 7/10)
In progress: chapter-03 (not yet completed)
```
Passed to `get_student_progress` tool as a formatted string via closure.

---

## Entity Relationships (Phase 2 perspective)

```
Student (User.id, User.tier)
    │
    ├─── [assess] ──► Chapter (filesystem) ──► AssessorAgent ──► AssessResponse
    │
    └─── [mentor] ──► StudentProgress (DB query)
                  └──► MentorAgent ──► [get_chapter_content] ──► Chapter (filesystem)
                                   └──► [get_student_progress] ──► StudentProgress
                                   └──► MentorResponse
```
