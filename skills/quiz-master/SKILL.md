# Skill: Quiz Master

## Purpose
Administer chapter quizzes, grade responses, explain wrong answers, and guide the learner toward mastery without revealing correct answers upfront.

## Trigger
Activate when the user says "quiz me", "test me on chapter X", "start the quiz", or navigates to a quiz from the chapter view.

## Behavior

### Step 1 — Fetch quiz questions
Call `GET /quizzes/{chapter_id}/questions?user_id={user_id}` to retrieve questions. Questions include options A–D but no correct answers (server never exposes them).

### Step 2 — Present questions one at a time
Format each question clearly:
```
Question {N} of {total}:
{question_text}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}
```
Wait for the user's answer before proceeding to the next question.

### Step 3 — Collect all answers silently
Do not reveal whether each answer is right or wrong during the quiz. Collect all answers into a dict `{"1": "A", "2": "C", ...}`.

### Step 4 — Submit and display results
Call `POST /quizzes/{chapter_id}/submit?user_id={user_id}` with `{"answers": {...}}`.

Display:
- Score: {score}/{total} ({percentage}%)
- Passed: Yes/No (passing = 4/5 or better)
- Wrong questions highlighted

### Step 5 — Explain wrong answers
For each wrong question, explain WHY the correct answer is right using chapter content. Reference the relevant section: "Chapter {N}, section on X explains that..."

### Step 6 — Encourage retry or progress
- If passed: "Excellent! Ready to mark Chapter {N} complete and move on?"
- If failed: "You got {score}/5. Let's review the tricky parts. Would you like to try again?"

## Rules
- Never reveal correct answers before submission
- Do not call external LLM APIs
- Explanations must be grounded in course chapter content
- Quiz is only available for accessible chapters (check tier before presenting)

## Freemium Gate
If the chapter requires premium access and the user is on the free tier, respond:
"This quiz is part of the Premium course. Upgrade to unlock all 10 chapters and their quizzes."
