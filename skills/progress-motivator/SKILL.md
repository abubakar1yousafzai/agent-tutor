# Skill: Progress Motivator

## Purpose
Keep learners engaged, celebrate milestones, surface progress data, and provide personalized encouragement based on streak and completion state.

## Trigger
Activate when:
- The user completes a chapter or quiz
- The user asks "how am I doing?", "what's my progress?", "show my streak"
- The user has been inactive (detected via stale `last_active` date)
- After marking a chapter complete via `POST /progress/{user_id}/chapters/{chapter_id}/complete`

## Behavior

### Step 1 — Fetch current progress
Call `GET /progress/{user_id}` to get:
- `chapters_completed` / `total_accessible_chapters`
- `completion_percentage`
- `streak_days`
- `chapter_progress` list

### Step 2 — Celebrate appropriately

**On chapter completion:**
- Streak day 1: "Great start! You've begun your learning journey. Come back tomorrow to build your streak."
- Streak days 2–4: "You're on a {N}-day streak! Momentum is building. Keep it going!"
- Streak days 5–9: "Amazing — {N} days straight! You're in the top tier of learners."
- Streak 10+: "UNSTOPPABLE! {N}-day streak. You are a machine. 🔥"

**On quiz pass:**
"Quiz passed with {percentage}%! That's chapter {N} locked in. Ready for Chapter {N+1}?"

**On quiz fail:**
"You scored {score}/5 — so close! The tricky questions were about {topics}. Want a quick review, then try again?"

### Step 3 — Surface progress summary
Display a visual progress bar (text-based):
```
Progress: [████████░░] 80% (8/10 chapters)
Streak:   🔥 5 days
```

### Step 4 — Nudge toward next action
Always close with a specific next action:
- If chapters remain: "Your next chapter is '{title}'. Ready to start?"
- If quiz pending: "You haven't taken the Chapter {N} quiz yet. Want to test your knowledge?"
- If all complete: "You've finished the entire course! Share your achievement."

### Step 5 — Freemium nudge (for free users with locked chapters)
After completing chapter 3:
"You've completed all free chapters! Unlock 7 more chapters and the full quiz bank with Premium. Want to continue your learning journey?"

## Rules
- Fetch real progress from the API — never fabricate completion numbers
- Motivational tone must remain genuine, not sycophantic
- Adapt intensity to streak length — mild for day 1, excited for day 10+
- Do not call external LLM APIs

## Streak Calculation (reference)
- Same day: streak unchanged (idempotent)
- Next consecutive day: streak + 1
- Gap > 1 day: streak resets to 1
