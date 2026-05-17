# Chapter 6: Multi-Agent Collaboration

## Learning Objectives
- Understand orchestrator–worker agent patterns
- Design handoffs between specialized agents
- Handle shared state and context in multi-agent systems
- Build a pipeline of collaborating agents

---

## 6.1 Why Multiple Agents?

A single agent handling a complex task faces fundamental limits:
- **Context window saturation** — long tasks exceed the model's memory
- **Specialization gaps** — one agent can't be expert at everything
- **Parallelism** — sequential agents are slow for independent subtasks

Multi-agent collaboration solves these by dividing work among specialized agents that each excel at a specific domain.

---

## 6.2 Orchestrator–Worker Pattern

The most common multi-agent pattern:

```
User Request
     │
     ▼
┌──────────────┐
│ ORCHESTRATOR │  ← Plans, coordinates, aggregates
│   Agent      │
└──────┬───────┘
       │ delegates subtasks
  ┌────┼────┬────────┐
  ▼    ▼    ▼        ▼
[Research][Code][Review][Test]
 Worker  Worker Worker  Worker
```

### Orchestrator responsibilities
- Parse the user's high-level goal into subtasks
- Select the appropriate worker for each subtask
- Pass context between workers
- Aggregate results into a final response
- Handle worker failures gracefully

### Worker responsibilities
- Accept a specific, well-defined task
- Execute it with full expertise
- Return a structured result
- Report failures clearly

---

## 6.3 Implementing Agent Handoffs

A **handoff** transfers control and context from one agent to another.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class HandoffPayload:
    source_agent: str
    target_agent: str
    task: str
    context: dict[str, Any]
    artifacts: list[str]  # file paths, IDs, etc.

class OrchestratorAgent:
    def __init__(self, workers: dict[str, "WorkerAgent"]):
        self.workers = workers
        self.client = Anthropic()
    
    async def run(self, user_request: str) -> str:
        plan = await self._create_plan(user_request)
        results = {}
        
        for step in plan:
            worker = self.workers[step["worker"]]
            payload = HandoffPayload(
                source_agent="orchestrator",
                target_agent=step["worker"],
                task=step["task"],
                context={**results},  # pass accumulated results
                artifacts=step.get("artifacts", []),
            )
            results[step["id"]] = await worker.execute(payload)
        
        return await self._synthesize(results, user_request)
```

---

## 6.4 Context Sharing Strategies

Workers need context from prior steps. Three strategies:

### 1. Message passing
Pass context explicitly in the handoff payload. Simple and auditable.

```python
payload = HandoffPayload(
    task="Review this code for security issues",
    context={"code": previous_agent_result["code"]},
    artifacts=[],
)
```

### 2. Shared memory store
Workers read/write to a shared key-value store or vector database.

```python
memory_store["research_results"] = research_agent.run(query)
# Later...
context = memory_store["research_results"]
code_agent.run(task, context=context)
```

### 3. Pub/sub messaging
Workers publish events; downstream workers subscribe and react.

```python
event_bus.publish("research.complete", {"results": data})
# Code agent subscribes to "research.complete"
```

---

## 6.5 Parallel Agent Execution

Independent subtasks can run concurrently using `asyncio.gather`:

```python
async def parallel_research(topics: list[str]) -> list[str]:
    tasks = [research_agent.run(topic) for topic in topics]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out failures
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    
    if failures:
        print(f"Warning: {len(failures)} parallel tasks failed")
    
    return successes
```

Parallelism can reduce total latency by 3–5× for independent subtasks.

---

## 6.6 Error Handling in Multi-Agent Systems

Failures cascade in multi-agent systems. Use circuit breakers and fallback strategies:

```python
async def safe_worker_call(worker, payload, fallback_value=""):
    try:
        return await asyncio.wait_for(
            worker.execute(payload),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        logger.warning(f"Worker {payload.target_agent} timed out")
        return fallback_value
    except Exception as e:
        logger.error(f"Worker {payload.target_agent} failed: {e}")
        return fallback_value
```

---

## Summary

- Multi-agent collaboration overcomes single-agent limits: context, specialization, speed
- Orchestrator–worker is the dominant pattern: orchestrator plans, workers execute
- Handoffs carry task + context + artifacts between agents
- Context sharing: message passing (simple), shared memory (flexible), pub/sub (reactive)
- Use `asyncio.gather` for parallel independent subtasks
- Always implement timeouts and fallbacks for worker failures

**Next:** Chapter 7 — Agent Memory and State
