<!-- SYNC IMPACT REPORT
  Version change: [TEMPLATE] → 1.0.0
  Modified principles: N/A (initial creation)
  Added sections:
    - Core Principles (7 principles)
    - Technical Stack & Constraints
    - Development Workflow
    - Governance
  Removed sections: N/A (template placeholders removed)
  Templates checked:
    - .specify/templates/plan-template.md ✅ Constitution Check section present, aligns with principles
    - .specify/templates/spec-template.md ✅ No conflicting mandatory sections
    - .specify/templates/tasks-template.md ✅ Task categories align with phased architecture
    - .specify/templates/phr-template.prompt.md ✅ No conflicting guidance
  Deferred TODOs: None — all required fields populated.
-->

# Course Companion FTE Constitution

## Core Principles

### I. Zero-Backend-LLM Default (NON-NEGOTIABLE)

The backend MUST perform zero LLM API calls in Phase 1. All reasoning, explanation,
tutoring, adaptation, and intelligence is delegated to the ChatGPT App frontend.
The backend is strictly deterministic: it serves content verbatim from storage,
grades quizzes via answer keys, tracks progress, enforces access control, and
performs keyword/embedding search.

Any Phase 1 backend containing LLM API calls, RAG summarization, prompt
orchestration, or agent loops constitutes an immediate disqualification.
Detection is via code review and API audit.

**Rationale:** Zero-LLM default achieves near-zero marginal cost per user
(~$0.002–$0.004/user/month at 10K users), predictable scaling to 100K+ users,
and compliance auditability — without sacrificing educational quality, since
ChatGPT provides all tutoring intelligence client-side.

### II. Spec-Driven Development (SDD)

All features MUST begin as an approved spec before any code is written. Claude Code
(General Agent) manufactures the Custom Agent (Course Companion FTE) from the spec.
The spec is the source of truth; if a behavior is not in the spec, it MUST NOT be
implemented. Scope creep is rejected at the spec review gate.

Spec artifacts for every feature:
- `specs/<feature>/spec.md` — requirements and acceptance criteria
- `specs/<feature>/plan.md` — architecture and technical decisions
- `specs/<feature>/tasks.md` — testable tasks with test cases

**Rationale:** Spec-Driven Development ensures the General Agent (Claude Code)
manufactures exactly the product described. It prevents scope creep, keeps changes
small and reviewable, and provides a durable audit trail for every decision.

### III. Selective Hybrid Intelligence

Backend LLM integration is ONLY permitted in Phase 2, and MUST satisfy ALL five
conditions before implementation:

1. **Educational value** — demonstrably adds value beyond what zero-LLM can deliver
2. **Premium-gated** — restricted to paid users (Pro tier or higher); MUST NOT be
   required for core Phase 1 UX
3. **User-initiated** — MUST be explicitly triggered by the user; auto-triggering is
   forbidden
4. **Architecturally isolated** — hybrid routes MUST be separate API endpoints from
   Phase 1 routes; Phase 1 routes MUST remain LLM-free
5. **Cost-tracked** — per-user cost analysis MUST be documented before shipping

Maximum 2 hybrid features per Phase 2 release. Allowed feature set:
Adaptive Learning Path, LLM-Graded Assessments, Cross-Chapter Synthesis, AI Mentor Agent.

**Rationale:** Hybrid intelligence introduces real operational burden, cost variability,
and hallucination risk. Constraining it to proven, premium, isolated use cases preserves
the cost model while enabling advanced tutoring for paying users.

### IV. Agent Skills-First Design

All educational behaviors are encapsulated in SKILL.md files before the agent runs in
production. The four required runtime skills MUST be implemented before Phase 1 launch:

| Skill | Trigger Keywords |
|---|---|
| `concept-explainer` | "explain", "what is", "how does" |
| `quiz-master` | "quiz", "test me", "practice" |
| `socratic-tutor` | "help me think", "I'm stuck" |
| `progress-motivator` | "my progress", "streak", "how am I doing" |

Each SKILL.md MUST contain: Metadata, Purpose, Workflow, Response Templates, Key Principles.

**Rationale:** Skills encode the FTE's pedagogy in version-controlled, reviewable files.
They enable consistent 99%+ educational delivery at scale and allow instant ramp-up
via SKILL.md — eliminating training time compared to human tutors.

### V. Phased Architecture Discipline

Development MUST follow the mandated phase sequence:

- **Phase 1** — Zero-Backend-LLM: ChatGPT App + Deterministic FastAPI backend + R2 storage
- **Phase 2** — Hybrid Intelligence: Phase 1 intact + isolated LLM-gated premium endpoints
- **Phase 3** — Full Web App: Next.js frontend + consolidated FastAPI backend (all features)

Phase 2 features MUST NOT appear in Phase 1 code. Phase 3 delivers a standalone web app
with a single API surface (no code-sharing requirement with ChatGPT App).

The 8-layer Agent Factory architecture governs Phase 2+:
L0 (gVisor) → L1 (Kafka) → L2 (Dapr) → L3 (FastAPI) → L4 (OpenAI SDK) →
L5 (Claude SDK) → L6 (Skills + MCP) → L7 (A2A Protocol).

**Rationale:** Phased delivery de-risks the project. Phase 1 proves core value at
minimal cost; Phase 2 introduces intelligence only where justified; Phase 3 extends
reach via an independent web surface.

### VI. Cost-Conscious Engineering

Every architectural decision MUST include a cost justification. Budgets:

- Phase 1: ≤ $0.004/user/month at 10K concurrent users (infra only; LLM cost = $0)
- Phase 2 hybrid features: MUST be monetized at Pro ($19.99/mo) or Team ($49.99/mo) tier;
  cost per hybrid request MUST be documented before shipping
- No hybrid feature may be auto-triggered in a way that generates unbounded cost

Cost analysis is a required deliverable alongside every Phase 2 feature.

**Rationale:** The Digital FTE thesis depends on 85-90% cost savings vs human tutors.
Unconstrained LLM usage destroys the business model. Cost discipline ensures the platform
remains viable at scale.

### VII. Test-First Development (TDD)

Tests MUST be written before implementation and approved by the team before code is
written. The Red-Green-Refactor cycle is enforced:

1. **Red** — Write failing tests; tests MUST be approved before proceeding
2. **Green** — Implement until all tests pass; no scope beyond what tests require
3. **Refactor** — Improve code quality while tests remain green

Required test coverage:
- Unit tests for all service and utility functions
- Integration tests for all API contracts (Content, Navigation, Quiz, Progress, Search,
  Access Control)
- The Zero-Backend-LLM invariant MUST be verified by a dedicated test or CI gate in Phase 1

**Rationale:** Test-first ensures correctness before deployment, prevents regressions
when phasing from Phase 1 to Phase 2, and provides a verifiable definition of done
for every feature task.

## Technical Stack & Constraints

**Mandatory stack (non-negotiable per hackathon requirements):**

| Layer | Technology | Phase |
|---|---|---|
| Backend API | FastAPI (Python 3.11+) | 1, 2, 3 |
| ChatGPT Frontend | OpenAI Apps SDK | 1, 2 |
| Web Frontend | Next.js / React | 3 |
| Content Storage | Cloudflare R2 | 1, 2, 3 |
| Database | Neon or Supabase (PostgreSQL) | 1, 2, 3 |
| LLM (Hybrid only) | Claude Sonnet (Anthropic) | 2, 3 |
| Agent Orchestration | OpenAI Agents SDK / Claude Agent SDK | 2, 3 |
| Event Backbone | Apache Kafka | 2, 3 |
| Infrastructure | Dapr + Workflows | 2, 3 |
| Sandbox | gVisor (agent execution) | 2, 3 |

**Course topic:** Teams choose ONE: AI Agent Development, Cloud-Native Python,
Generative AI Fundamentals, or Modern Python. The choice is locked at spec ratification.

**Secrets and configuration:** MUST use `.env` files; no hardcoded secrets or tokens
in source code. API keys, database URLs, and LLM credentials are environment variables only.

**API documentation:** All backend APIs MUST be documented with OpenAPI/Swagger.
The ChatGPT App MUST have a valid manifest YAML.

## Development Workflow

1. **Spec** — Define feature requirements in `specs/<feature>/spec.md` via `/sp.specify`
2. **Plan** — Architecture and technical decisions in `specs/<feature>/plan.md` via `/sp.plan`
3. **Tasks** — Testable tasks with acceptance criteria in `specs/<feature>/tasks.md` via `/sp.tasks`
4. **Red** — Write failing tests; team approval required before proceeding via `/sp.tasks` red phase
5. **Green** — Implement until tests pass; smallest viable change only
6. **Refactor** — Improve code quality while tests remain green

**Pull Request gates:**
- Constitution Check: zero-LLM invariant verified for Phase 1 PRs
- All tests pass (unit + integration)
- API documentation updated
- No hardcoded secrets detected
- PHR created for the associated prompt session

**Deliverables required at submission:**
- GitHub repository with complete source code and README
- Architecture diagram (PNG/PDF)
- Spec document (Markdown)
- Cost analysis (Markdown/PDF)
- Demo video (MP4, ≤5 min)
- OpenAPI/Swagger documentation
- ChatGPT App manifest (YAML)

## Governance

This constitution supersedes all other practices, coding standards, and verbal agreements
on the Course Companion FTE project. Any deviation requires a documented amendment.

**Amendment procedure:**
1. Author proposes change with rationale in a PR against this file
2. At least one team review and approval required
3. Version number incremented per semantic versioning:
   - MAJOR: backward-incompatible removal or redefinition of a principle
   - MINOR: new principle, section, or materially expanded guidance
   - PATCH: clarification, wording fix, or non-semantic refinement
4. `LAST_AMENDED_DATE` updated to the amendment date

**Compliance:** All PRs and code reviews MUST verify compliance with:
- Principle I (Zero-Backend-LLM gate for Phase 1)
- Principle III (Hybrid isolation and gating)
- Principle VII (TDD cycle)

Complexity violations MUST be justified in the plan's Complexity Tracking section.
Use `CLAUDE.md` for runtime agent guidance on tool use and SDD workflows.

**Version**: 1.0.0 | **Ratified**: 2026-05-01 | **Last Amended**: 2026-05-01
