# Chapter 3: Building Your First Agent

## Learning Objectives
- Design a complete agent from requirements to code
- Write an effective system prompt
- Handle errors gracefully in agentic workflows
- Test your agent end-to-end

---

## 3.1 The Agent Design Process

Before writing code, define:
1. **Goal:** What does the agent accomplish?
2. **Tools:** What capabilities does it need?
3. **Constraints:** What should it never do?
4. **Inputs/Outputs:** What does it receive and return?

### Example: Research Assistant Agent

**Goal:** Given a topic, research it and produce a structured summary.
**Tools:** `web_search`, `read_url`, `write_summary`
**Constraints:** Do not fabricate citations; stay on topic.
**Input:** User query string. **Output:** Markdown summary with sources.

---

## 3.2 Writing an Effective System Prompt

A system prompt defines the agent's identity, purpose, tools, and behavioral boundaries.

```python
SYSTEM_PROMPT = """You are a Research Assistant agent. Your job is to research topics thoroughly and produce clear, accurate summaries.

## Available Tools
- web_search(query): Search the web for current information
- read_url(url): Read the content of a specific webpage  
- write_summary(content): Format and save the final summary

## Behavioral Rules
1. Always verify information from at least two sources
2. Never fabricate citations or URLs
3. Cite your sources in the final summary
4. Ask clarifying questions if the topic is ambiguous
5. Stop and report if you cannot find reliable sources

## Output Format
Your final summary must include:
- Executive Summary (2-3 sentences)
- Key Findings (bullet points)
- Sources (list of URLs)
"""
```

### Principles of good system prompts
- **Explicit purpose:** One clear mission statement
- **Tool documentation:** What each tool does and when to use it
- **Behavioral constraints:** What the agent must/must not do
- **Output specification:** Expected format and structure

---

## 3.3 Implementing Tools

```python
import httpx
from pathlib import Path

def web_search(query: str) -> str:
    """Search the web for information about a query.
    
    Args:
        query: The search query string.
    
    Returns:
        A list of search results with titles and snippets.
    """
    # Production implementation would call a search API
    # (e.g., Serper, Bing, DuckDuckGo)
    return f"Search results for '{query}': [simulated results]"


def read_url(url: str) -> str:
    """Read and return the text content of a webpage.
    
    Args:
        url: The full URL of the webpage to read.
    
    Returns:
        The text content of the page, truncated to 10,000 characters.
    """
    try:
        response = httpx.get(url, timeout=10)
        return response.text[:10_000]
    except Exception as e:
        return f"Error reading {url}: {str(e)}"


def write_summary(content: str) -> str:
    """Save the final research summary.
    
    Args:
        content: The formatted markdown summary to save.
    
    Returns:
        Confirmation message with file path.
    """
    path = Path("output/summary.md")
    path.parent.mkdir(exist_ok=True)
    path.write_text(content)
    return f"Summary saved to {path}"
```

---

## 3.4 Graceful Error Handling

Agents must handle tool failures without crashing the entire workflow.

```python
def execute_tool(name: str, inputs: dict) -> str:
    tool_map = {
        "web_search": web_search,
        "read_url": read_url,
        "write_summary": write_summary,
    }
    
    func = tool_map.get(name)
    if not func:
        return f"Unknown tool: {name}"
    
    try:
        return func(**inputs)
    except ValueError as e:
        return f"Invalid input for {name}: {e}"
    except httpx.TimeoutException:
        return f"Tool {name} timed out. Try with a simpler query."
    except Exception as e:
        return f"Tool {name} failed: {type(e).__name__}: {e}"
```

### Error handling principles
- **Never crash:** Return an error string, not an exception
- **Be specific:** Tell the agent what went wrong and why
- **Suggest recovery:** "Try with a simpler query" gives the agent a path forward
- **Log everything:** Record tool calls and failures for debugging

---

## 3.5 Complete Agent Implementation

```python
from anthropic import Anthropic

client = Anthropic()

def run_research_agent(topic: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": f"Research this topic: {topic}"}]
    
    for turn in range(max_turns):
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        
        if response.stop_reason == "end_turn":
            # Extract text from response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Agent completed without text output."
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            
            messages.append({"role": "user", "content": tool_results})
        else:
            break
    
    return f"Agent reached max_turns={max_turns} without completing."
```

---

## 3.6 Testing Your Agent

Test at three levels:

### Unit tests — test tools in isolation
```python
def test_web_search_returns_string():
    result = web_search("Python programming")
    assert isinstance(result, str)
    assert len(result) > 0

def test_read_url_handles_timeout():
    result = read_url("http://doesnotexist.invalid")
    assert "Error" in result or "timed out" in result
```

### Integration tests — test the agent loop
```python
def test_agent_completes_simple_task():
    result = run_research_agent("What is Python?", max_turns=5)
    assert isinstance(result, str)
    assert len(result) > 100
```

### End-to-end tests — test real tool calls
```python
def test_agent_uses_web_search(mocker):
    mock_search = mocker.patch("web_search", return_value="Python is a programming language")
    result = run_research_agent("What is Python?")
    mock_search.assert_called_at_least_once()
```

---

## Summary

- Design agents by defining goal, tools, constraints, and I/O before coding
- System prompts must include purpose, tool docs, behavioral rules, and output format
- Tools should return error strings, not raise exceptions
- `execute_tool` dispatch handles unknown tools and unexpected failures
- Test at unit, integration, and end-to-end levels

**Next:** Chapter 4 — Model Context Protocol *(Premium)*
