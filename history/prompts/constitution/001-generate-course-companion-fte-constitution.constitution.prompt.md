---
id: "001"
title: Generate Course Companion FTE Constitution
stage: constitution
date: 2026-05-01
surface: agent
model: claude-sonnet-4-6
feature: none
branch: master
user: Abu Bakar
command: /sp.constitution
labels: ["constitution","spec-driven-development","zero-backend-llm","agent-factory","course-companion-fte"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/001-generate-course-companion-fte-constitution.constitution.prompt.md
tests:
  - N/A (constitution authoring, no tests)
---

## Prompt

read Hackathon Ⅳ document and generate complete constitutiion file

## Response snapshot

Read the full `Hackathon IV.md` document (Course Companion FTE — Agent Factory Hackathon IV,
Version 1.0 January 2026) and the existing constitution template at
`.specify/memory/constitution.md`. Derived all project principles, technical stack,
phased architecture requirements, and governance rules from the document.

Generated and wrote a complete constitution to `.specify/memory/constitution.md` (v1.0.0)
with 7 core principles:

1. Zero-Backend-LLM Default (NON-NEGOTIABLE) — Phase 1 backend performs zero LLM calls
2. Spec-Driven Development (SDD) — all features begin as approved specs
3. Selective Hybrid Intelligence — Phase 2 LLM gated to premium, user-initiated, isolated endpoints
4. Agent Skills-First Design — educational behaviors in SKILL.md files; 4 required skills pre-launch
5. Phased Architecture Discipline — Phase 1 → 2 → 3 sequencing enforced
6. Cost-Conscious Engineering — $0.004/user/month Phase 1 budget; hybrid features monetized
7. Test-First Development (TDD) — Red-Green-Refactor cycle enforced; zero-LLM invariant CI gate

Also created `history/prompts/constitution/` directory and this PHR.

## Outcome

- ✅ Impact: Constitution v1.0.0 established; all 7 principles derived from Hackathon IV spec document; governs all future development on Course Companion FTE
- 🧪 Tests: N/A — constitution authoring task
- 📁 Files: `.specify/memory/constitution.md` (created/overwritten), `history/prompts/constitution/001-generate-course-companion-fte-constitution.constitution.prompt.md` (created)
- 🔁 Next prompts: `/sp.specify` to define Phase 1 features; `/sp.adr` for architectural decisions on tech stack and course topic selection
- 🧠 Reflection: Document was ~150K tokens; read in sections to extract all principles. Zero-Backend-LLM principle is the most critical constraint — should be a CI gate, not just a code review.

## Evaluation notes (flywheel)

- Failure modes observed: None — document was comprehensive and all required fields derivable
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add a `/sp.adr` for course topic selection (locks architecture early)
