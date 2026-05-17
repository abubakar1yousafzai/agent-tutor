# Chapter 5: Agent Skills and SKILL.md

## Learning Objectives
- Understand what Agent Skills are and why they matter
- Learn the SKILL.md specification format
- Design skills for common agentic behaviors
- Integrate SKILL.md files into ChatGPT App / GPT Actions

---

## 5.1 What are Agent Skills?

An **Agent Skill** is a behavioral specification that defines how an AI agent performs a specific, repeatable task. Skills encode expert knowledge about:
- When to activate (trigger conditions)
- How to execute step-by-step (workflow)
- What guardrails to apply (constraints)
- How to handle edge cases (error handling)

Skills bridge the gap between a general-purpose LLM and a specialized, production-ready agent behavior.

---

## 5.2 The SKILL.md Format

SKILL.md files are markdown documents that define a single skill. They are loaded into the AI's context and guide its behavior for that skill domain.

### Required Sections

```markdown
# Skill: {Name}

## Purpose
One-sentence description of what this skill accomplishes.

## Trigger
When does this skill activate? (user phrases, context signals)

## Behavior
Step-by-step workflow the agent follows when this skill is active.

## Rules
Invariants and constraints that must never be violated.

## Example Interaction
A concrete example showing the skill in action.
```

### Optional Sections
- **Prerequisites:** What must be true before this skill can run
- **Error Handling:** How to recover from failures
- **Metrics:** What success looks like (e.g., user confirms understanding)

---

## 5.3 Designing Effective Skills

### Principle 1: Single Responsibility
Each SKILL.md should do one thing well. Avoid skills that try to handle multiple unrelated tasks.

Bad: "Answer questions AND quiz users AND track progress"
Good: Three separate skills: Concept Explainer, Quiz Master, Progress Motivator

### Principle 2: Explicit Workflow
The workflow section should be so clear that any LLM following it produces consistent behavior.

```markdown
## Behavior

### Step 1 — Identify the concept
Extract the specific term from the user's question.

### Step 2 — Layer the explanation
1. One-sentence definition
2. Analogy to familiar concept
3. Technical precise definition

### Step 3 — Check comprehension
"Does this make sense? Want me to go deeper?"
```

### Principle 3: Grounded Constraints
Rules must be grounded in real requirements, not vague preferences.

```markdown
## Rules
- Never reveal quiz answers before submission (grading integrity)
- Always cite chapter number when referencing content (traceability)
- Do not call external LLM APIs (Zero-Backend-LLM constraint)
```

---

## 5.4 Skills in the Agent Factory

In the Agent Factory Architecture, SKILL.md files are first-class artifacts:

```
General Agent (Claude Code)
      │
      ▼
[Specs + SKILL.md files]
      │
      ▼
Custom Agent (Course Companion FTE)
  ├── concept-explainer/SKILL.md
  ├── quiz-master/SKILL.md
  ├── socratic-tutor/SKILL.md
  └── progress-motivator/SKILL.md
```

The General Agent manufactures the Custom Agent by combining:
1. API backend (FastAPI + PostgreSQL)
2. SKILL.md behavioral specs
3. ChatGPT App manifest

---

## 5.5 ChatGPT App Integration

SKILL.md files are referenced in the ChatGPT App manifest:

```yaml
skills:
  - name: quiz-master
    description: Administers chapter quizzes and grades responses.
    trigger_phrases:
      - "quiz me"
      - "test me on chapter"
    skill_file: skills/quiz-master/SKILL.md
```

When a user says "quiz me on Chapter 3," the ChatGPT App loads the quiz-master SKILL.md and executes its workflow — calling the FastAPI backend for questions and submitting answers.

---

## 5.6 Skills vs. Tools vs. Prompts

| Concept | Scope | Definition Location | Runtime |
|---------|-------|--------------------|-|
| **Tool** | Single function call | Python function / MCP server | Backend |
| **Prompt** | Single API call | System prompt string | LLM context |
| **Skill** | Multi-step workflow | SKILL.md file | LLM behavior |

Skills are higher-level than prompts. A skill may invoke multiple tools, ask clarifying questions, and adapt its behavior based on user responses — all within a defined workflow.

---

## Summary

- Agent Skills define how an AI performs specific tasks reproducibly
- SKILL.md is a markdown format encoding trigger, workflow, rules, and examples
- Good skills have single responsibility, explicit workflows, and grounded constraints
- In the Agent Factory, SKILL.md files are manufactured artifacts, not afterthoughts
- ChatGPT App manifest wires skill files to trigger phrases and API calls

**Next:** Chapter 6 — Multi-Agent Collaboration
