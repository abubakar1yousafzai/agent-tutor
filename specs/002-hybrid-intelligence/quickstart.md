# Quickstart: AgentTutor Phase 2 — Hybrid Intelligence

**Feature**: 002-hybrid-intelligence | **Date**: 2026-05-17

---

## Prerequisites

- Phase 1 backend running (all tables created, chapters seeded)
- A Gemini API key from Google AI Studio
- A user record with `tier = "premium"` in the database

---

## 1. Install the new dependency

```bash
cd backend
pip install openai-agents
# or if using requirements.txt:
pip install -r requirements.txt
```

---

## 2. Set the Gemini API key

```bash
# backend/.env  (never commit this file)
echo "GEMINI_API_KEY=your_key_here" >> backend/.env
```

---

## 3. Run the server

```bash
cd backend
uvicorn backend.main:app --reload
```

The hybrid endpoints are now live at:
- `POST http://localhost:8000/hybrid/assess`
- `POST http://localhost:8000/hybrid/mentor`

---

## 4. Test the Assessment Endpoint

```bash
curl -X POST http://localhost:8000/hybrid/assess \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<your-premium-user-uuid>",
    "chapter_id": "chapter-01",
    "question": "Explain the agent loop in your own words.",
    "student_answer": "An agent loop is when the AI keeps checking its environment and taking actions until it reaches a goal."
  }'
```

**Expected response** (200):
```json
{
  "score": 8,
  "max_score": 10,
  "grade": "B+",
  "feedback": "...",
  "what_was_correct": "...",
  "what_was_missing": "...",
  "improvement_tip": "...",
  "estimated_cost_usd": 0.014
}
```

**Free user** → `403 {"error": "premium_required"}`

---

## 5. Test the Mentor Endpoint

```bash
curl -X POST http://localhost:8000/hybrid/mentor \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<your-premium-user-uuid>",
    "question": "I do not understand how MCP is different from just calling an API directly."
  }'
```

**Expected response** (200):
```json
{
  "mentor_response": "Great question! Let me check what chapter covers MCP...",
  "chapters_referenced": ["chapter-04"],
  "tools_used": ["get_chapter_content", "get_student_progress"],
  "estimated_cost_usd": 0.090
}
```

---

## 6. Run Integration Tests

```bash
cd backend   # or repo root, depending on pytest.ini location
pytest tests/integration/test_hybrid_assess_api.py tests/integration/test_hybrid_mentor_api.py -v
```

All 4 tests should pass. Real Gemini calls are mocked — no API key needed for tests.

---

## Architecture Separation Check

```bash
git diff main -- \
  backend/routers/chapters.py backend/routers/quizzes.py \
  backend/routers/progress.py backend/routers/search.py \
  backend/routers/access.py backend/routers/users.py
# Expected: (empty output — Phase 1 untouched)
```
