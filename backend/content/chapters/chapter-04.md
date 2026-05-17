# Chapter 4: Model Context Protocol (MCP)

## Learning Objectives
- Understand what MCP is and the problem it solves
- Distinguish MCP clients, servers, and hosts
- Implement an MCP server in Python
- Connect Claude to an MCP server

---

## 4.1 The Problem MCP Solves

Before MCP, every AI application had to implement custom integrations for each tool: a bespoke connector for GitHub, another for Slack, another for databases. This created an `N × M` problem — N models × M tools = exponential integration complexity.

**Model Context Protocol (MCP)** is an open standard developed by Anthropic that standardizes how AI models connect to tools, data sources, and services. It creates a universal adapter layer.

```
Before MCP:              After MCP:
Claude ──► GitHub        Claude ──► MCP ──► GitHub
Claude ──► Slack                    ├──► Slack
Claude ──► DB                       ├──► DB
GPT ──► GitHub                      └──► Files
GPT ──► Slack         GPT ──► MCP ──► (same servers)
```

---

## 4.2 MCP Architecture

MCP defines three roles:

### Host
The application that contains the AI model (e.g., Claude Desktop, your custom app). The host manages MCP client connections and provides the LLM.

### Client
Lives inside the host. Each client maintains a 1:1 connection to one MCP server. The client negotiates capabilities and routes tool calls.

### Server
An independent process that exposes **tools**, **resources**, and **prompts** to any MCP-compatible client. Servers are language-agnostic.

```
┌─────────────────────────────────┐
│  HOST (Claude Desktop / App)    │
│  ┌──────────┐  ┌──────────┐    │
│  │ MCP      │  │ MCP      │    │
│  │ Client 1 │  │ Client 2 │    │
│  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼──────────┘
        │             │
   stdio/SSE     stdio/SSE
        │             │
┌───────▼─────┐ ┌─────▼──────────┐
│ MCP Server  │ │ MCP Server     │
│ (filesystem)│ │ (github)       │
└─────────────┘ └────────────────┘
```

---

## 4.3 MCP Transports

MCP supports two transport mechanisms:

### stdio (Standard I/O)
Used for local processes. The host spawns the server as a subprocess and communicates via stdin/stdout. Best for local tools.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["-m", "mcp_server_filesystem", "/home/user/docs"]
    }
  }
}
```

### SSE (Server-Sent Events)
Used for remote servers over HTTP. The client connects to a URL and receives a stream of events.

```json
{
  "mcpServers": {
    "remote-api": {
      "url": "https://api.example.com/mcp/sse"
    }
  }
}
```

---

## 4.4 Building an MCP Server in Python

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("my-tools-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_file_contents",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_file_contents":
        path = arguments["path"]
        try:
            content = open(path).read()
            return [types.TextContent(type="text", text=content)]
        except FileNotFoundError:
            return [types.TextContent(type="text", text=f"File not found: {path}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 4.5 MCP Resources and Prompts

Beyond tools, MCP servers can expose:

### Resources
Static or dynamic data the LLM can read (like read-only context):
```python
@server.list_resources()
async def list_resources():
    return [types.Resource(uri="file://docs/readme.md", name="README", mimeType="text/markdown")]
```

### Prompts
Pre-defined prompt templates with arguments:
```python
@server.list_prompts()
async def list_prompts():
    return [types.Prompt(name="summarize", description="Summarize a document", arguments=[...])]
```

---

## Summary

- MCP solves the N×M integration problem by standardizing the agent-tool interface
- Three roles: Host (app), Client (connector), Server (tool provider)
- Two transports: stdio (local) and SSE (remote)
- MCP servers expose tools, resources, and prompts
- Any MCP-compatible client can use any MCP server — vendor-agnostic

**Next:** Chapter 5 — Agent Skills and SKILL.md
