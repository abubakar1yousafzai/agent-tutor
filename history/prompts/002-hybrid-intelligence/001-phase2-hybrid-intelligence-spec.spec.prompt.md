---
id: "001"
title: Phase 2 Hybrid Intelligence Spec
stage: spec
date: 2026-05-17
surface: agent
model: claude-sonnet-4-6
feature: 002-hybrid-intelligence
branch: 002-hybrid-intelligence
user: Abu Bakar
command: /sp.specify
labels: ["spec","hybrid","premium","gemini","openai-agents","fastapi","phase2"]
links:
  spec: specs/002-hybrid-intelligence/spec.md
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - specs/002-hybrid-intelligence/spec.md
  - specs/002-hybrid-intelligence/checklists/requirements.md
tests:
  - "null"
---

## Prompt

# AgentTutor Phase 2 — Hybrid Intelligence Add two premium hybrid intelligence features to the existing AgentTutor FastAPI backend. Phase 1 code must not be modified in any way. All new features are isolated in separate API routes, gated behind premium tier, and only triggered when the user explicitly requests them.## Technology Stack for Phase 2Use the OpenAI Agents SDK with Google Gemini as the LLM provider via the OpenAI Chat Completions compatible API. This is the exact pattern to follow for setting up the LLM client:
```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
import os
external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
llm_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
```
Add GEMINI_API_KEY to the .env file. All hybrid logic must live in a new file called backend/routers/hybrid.py. Import and register this router in main.py under the prefix /hybrid.

## Feature 1 — LLM Graded Assessment
POST /hybrid/assess — premium student submits free-form written answer; Gemini grades it and returns score, grade, feedback, what_was_correct, what_was_missing, improvement_tip, estimated_cost_usd (0.014). Free users get 403.

## Feature 2 — AI Mentor Agent
POST /hybrid/mentor — premium student asks a complex question; agent uses two tools (get_chapter_content, get_student_progress) to personalise a Socratic response. Returns mentor_response, chapters_referenced, tools_used, estimated_cost_usd (0.090). Free users get 403. Agent must use at least one tool.

New dependency: openai-agents in requirements.txt. New env var: GEMINI_API_KEY in .env.example. Integration tests required for both endpoints.

## Response snapshot

Created branch `002-hybrid-intelligence` and wrote full specification to `specs/002-hybrid-intelligence/spec.md`. Specification covers:
- 3 user stories (P1: LLM Assessment, P2: AI Mentor, P3: Tier Enforcement)
- 8 acceptance scenarios total across all stories
- 6 edge cases (parse failure, timeout, new student, malformed chapter, concurrent requests, path traversal)
- 14 functional requirements (FR-001 through FR-014), all testable
- 7 key entities (AssessmentRequest/Response, MentorRequest/Response, User, Chapter, StudentProgress)
- 6 success criteria (SC-001 through SC-006) — measurable, technology-agnostic
- Explicit Assumptions and Out of Scope sections

Quality checklist created at `specs/002-hybrid-intelligence/checklists/requirements.md` — all items pass, no clarification questions required.

## Outcome

- ✅ Impact: Full Phase 2 specification written; no Phase 1 artifacts touched; all 14 FRs traceable to user stories and success criteria
- 🧪 Tests: No tests written at spec stage; integration test requirements captured in FR-014 and SC-004
- 📁 Files: specs/002-hybrid-intelligence/spec.md, specs/002-hybrid-intelligence/checklists/requirements.md
- 🔁 Next prompts: /sp.plan to generate architecture and design decisions; /sp.clarify if any ambiguity surfaces during planning
- 🧠 Reflection: Feature description was exceptionally complete — zero clarification markers needed. The main design tension is Runner.run_sync() in an async FastAPI context; flagged as an assumption for the plan stage.

## Evaluation notes (flywheel)

- Failure modes observed: create-new-feature.ps1 threw a positional-parameter error on the -Description arg but still created branch and directory successfully; script was idempotent
- Graders run and results (PASS/FAIL): Quality checklist — all 16 items PASS
- Prompt variant (if applicable): "null"
- Next experiment: Verify Runner.run_sync() compatibility in FastAPI async context during /sp.plan
