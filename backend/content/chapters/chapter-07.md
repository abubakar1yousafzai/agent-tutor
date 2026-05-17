# Chapter 7: Agent Memory and State

## Learning Objectives
- Distinguish the four types of agent memory
- Implement in-context and external memory systems
- Design stateful agents that persist across sessions
- Use vector embeddings for semantic memory retrieval

---

## 7.1 Why Agents Need Memory

Without memory, every agent interaction starts from zero. The agent:
- Can't remember what was discussed two messages ago (past context window)
- Can't recall decisions made in yesterday's session
- Can't build up knowledge about a user over time
- Can't resume interrupted tasks

Memory transforms a stateless model into a **stateful agent** that learns and adapts.

---

## 7.2 The Four Memory Types

### Type 1: In-Context Memory (Short-term)
Information stored in the active conversation window.

- **Capacity:** Limited by model context window (e.g., 200K tokens for Claude)
- **Scope:** Current session only
- **Access:** Instant — model sees it directly
- **Cost:** Tokens = cost

```python
messages = [
    {"role": "user", "content": "My name is Abu Bakar"},
    {"role": "assistant", "content": "Hello Abu Bakar!"},
    {"role": "user", "content": "What's my name?"},  # Agent knows from context
]
```

### Type 2: External Memory (Long-term Episodic)
Records of past interactions stored in a database.

- **Capacity:** Unlimited
- **Scope:** Persistent across sessions
- **Access:** Requires explicit retrieval
- **Cost:** Storage + retrieval query

```python
# Save interaction
await db.execute(
    insert(memory_log).values(user_id=user_id, content=summary, timestamp=now())
)

# Retrieve relevant memories
memories = await db.execute(
    select(memory_log)
    .where(memory_log.c.user_id == user_id)
    .order_by(memory_log.c.timestamp.desc())
    .limit(10)
)
```

### Type 3: Semantic Memory (Vector Search)
Concepts and knowledge stored as embeddings for similarity search.

- **Capacity:** Millions of documents
- **Scope:** Shared across users (knowledge base) or per-user
- **Access:** Approximate nearest neighbor search
- **Cost:** Embedding generation + vector DB query

```python
from pgvector.asyncpg import register_vector

async def search_similar(query: str, limit: int = 5):
    embedding = await embed(query)  # e.g., text-embedding-3-small
    results = await db.execute(
        "SELECT content FROM knowledge_base ORDER BY embedding <-> $1 LIMIT $2",
        [embedding, limit]
    )
    return results.all()
```

### Type 4: Procedural Memory (Skills)
Learned procedures encoded as SKILL.md files, tools, or fine-tuned behaviors.

- **Capacity:** As many skills as needed
- **Scope:** Global (applies to all users)
- **Access:** Loaded into context when triggered
- **Cost:** Context tokens per skill loaded

---

## 7.3 State Management Patterns

### Session State
Short-lived state within a single user session:

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class SessionState:
    user_id: str
    session_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    current_chapter: str | None = None
    quiz_in_progress: bool = False
    messages: list[dict] = field(default_factory=list)
    tool_call_count: int = 0
```

### Persistent State
User state that survives session boundaries (stored in DB):

```python
# Our AgentTutor uses this pattern for streaks and progress
async def load_user_state(user_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        select(users.c.tier, users.c.streak_days, users.c.last_active)
        .where(users.c.id == user_id)
    )
    row = result.first()
    return {"tier": row[0], "streak": row[1], "last_active": row[2]}
```

---

## 7.4 Context Window Management

When in-context memory fills up, use a summarization strategy:

```python
async def compress_history(messages: list[dict], client: Anthropic) -> list[dict]:
    if len(messages) <= 10:
        return messages
    
    # Keep first system message and last 5 exchanges
    to_summarize = messages[:-10]
    recent = messages[-10:]
    
    summary_response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # cheap model for summarization
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Summarize this conversation in 3 sentences:\n\n{str(to_summarize)}"
        }]
    )
    
    summary_message = {
        "role": "user",
        "content": f"[Previous conversation summary: {summary_response.content[0].text}]"
    }
    
    return [summary_message] + recent
```

---

## Summary

- Four memory types: in-context (short-term), external (episodic), semantic (vector), procedural (skills)
- In-context memory is instant but bounded; external memory is unlimited but requires retrieval
- Semantic memory uses vector embeddings for "fuzzy" concept recall
- Session state tracks current interaction; persistent state tracks cross-session data
- Use summarization to compress long histories and preserve context window budget

**Next:** Chapter 8 — A2A Protocol
