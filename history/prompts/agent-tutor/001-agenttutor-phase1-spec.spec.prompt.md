---
id: "001"
title: AgentTutor Phase 1 Spec
stage: spec
date: 2026-05-01
surface: agent
model: claude-sonnet-4-6
feature: agent-tutor
branch: 001-agent-tutor
user: Abu Bakar
command: /sp.specify
labels: ["spec","agent-tutor","zero-backend-llm","course-companion-fte","phase-1","chatgpt-app"]
links:
  spec: specs/001-agent-tutor/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-agent-tutor/spec.md
  - specs/001-agent-tutor/checklists/requirements.md
  - history/prompts/agent-tutor/001-agenttutor-phase1-spec.spec.prompt.md
tests:
  - N/A (spec authoring, no code tests)
---

## Prompt

Build AgentTutor — an AI Agent Learning Companion that acts as a Digital
Full-Time Equivalent (FTE) educational tutor for the Panaversity Agent Factory
Hackathon IV. AgentTutor teaches students AI Agent Development topics including
Claude Agent SDK, Model Context Protocol (MCP), Agent Skills, and the Agent
Factory Architecture.

What We Are Building:
1. A FastAPI backend that serves course content, grades quizzes, tracks student
   progress, and enforces freemium access control — all without any LLM calls.
2. A ChatGPT App (OpenAI Apps SDK) that acts as the conversational frontend.

Core Architecture Rule (Non-Negotiable): Zero-Backend-LLM. Backend never calls
any LLM API. All intelligence lives inside ChatGPT.

Course Content: 10 chapters; chapters 1-3 free, 4-10 premium. Topics: What is an
AI Agent, Claude Agent SDK Basics, Building Your First Agent, Model Context
Protocol, Agent Skills and SKILL.md, Multi-Agent Collaboration, Agent Memory and
State, A2A Protocol, Agent Factory Architecture, Production Deployment.

6 Required Backend Features: Content Delivery, Navigation, Search, Quiz System
(rule-based grading), Progress Tracking (streaks), Freemium Access Gate.

Users: UUID-identified; free/premium tier; email, name, streak count, last active.

4 SKILL.md files: concept-explainer, quiz-master, socratic-tutor, progress-motivator.

Tech Stack: FastAPI/Python 3.12, Neon PostgreSQL, Cloudflare R2, OpenAI Apps SDK,
Fly.io.

## Response snapshot

Created branch `001-agent-tutor` via `.specify/scripts/powershell/create-new-feature.ps1`.
Wrote complete specification to `specs/001-agent-tutor/spec.md` with:

- 6 prioritized user stories covering all 6 required Phase 1 features
- 22 functional requirements (FR-001–FR-022) including the Zero-LLM invariant (FR-018)
- 5 key entities: Student, Chapter, Quiz, Progress Record, Skill
- 10 measurable success criteria (SC-001–SC-010)
- 6 edge cases documented
- Assumptions section with tech stack flagged as planning reference only
- Out-of-scope section with 9 explicit exclusions

Validation: all 14 quality checklist items PASS on first run. Zero [NEEDS CLARIFICATION]
markers — spec description was comprehensive. Checklist written to
`specs/001-agent-tutor/checklists/requirements.md`.

## Outcome

- ✅ Impact: Complete Phase 1 spec for AgentTutor; all 6 required hackathon features specified; Zero-LLM invariant formally captured in FR-018; ready for `/sp.plan`
- 🧪 Tests: N/A — spec authoring task; acceptance scenarios defined in user stories
- 📁 Files: `specs/001-agent-tutor/spec.md` (written), `specs/001-agent-tutor/checklists/requirements.md` (created, all PASS)
- 🔁 Next prompts: `/sp.plan` to generate architecture and technical decisions; `/sp.adr` for Zero-Backend-LLM architecture decision
- 🧠 Reflection: Spec description was thorough enough to resolve all clarification points as assumptions. Most critical constraint (FR-018: zero-LLM) is explicitly stated and verifiable by code audit.

## Evaluation notes (flywheel)

- Failure modes observed: None — create-new-feature.ps1 errored on extra args but branch was created successfully; script ran once as required
- Graders run and results (PASS/FAIL): Spec quality checklist — 14/14 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add quiz question count per chapter to spec before planning (currently deferred to Assumptions)
