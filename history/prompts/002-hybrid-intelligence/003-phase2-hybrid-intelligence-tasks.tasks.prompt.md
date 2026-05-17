---
id: "003"
title: Phase 2 Hybrid Intelligence Task List
stage: tasks
date: 2026-05-17
surface: agent
model: claude-sonnet-4-6
feature: 002-hybrid-intelligence
branch: 002-hybrid-intelligence
user: Abu Bakar
command: /sp.tasks
labels: ["tasks","hybrid","gemini","openai-agents","fastapi","tdd","premium","phase2"]
links:
  spec: specs/002-hybrid-intelligence/spec.md
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - specs/002-hybrid-intelligence/tasks.md
tests:
  - tests/integration/test_hybrid_assess_api.py
  - tests/integration/test_hybrid_mentor_api.py
---

## Prompt

/sp.tasks (no additional arguments — feature context derived from current branch 002-hybrid-intelligence)

## Response snapshot

Generated `specs/002-hybrid-intelligence/tasks.md` with 21 tasks across 6 phases organized by user story:

- **Phase 1 Setup** (T001–T002): Add openai-agents dependency + GEMINI_API_KEY to .env.example
- **Phase 2 Foundational** (T003–T006): agents/__init__.py, llm_client.py with get_llm_model(), hybrid.py skeleton (router, 4 Pydantic models, _require_premium, _fetch_progress_summary), main.py 2-line update
- **Phase 3 US1** (T007–T010): TDD — write failing assess tests, create assessor_agent.py (ASSESSOR_SYSTEM_PROMPT + extract_json + run_assessment), wire /hybrid/assess endpoint, confirm green
- **Phase 4 US2** (T011–T014): TDD — write failing mentor tests, create mentor_agent.py (MENTOR_SYSTEM_PROMPT + tool closures + _extract_tool_calls + run_mentor), wire /hybrid/mentor endpoint, confirm green
- **Phase 5 US3** (T015–T017): Architecture separation git diff check + Phase 1 regression suite + health invariant
- **Phase 6 Polish** (T018–T021): Cost logging verification, full test run, quickstart validation, .gitignore check

10 of 21 tasks are parallelizable [P]. US1 and US2 implementation phases can run in parallel after Phase 2 completes.

## Outcome

- ✅ Impact: Complete dependency-ordered task list; each user story independently implementable and testable; TDD cycle enforced (tests written before implementation)
- 🧪 Tests: 6 test-related tasks (T007, T010, T011, T014, T016, T019); mock strategy for asyncio.to_thread specified in task descriptions
- 📁 Files: specs/002-hybrid-intelligence/tasks.md
- 🔁 Next prompts: /sp.implement to begin executing tasks; or /sp.analyze to validate artifact consistency
- 🧠 Reflection: Key implementation risk is the extract_json regex — the note at the bottom of tasks.md calls this out explicitly so it won't be missed during red phase

## Evaluation notes (flywheel)

- Failure modes observed: None — tasks.md generated cleanly from plan.md + spec.md + data-model.md context
- Graders run and results (PASS/FAIL): Format validation — all 21 tasks have checkbox + ID + labels + file path ✅
- Prompt variant (if applicable): "null"
- Next experiment: Confirm mock pattern for asyncio.to_thread works with the conftest.py fixture pattern during T007/T011 (red phase)
