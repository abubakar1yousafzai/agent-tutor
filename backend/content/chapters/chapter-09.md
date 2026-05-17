# Chapter 9: Agent Factory Architecture

## Learning Objectives
- Understand the Agent Factory pattern and its meta-agentic role
- Learn how General Agents manufacture Custom Agents from specs
- Implement a Spec-Driven Development (SDD) workflow
- Apply the Agent Factory to the Panaversity Hackathon IV challenge

---

## 9.1 The Agent Factory Concept

Traditional software development: humans write code → deploy application.

**Agent Factory:** A General Agent (like Claude Code) reads specifications → manufactures a Custom Agent → deploys it.

```
┌──────────────────────────────────────────────┐
│            AGENT FACTORY                     │
│                                              │
│  [Constitution]──┐                           │
│  [Spec]──────────┤                           │
│  [Plan]──────────┼──► General Agent ──► Custom Agent │
│  [Tasks]─────────┤    (Claude Code)    (FTE)        │
│  [SKILL.md]──────┘                           │
└──────────────────────────────────────────────┘
```

The General Agent is the **factory**. The Custom Agent is the **product**. Specifications are the **blueprints**.

---

## 9.2 Spec-Driven Development (SDD)

SDD is the methodology that powers the Agent Factory:

```
Constitution → Spec → Plan → Tasks → Red → Green → Refactor
```

### Stage 1: Constitution
Project-wide principles, technology choices, and non-negotiables. Written once, referenced always.

```markdown
# Principle I: Zero-Backend-LLM
The backend makes ZERO LLM API calls. Violation = disqualification.
```

### Stage 2: Spec (Specification)
Feature requirements written as user stories with acceptance criteria.

```markdown
## US1: Content Delivery
As a student, I want to read AI course chapters via a structured API
so that I can learn agentic AI concepts progressively.

### Acceptance Criteria
- FR-001: GET /chapters returns all chapters with accessibility flags
- FR-002: GET /chapters/{id}/content returns markdown for accessible chapters
- FR-003: Chapters 1–3 free; 4–10 premium only
```

### Stage 3: Plan
Architecture decisions, data model, API contracts, and file structure.

### Stage 4: Tasks
Atomic, testable tasks with explicit file paths and dependency chains.

```markdown
## T011 [P2-infra]
Create `backend/main.py`:
- Comment: `# Zero-Backend-LLM Architecture`
- FastAPI app with lifespan → `create_all_tables()`
- CORSMiddleware from settings
- Register 6 routers
- GET /health → {"status": "ok", "llm_calls": 0}
```

### Stage 5: Red → Green → Refactor (TDD)
- **Red:** Write failing tests first
- **Green:** Write minimal code to pass tests
- **Refactor:** Improve code quality without changing behavior

---

## 9.3 The FTE (Full-Time Employee) Agent Model

A **Course Companion FTE** is not just a chatbot — it's a specialized agent that behaves like a dedicated human tutor:

| Human Tutor | FTE Agent |
|-------------|-----------|
| Explains concepts | concept-explainer SKILL.md |
| Quizzes students | quiz-master SKILL.md |
| Uses Socratic method | socratic-tutor SKILL.md |
| Motivates learners | progress-motivator SKILL.md |
| Tracks progress | FastAPI backend + PostgreSQL |
| Enforces curriculum | Freemium access control |

The FTE agent is always available, never tired, infinitely patient, and costs a fraction of a human tutor.

---

## 9.4 Applying Agent Factory to Hackathon IV

The Panaversity Agent Factory Hackathon IV challenge:

**Task:** Build a Course Companion FTE using the Agent Factory architecture.

**Constraint:** Zero-Backend-LLM — backend is a dumb data API; all intelligence in the ChatGPT App.

**Solution Architecture:**
```
ChatGPT App (Intelligence)
├── SKILL.md files (4 behavioral specs)
├── GPT Actions → FastAPI backend
│
FastAPI Backend (Data)
├── PostgreSQL (Neon) — users, progress, quiz_bank
├── Local filesystem — chapter markdown content
└── Zero LLM calls (enforced by AST test)
```

**Why this matters:** Proves agents can deliver educational value without direct LLM API calls on the backend — the LLM intelligence is "pushed up" to the client (ChatGPT App).

---

## 9.5 Meta-Agentic Systems

The Agent Factory is itself a **meta-agent** — an agent that creates other agents.

```python
class AgentFactory:
    """A General Agent that manufactures Custom Agents from specifications."""
    
    async def manufacture(self, spec: AgentSpec) -> CustomAgent:
        constitution = await self.read_constitution()
        plan = await self.create_plan(spec, constitution)
        tasks = await self.generate_tasks(plan)
        
        agent = CustomAgent()
        for task in tasks:
            await self.execute_task(task, agent)
            await self.run_tests(task, agent)
        
        await self.validate_against_spec(agent, spec)
        return agent
```

This recursive structure — agents manufacturing agents — is the frontier of agentic AI.

---

## Summary

- Agent Factory: General Agent reads specs → manufactures Custom Agent (FTE)
- SDD workflow: Constitution → Spec → Plan → Tasks → TDD
- FTEs replace specialized human roles with always-available AI agents
- Hackathon IV demonstrates Zero-Backend-LLM architecture (intelligence at the ChatGPT App layer)
- Meta-agentic systems (agents manufacturing agents) are the next frontier

**Next:** Chapter 10 — Production Deployment
