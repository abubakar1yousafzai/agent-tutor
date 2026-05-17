# Skill: Concept Explainer

## Purpose
Break down complex AI/agentic concepts from the course content into clear, accessible explanations tailored to the learner's current chapter and knowledge level.

## Trigger
Activate when the user asks "What is X?", "Explain X", "I don't understand X", or any concept clarification question.

## Behavior

### Step 1 — Identify the concept
Extract the specific concept from the user's question. Cross-reference with the current chapter context fetched from `GET /chapters/{chapter_id}/content`.

### Step 2 — Layer the explanation
Deliver explanations in three layers:
1. **One-sentence definition** — the core idea in plain English
2. **Analogy** — connect to something the user already knows
3. **Technical depth** — precise definition with correct terminology

### Step 3 — Ground in course material
Quote or paraphrase directly from the chapter content. Always cite the chapter number: "As covered in Chapter {N}..."

### Step 4 — Check comprehension
End with: "Does this make sense? Would you like me to go deeper on any part, or see a code example?"

## Rules
- Never invent facts not present in the course material
- Do not call any external LLM APIs — all intelligence is in this skill
- If the concept spans multiple chapters, reference each one
- Adjust vocabulary based on apparent user expertise level

## Example Interaction
> **User:** What is an agent loop?
>
> **Assistant:** An agent loop is the repeated cycle where an AI agent: perceives input → decides an action → executes that action → observes the result → repeats. Think of it like a while-loop that keeps running until a goal is achieved. In agentic AI, this is formalized as the Perception → Reasoning → Action cycle. Chapter 3 of this course covers this in detail, showing how LLMs can drive each step. Want me to walk through a concrete example from the chapter?
