# Chapter 1: What is an AI Agent

## Learning Objectives
By the end of this chapter, you will understand:
- What distinguishes an AI agent from a simple script or chatbot
- The agent loop: Perception → Reasoning → Action
- Key components: tools, memory, planning, and action
- Real-world examples of AI agents in production

---

## 1.1 Defining an AI Agent

An **AI agent** is a system that perceives its environment, reasons about what to do, and takes actions to achieve a goal — autonomously, over multiple steps.

This is fundamentally different from a chatbot that simply responds to a prompt. A chatbot is stateless and reactive. An agent is **goal-directed** and **proactive**.

> *"An agent is an entity that perceives its environment and takes actions that maximize its chances of achieving its goals."*
> — Russell & Norvig, Artificial Intelligence: A Modern Approach

### Key distinction: Tool use

The capability that unlocks agency is **tool use** (also called function calling). When an LLM can call external functions — search the web, write a file, query a database, send an email — it transitions from a language model into an agent.

---

## 1.2 The Agent Loop

Every AI agent operates through a continuous cycle:

```
┌─────────────────────────────────────────────┐
│                 AGENT LOOP                  │
│                                             │
│  [Environment] ──► PERCEIVE ──► REASON      │
│       ▲                           │         │
│       └────────── ACT ◄───────────┘         │
└─────────────────────────────────────────────┘
```

**Perceive:** The agent reads its inputs — user messages, tool results, database records, sensor data.

**Reason:** The LLM at the core of the agent processes the perceived inputs and decides what to do next. This may involve planning, tool selection, or direct response.

**Act:** The agent executes the chosen action — calling a tool, generating a response, modifying state, or asking a clarifying question.

This loop repeats until the agent's goal is achieved or a stopping condition is met.

---

## 1.3 Core Agent Components

### 1. The LLM "Brain"
The language model provides reasoning capabilities. Modern agents use models like Claude, GPT-4, or Gemini as their reasoning core.

### 2. Tools
Functions the agent can invoke to interact with the world:
- `web_search(query)` — retrieve current information
- `read_file(path)` — access file system
- `execute_code(code)` — run Python or shell commands
- `call_api(url, payload)` — interact with external services

### 3. Memory
Agents need memory to maintain context across steps:
- **In-context memory:** Information in the current conversation window
- **External memory:** Databases, vector stores, files
- **Episodic memory:** Records of past interactions

### 4. Planning
For complex tasks, agents decompose goals into subtasks and execute them in sequence or parallel.

---

## 1.4 Agent Types

| Type | Description | Example |
|------|-------------|---------|
| **Reactive** | Responds to inputs without planning | Simple chatbot with tools |
| **Deliberative** | Plans multi-step sequences | Code-writing agent |
| **Autonomous** | Operates independently over time | Research agent |
| **Multi-agent** | Coordinates with other agents | Agent Factory |

---

## 1.5 Why Agents Now?

Three factors converged to make agents viable in 2024–2025:

1. **Instruction-following LLMs** — Models that reliably follow structured prompts and use tools correctly
2. **Structured outputs** — JSON-mode and tool_use APIs that make tool calls deterministic
3. **Faster inference** — Response times under 2 seconds enable real-time agentic loops

---

## Summary

- An AI agent is a goal-directed system that perceives, reasons, and acts
- The agent loop (Perceive → Reason → Act) is the fundamental execution model
- Tool use is the capability that distinguishes agents from chatbots
- Agents have four core components: LLM brain, tools, memory, and planning
- Multiple agent types exist, from reactive to fully autonomous

**Next:** Chapter 2 — Claude Agent SDK Basics
