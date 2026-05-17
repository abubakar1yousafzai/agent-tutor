# Chapter 8: A2A Protocol

## Learning Objectives
- Understand what A2A (Agent-to-Agent) protocol is
- Learn the A2A specification: Agent Cards, tasks, and streaming
- Implement a simple A2A server
- Connect agents across different vendors and platforms

---

## 8.1 The A2A Problem

As multi-agent systems scale, agents built by different teams and vendors need to communicate. Without a standard:
- Agent A (built by Team X, using Claude) can't discover Agent B (built by Team Y, using GPT-4)
- Handoff formats are proprietary and incompatible
- Trust and authentication vary per integration
- Debugging inter-agent communication is opaque

**A2A Protocol** solves this by defining a standard HTTP-based communication layer between agents, regardless of their underlying LLM or framework.

---

## 8.2 Core A2A Concepts

### Agent Card
A JSON document that describes an agent's capabilities, endpoints, and authentication requirements. Published at a well-known URL.

```json
{
  "name": "Research Agent",
  "description": "Performs web research and produces structured summaries",
  "version": "1.0.0",
  "url": "https://research-agent.example.com",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": true
  },
  "skills": [
    {
      "id": "web-research",
      "name": "Web Research",
      "description": "Research a topic and return a summary",
      "inputModes": ["text"],
      "outputModes": ["text", "data"]
    }
  ],
  "authentication": {
    "schemes": ["Bearer"]
  }
}
```

### Task
The unit of work in A2A. A task has a lifecycle: `submitted` → `working` → `completed` (or `failed`/`canceled`).

```json
{
  "id": "task-uuid-here",
  "status": {"state": "working"},
  "message": {
    "role": "user",
    "parts": [{"type": "text", "text": "Research the history of Python"}]
  }
}
```

### Message Parts
A2A uses a flexible "parts" format for messages, supporting text, files, and structured data:

```json
{"type": "text", "text": "Here is the summary..."}
{"type": "file", "file": {"mimeType": "application/pdf", "uri": "https://..."}}
{"type": "data", "data": {"key": "value"}}
```

---

## 8.3 A2A Communication Flow

```
Client Agent                    Server Agent
     │                               │
     │  POST /tasks/send             │
     │  {message: {role: "user"...}} │
     │ ─────────────────────────────► │
     │                               │ [processes task]
     │  {"id": "task-123",           │
     │   "status": "submitted"}      │
     │ ◄───────────────────────────── │
     │                               │
     │  GET /tasks/task-123          │
     │ ─────────────────────────────► │
     │                               │
     │  {"status": "completed",      │
     │   "artifacts": [...]}         │
     │ ◄───────────────────────────── │
```

---

## 8.4 Streaming with Server-Sent Events

For long-running tasks, A2A supports SSE streaming:

```
Client Agent                    Server Agent
     │                               │
     │  POST /tasks/sendSubscribe    │
     │ ─────────────────────────────► │
     │                               │
     │  event: task_status_update    │
     │  data: {"state": "working"}   │
     │ ◄───────────────────────────── │
     │                               │
     │  event: artifact_update       │
     │  data: {"parts": [...]}       │
     │ ◄───────────────────────────── │
     │                               │
     │  event: task_status_update    │
     │  data: {"state": "completed"} │
     │ ◄───────────────────────────── │
```

---

## 8.5 Implementing an A2A Server

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uuid, json, asyncio

app = FastAPI()

tasks_store: dict[str, dict] = {}

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "MyAgent",
        "version": "1.0.0",
        "url": "https://myagent.example.com",
        "capabilities": {"streaming": True},
        "skills": [{"id": "chat", "name": "Chat", "inputModes": ["text"]}],
    }

@app.post("/tasks/send")
async def send_task(payload: dict):
    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {"id": task_id, "status": {"state": "submitted"}}
    # In production: queue task for async processing
    asyncio.create_task(process_task(task_id, payload))
    return tasks_store[task_id]

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = tasks_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404)
    return task

async def process_task(task_id: str, payload: dict):
    tasks_store[task_id]["status"] = {"state": "working"}
    # Run the agent...
    result = "Processed: " + str(payload)
    tasks_store[task_id]["status"] = {"state": "completed"}
    tasks_store[task_id]["artifacts"] = [{"parts": [{"type": "text", "text": result}]}]
```

---

## Summary

- A2A standardizes inter-agent communication across vendors and frameworks
- Agent Cards are self-describing capability manifests at `/.well-known/agent.json`
- Tasks are the unit of work: `submitted` → `working` → `completed`
- Message parts support text, files, and structured data
- SSE streaming enables real-time progress updates for long-running tasks
- A2A + MCP together create a fully interoperable agentic ecosystem

**Next:** Chapter 9 — Agent Factory Architecture
