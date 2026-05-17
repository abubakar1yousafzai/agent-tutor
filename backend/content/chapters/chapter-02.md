# Chapter 2: Claude Agent SDK Basics

## Learning Objectives
- Set up the Claude Agent SDK (Anthropic Python SDK)
- Define tools using Python functions with type hints
- Run your first agent with `AgentRunner`
- Understand how tool results flow back into the agent

---

## 2.1 Installation and Setup

```bash
pip install anthropic
```

Set your API key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or in Python:
```python
import anthropic
client = anthropic.Anthropic(api_key="sk-ant-...")
```

---

## 2.2 Your First Tool

Tools are Python functions annotated with type hints and a docstring. The SDK introspects these to build the JSON schema automatically.

```python
def get_weather(city: str) -> str:
    """Get the current weather for a city.
    
    Args:
        city: The name of the city to get weather for.
    """
    # In production, this calls a real weather API
    return f"The weather in {city} is 22°C and sunny."
```

### Registering tools

```python
from anthropic import Anthropic
from anthropic.types import Tool

client = Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name"}
            },
            "required": ["city"]
        }
    }
]
```

---

## 2.3 Running an Agent

```python
messages = [{"role": "user", "content": "What's the weather in Karachi?"}]

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)
```

### Handling tool calls

When Claude decides to use a tool, `response.stop_reason == "tool_use"`. You must:
1. Execute the tool
2. Return the result as a `tool_result` message
3. Call the API again

```python
def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )
        
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        
        # Add assistant response + tool results to history
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
```

---

## 2.4 The AgentRunner Pattern

For production agents, use a structured runner that handles the loop automatically:

```python
class AgentRunner:
    def __init__(self, model: str, tools: list, system: str):
        self.client = Anthropic()
        self.model = model
        self.tools = tools
        self.system = system
    
    def run(self, user_input: str, max_turns: int = 10) -> str:
        messages = [{"role": "user", "content": user_input}]
        turns = 0
        
        while turns < max_turns:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system,
                tools=self.tools,
                messages=messages,
            )
            turns += 1
            
            if response.stop_reason == "end_turn":
                return response.content[0].text
            
            # Handle tool use ...
        
        raise RuntimeError(f"Agent exceeded max_turns={max_turns}")
```

`max_turns` prevents infinite loops — a critical safety guard for production agents.

---

## 2.5 Tool Result Format

Tool results are returned via `tool_result` content blocks:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
  "content": "The weather in Karachi is 38°C and sunny."
}
```

Claude processes this result and continues reasoning. The conversation history accumulates:
1. User message
2. Assistant (with `tool_use` block)
3. User (with `tool_result` block)
4. Assistant (final response)

---

## Summary

- Install the Anthropic SDK and configure your API key
- Define tools as Python functions with type hints and docstrings
- The agent loop: create → check stop_reason → execute tools → loop
- `AgentRunner` encapsulates the loop and enforces `max_turns`
- Tool results flow back via `tool_result` content blocks in the next user message

**Next:** Chapter 3 — Building Your First Agent
