---
id: "003"
title: AgentTutor Phase 1 Tasks
stage: tasks
date: 2026-05-01
surface: agent
model: claude-sonnet-4-6
feature: agent-tutor
branch: 001-agent-tutor
user: Abu Bakar
command: /sp.tasks
labels: ["tasks","agent-tutor","tdd","zero-backend-llm","fastapi","phase-1"]
links:
  spec: specs/001-agent-tutor/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-agent-tutor/tasks.md
  - history/prompts/agent-tutor/003-agenttutor-phase1-tasks.tasks.prompt.md
tests:
  - N/A (tasks authoring; test strategy embedded in tasks.md)
---

## Prompt

(empty — /sp.tasks invoked with no additional arguments; derives tasks from available
design documents: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml,
quickstart.md)

## Response snapshot

Ran `check-prerequisites.ps1 -Json` → FEATURE_DIR confirmed, all 4 optional docs present.
Loaded tasks-template.md, spec.md (US1–US6 P1–P6), plan.md (project structure + tech stack),
data-model.md (5 tables + streak/grading logic), contracts/openapi.yaml (16 endpoints).

Generated `specs/001-agent-tutor/tasks.md` with 48 tasks across 9 phases:

- Phase 1 (Setup, T001–T005): project structure, requirements.txt, .env.example, Dockerfile, fly.toml
- Phase 2 (Foundation, T006–T013): config, DB connection, tables, seed, R2 client, main.py, conftest, zero-LLM invariant test
- Phase 3 (US1 P1, T014–T021): content delivery + user management + freemium gate (3 test + 5 impl)
- Phase 4 (US2 P2, T022–T026): quiz questions + rule-based grading (2 test + 3 impl)
- Phase 5 (US3 P3, T027–T030): progress tracking + streak calculation (2 test + 2 impl)
- Phase 6 (US4 P4, T031–T032): sequential navigation (1 test + 1 impl)
- Phase 7 (US5 P5, T033–T035): keyword search with tier scoping (1 test + 2 impl)
- Phase 8 (US6 P6, T036–T037): dedicated access check + tier info endpoints (1 test + 1 impl)
- Phase 9 (Polish, T038–T048): contract tests, 4 SKILL.md files, ChatGPT manifest, sample content, docs, full validation

TDD enforced per Constitution Principle VII — test tasks precede all implementation tasks
within each user story phase. T013 (zero-LLM invariant static analysis test) runs first
before any other test.

## Outcome

- ✅ Impact: 48 implementation-ready tasks spanning all 6 Phase 1 features; TDD enforced throughout; MVP = Phases 1+2+3 only; all tasks have exact file paths
- 🧪 Tests: 10 test-writing tasks (T013–T016, T022–T023, T027–T028, T031, T033, T036, T038); zero-LLM invariant test (T013) is first gate
- 📁 Files: `specs/001-agent-tutor/tasks.md` (created)
- 🔁 Next prompts: `/sp.implement` to start executing tasks; `/sp.adr zero-backend-llm-enforcement` for the CI gate decision
- 🧠 Reflection: US4 (navigation) depends on the same chapters.py router as US1, so T032 is an extension not a new file — kept in separate phase for independent testability. US3 (progress) has a soft dependency on US1 (users must exist) captured in the dependency table.

## Evaluation notes (flywheel)

- Failure modes observed: None — all prerequisite docs were present; check-prerequisites.ps1 ran cleanly
- Graders run and results (PASS/FAIL): Format validation — 48/48 tasks follow checklist format (checkbox + ID + optional P + optional USN + description + file path)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider splitting T009 (seed.py) into T009a (create tables) and T009b (seed quiz bank) for more granular task tracking
