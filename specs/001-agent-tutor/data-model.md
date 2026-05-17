# Data Model: AgentTutor Backend

**Feature**: 001-agent-tutor
**Date**: 2026-05-01
**Branch**: 001-agent-tutor

## Entity Relationship Overview

```
users (1) ────< progress (N)       [user_id FK]
users (1) ────< quiz_results (N)   [user_id FK]
chapters (1) ──< progress (N)      [chapter_id FK]
chapters (1) ──< quiz_results (N)  [chapter_id FK]
chapters (1) ──< quiz_bank (N)     [chapter_id FK]
```

## Table Definitions

### `users`

Stores learner profile, subscription tier, and streak state.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique student identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Student email (login identity) |
| `name` | VARCHAR(255) | NOT NULL | Display name |
| `tier` | VARCHAR(20) | NOT NULL, DEFAULT 'free', CHECK IN ('free','premium') | Subscription level |
| `streak_days` | INTEGER | NOT NULL, DEFAULT 0 | Current consecutive learning days |
| `last_active` | DATE | NULLABLE | Last date (UTC) student completed a chapter or quiz |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation timestamp |

**Indexes**: `UNIQUE(email)`, `INDEX(tier)` for bulk tier queries.

**Business rules**:
- `tier` transitions: free → premium (allowed); premium → free (allowed for downgrade)
- `streak_days` reset to 1 when `last_active` gap > 1 calendar day (UTC)
- `last_active` updated on every chapter completion or quiz submission

---

### `chapters`

Chapter metadata and searchable content cache. Content served verbatim from R2.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(20) | PK | Slug identifier, e.g., `chapter-01` |
| `number` | INTEGER | UNIQUE, NOT NULL | Sequential chapter number (1–10) |
| `title` | VARCHAR(255) | NOT NULL | Chapter display title |
| `tier_required` | VARCHAR(20) | NOT NULL, DEFAULT 'free', CHECK IN ('free','premium') | Access requirement |
| `content_key` | VARCHAR(255) | NOT NULL | R2 storage key, e.g., `chapters/chapter-01.md` |
| `search_text` | TEXT | NULLABLE | Plaintext content for keyword search (loaded at seed) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Row creation timestamp |

**Chapter ID mapping**:

| id | number | title | tier_required |
|---|---|---|---|
| chapter-01 | 1 | What is an AI Agent | free |
| chapter-02 | 2 | Claude Agent SDK Basics | free |
| chapter-03 | 3 | Building Your First Agent | free |
| chapter-04 | 4 | Model Context Protocol | premium |
| chapter-05 | 5 | Agent Skills and SKILL.md | premium |
| chapter-06 | 6 | Multi-Agent Collaboration | premium |
| chapter-07 | 7 | Agent Memory and State | premium |
| chapter-08 | 8 | A2A Protocol | premium |
| chapter-09 | 9 | Agent Factory Architecture | premium |
| chapter-10 | 10 | Production Deployment | premium |

**Access gate constant** (in `routers/chapters.py`):
```python
FREE_CHAPTERS = {"chapter-01", "chapter-02", "chapter-03"}
```

---

### `progress`

One row per (user, chapter) pair. Records completion and time spent.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Row identifier |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | Student |
| `chapter_id` | VARCHAR(20) | NOT NULL, FK → chapters(id) | Chapter |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether chapter was finished |
| `completed_at` | TIMESTAMPTZ | NULLABLE | When completion was recorded |
| `time_spent_seconds` | INTEGER | NULLABLE | Optional time tracking (future use) |

**Constraint**: `UNIQUE(user_id, chapter_id)` — one record per student per chapter.
Re-completion updates `completed_at` (upsert pattern).

---

### `quiz_results`

Records each quiz attempt. Multiple attempts per (user, chapter) are allowed.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Row identifier |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | Student |
| `chapter_id` | VARCHAR(20) | NOT NULL, FK → chapters(id) | Chapter the quiz belongs to |
| `score` | INTEGER | NOT NULL | Number of correct answers |
| `total_questions` | INTEGER | NOT NULL | Total questions in this attempt |
| `answers` | JSONB | NOT NULL | Student answers: `{"1": "A", "2": "C", ...}` |
| `attempted_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Attempt timestamp |

**Note**: Correct answers are NOT stored in quiz_results — only student answers.
Pass/fail is computed on read from `score >= QUIZ_PASS_THRESHOLD`.

---

### `quiz_bank`

Master quiz question store. Seeded once at setup. Correct answers stored here.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Row identifier |
| `chapter_id` | VARCHAR(20) | NOT NULL, FK → chapters(id) | Chapter this question belongs to |
| `question_number` | INTEGER | NOT NULL | Question sequence within chapter (1–5) |
| `question` | TEXT | NOT NULL | Full question text |
| `option_a` | TEXT | NOT NULL | Option A text |
| `option_b` | TEXT | NOT NULL | Option B text |
| `option_c` | TEXT | NOT NULL | Option C text |
| `option_d` | TEXT | NOT NULL | Option D text |
| `correct_answer` | CHAR(1) | NOT NULL, CHECK IN ('A','B','C','D') | Correct option |

**Constraint**: `UNIQUE(chapter_id, question_number)` — unique question per chapter.
**Total rows at seed**: 10 chapters × 5 questions = 50 rows.

---

## Migration SQL

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'free'
        CHECK (tier IN ('free', 'premium')),
    streak_days INTEGER NOT NULL DEFAULT 0,
    last_active DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_tier ON users(tier);

-- chapters
CREATE TABLE IF NOT EXISTS chapters (
    id VARCHAR(20) PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    tier_required VARCHAR(20) NOT NULL DEFAULT 'free'
        CHECK (tier_required IN ('free', 'premium')),
    content_key VARCHAR(255) NOT NULL,
    search_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chapters_tier ON chapters(tier_required);
CREATE INDEX IF NOT EXISTS idx_chapters_number ON chapters(number);

-- progress
CREATE TABLE IF NOT EXISTS progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id VARCHAR(20) NOT NULL REFERENCES chapters(id),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    time_spent_seconds INTEGER,
    UNIQUE(user_id, chapter_id)
);
CREATE INDEX IF NOT EXISTS idx_progress_user ON progress(user_id);

-- quiz_results
CREATE TABLE IF NOT EXISTS quiz_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id VARCHAR(20) NOT NULL REFERENCES chapters(id),
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    answers JSONB NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_quiz_results_user ON quiz_results(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_results_chapter ON quiz_results(chapter_id);

-- quiz_bank
CREATE TABLE IF NOT EXISTS quiz_bank (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id VARCHAR(20) NOT NULL REFERENCES chapters(id),
    question_number INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    UNIQUE(chapter_id, question_number)
);
CREATE INDEX IF NOT EXISTS idx_quiz_bank_chapter ON quiz_bank(chapter_id);
```

## Streak Calculation Logic

```python
from datetime import date, timedelta

def update_streak(last_active: date | None, streak_days: int) -> tuple[int, date]:
    today = date.today()  # UTC
    if last_active is None:
        return 1, today
    if last_active == today:
        return streak_days, today          # idempotent: same day
    if last_active == today - timedelta(days=1):
        return streak_days + 1, today      # consecutive day
    return 1, today                        # gap: reset
```

## Quiz Grading Logic

```python
QUIZ_PASS_THRESHOLD = 4  # out of 5

def grade_quiz(
    student_answers: dict[int, str],  # {question_number: "A"|"B"|"C"|"D"}
    correct_answers: dict[int, str],  # fetched from quiz_bank, NOT returned to client
) -> dict:
    wrong = [q for q, ans in student_answers.items()
             if correct_answers.get(q) != ans]
    score = len(student_answers) - len(wrong)
    total = len(correct_answers)
    return {
        "score": score,
        "total": total,
        "percentage": round(score / total * 100),
        "passed": score >= QUIZ_PASS_THRESHOLD,
        "wrong_question_numbers": sorted(wrong),
    }
    # NOTE: correct_answers dict is NEVER included in the return value
```
