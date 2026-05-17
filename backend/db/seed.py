"""
Seed script: creates tables and populates chapters + quiz bank.
Usage (from anywhere):
    python db/seed.py --create-tables --quiz-bank        (from backend/)
    python -m backend.db.seed --create-tables --quiz-bank (from project root)
"""
import sys
from pathlib import Path
# Add project root to sys.path so 'backend' package is always importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
import argparse
import uuid
from sqlalchemy.dialects.postgresql import insert
from backend.db.connection import engine, create_all_tables
from backend.db.tables import chapters, quiz_bank
from backend.storage.content_reader import get_local_content

CHAPTER_DATA = [
    {"id": "chapter-01", "number": 1, "title": "What is an AI Agent",             "tier_required": "free",    "content_key": "chapter-01.md"},
    {"id": "chapter-02", "number": 2, "title": "Claude Agent SDK Basics",          "tier_required": "free",    "content_key": "chapter-02.md"},
    {"id": "chapter-03", "number": 3, "title": "Building Your First Agent",        "tier_required": "free",    "content_key": "chapter-03.md"},
    {"id": "chapter-04", "number": 4, "title": "Model Context Protocol",           "tier_required": "premium", "content_key": "chapter-04.md"},
    {"id": "chapter-05", "number": 5, "title": "Agent Skills and SKILL.md",        "tier_required": "premium", "content_key": "chapter-05.md"},
    {"id": "chapter-06", "number": 6, "title": "Multi-Agent Collaboration",        "tier_required": "premium", "content_key": "chapter-06.md"},
    {"id": "chapter-07", "number": 7, "title": "Agent Memory and State",           "tier_required": "premium", "content_key": "chapter-07.md"},
    {"id": "chapter-08", "number": 8, "title": "A2A Protocol",                     "tier_required": "premium", "content_key": "chapter-08.md"},
    {"id": "chapter-09", "number": 9, "title": "Agent Factory Architecture",       "tier_required": "premium", "content_key": "chapter-09.md"},
    {"id": "chapter-10", "number": 10,"title": "Production Deployment",            "tier_required": "premium", "content_key": "chapter-10.md"},
]

QUIZ_DATA = [
    # chapter-01: What is an AI Agent
    {"chapter_id": "chapter-01", "question_number": 1, "question": "What is the primary characteristic that distinguishes an AI agent from a simple script?", "option_a": "It runs faster", "option_b": "It perceives its environment and takes actions to achieve goals", "option_c": "It uses more memory", "option_d": "It requires internet access", "correct_answer": "B"},
    {"chapter_id": "chapter-01", "question_number": 2, "question": "Which component allows an AI agent to interact with external tools and APIs?", "option_a": "The training dataset", "option_b": "The GPU hardware", "option_c": "Tool use / function calling", "option_d": "The user interface", "correct_answer": "C"},
    {"chapter_id": "chapter-01", "question_number": 3, "question": "What does the 'perception' step in an agent loop involve?", "option_a": "Generating a response", "option_b": "Reading and interpreting inputs from the environment", "option_c": "Storing data in a database", "option_d": "Deploying the model", "correct_answer": "B"},
    {"chapter_id": "chapter-01", "question_number": 4, "question": "An AI agent that can plan multiple steps to complete a task is described as:", "option_a": "Reactive", "option_b": "Stateless", "option_c": "Agentic", "option_d": "Deterministic", "correct_answer": "C"},
    {"chapter_id": "chapter-01", "question_number": 5, "question": "What is the agent loop?", "option_a": "A loop that runs the model training process", "option_b": "The repeated cycle of perceive → think → act", "option_c": "A loop that refreshes the user interface", "option_d": "A database connection retry mechanism", "correct_answer": "B"},
    # chapter-02: Claude Agent SDK Basics
    {"chapter_id": "chapter-02", "question_number": 1, "question": "What is the Claude Agent SDK primarily used for?", "option_a": "Training new Claude models", "option_b": "Building agentic applications powered by Claude", "option_c": "Managing AWS infrastructure", "option_d": "Creating static websites", "correct_answer": "B"},
    {"chapter_id": "chapter-02", "question_number": 2, "question": "In the Claude Agent SDK, what is a 'tool'?", "option_a": "A hardware device", "option_b": "A Python decorator", "option_c": "A function the agent can call to interact with external systems", "option_d": "A configuration file", "correct_answer": "C"},
    {"chapter_id": "chapter-02", "question_number": 3, "question": "Which class is the entry point for running agents in the Claude SDK?", "option_a": "AgentRunner", "option_b": "ClaudeClient", "option_c": "ModelServer", "option_d": "ToolRegistry", "correct_answer": "A"},
    {"chapter_id": "chapter-02", "question_number": 4, "question": "What format does the Claude Agent SDK use to define tools?", "option_a": "XML schemas", "option_b": "Python functions with type hints and docstrings", "option_c": "JSON configuration files", "option_d": "SQL stored procedures", "correct_answer": "B"},
    {"chapter_id": "chapter-02", "question_number": 5, "question": "How does Claude communicate tool results back into the conversation?", "option_a": "Via a separate REST endpoint", "option_b": "Through tool_result messages in the conversation context", "option_c": "By writing to a shared database", "option_d": "Via email notification", "correct_answer": "B"},
    # chapter-03: Building Your First Agent
    {"chapter_id": "chapter-03", "question_number": 1, "question": "What is the minimum requirement to build a functional agent with the Claude SDK?", "option_a": "A GPU server", "option_b": "A system prompt, a model, and at least one tool", "option_c": "A React frontend", "option_d": "A Kubernetes cluster", "correct_answer": "B"},
    {"chapter_id": "chapter-03", "question_number": 2, "question": "What should a well-written agent system prompt include?", "option_a": "Database credentials", "option_b": "The agent's purpose, available tools, and behavioral constraints", "option_c": "HTML markup", "option_d": "Random seed values", "correct_answer": "B"},
    {"chapter_id": "chapter-03", "question_number": 3, "question": "Which pattern is recommended for handling agent errors gracefully?", "option_a": "Ignore all errors", "option_b": "Crash the application", "option_c": "Try/except with fallback responses and user-friendly messages", "option_d": "Restart the server", "correct_answer": "C"},
    {"chapter_id": "chapter-03", "question_number": 4, "question": "What does 'max_turns' control in an agent run?", "option_a": "The maximum number of users", "option_b": "The maximum number of agentic steps before stopping", "option_c": "The response length limit", "option_d": "The database connection timeout", "correct_answer": "B"},
    {"chapter_id": "chapter-03", "question_number": 5, "question": "Why is testing agents with real tool calls important?", "option_a": "It is not important", "option_b": "To verify the agent selects and uses tools correctly end-to-end", "option_c": "Only to measure speed", "option_d": "To check spelling errors", "correct_answer": "B"},
    # chapter-04: Model Context Protocol
    {"chapter_id": "chapter-04", "question_number": 1, "question": "What does MCP stand for in the context of AI agents?", "option_a": "Multi-Channel Processing", "option_b": "Model Context Protocol", "option_c": "Machine Control Program", "option_d": "Memory Cache Pool", "correct_answer": "B"},
    {"chapter_id": "chapter-04", "question_number": 2, "question": "What problem does MCP solve for AI agents?", "option_a": "Reducing model size", "option_b": "Standardizing how agents connect to external tools and data sources", "option_c": "Speeding up training", "option_d": "Encrypting model weights", "correct_answer": "B"},
    {"chapter_id": "chapter-04", "question_number": 3, "question": "In MCP architecture, what is an 'MCP Server'?", "option_a": "A physical server rack", "option_b": "A process that exposes tools and resources to an AI agent", "option_c": "The Claude API endpoint", "option_d": "A load balancer", "correct_answer": "B"},
    {"chapter_id": "chapter-04", "question_number": 4, "question": "Which transport protocol does MCP support for local communication?", "option_a": "FTP", "option_b": "stdio (standard input/output)", "option_c": "Bluetooth", "option_d": "DNS", "correct_answer": "B"},
    {"chapter_id": "chapter-04", "question_number": 5, "question": "MCP is designed to be:", "option_a": "Proprietary to Anthropic only", "option_b": "An open standard usable by any AI system", "option_c": "Only for Python applications", "option_d": "Only for cloud deployments", "correct_answer": "B"},
    # chapter-05: Agent Skills and SKILL.md
    {"chapter_id": "chapter-05", "question_number": 1, "question": "What is a SKILL.md file?", "option_a": "A Python module for ML models", "option_b": "A markdown document defining how an agent performs a specific task", "option_c": "A database migration script", "option_d": "A Docker configuration file", "correct_answer": "B"},
    {"chapter_id": "chapter-05", "question_number": 2, "question": "Which section of a SKILL.md defines the step-by-step procedure?", "option_a": "Metadata", "option_b": "Workflow", "option_c": "Dependencies", "option_d": "Changelog", "correct_answer": "B"},
    {"chapter_id": "chapter-05", "question_number": 3, "question": "Why are Agent Skills important for production FTEs?", "option_a": "They replace the underlying LLM", "option_b": "They ensure consistent, reproducible behavior at scale", "option_c": "They reduce token usage to zero", "option_d": "They enable offline operation", "correct_answer": "B"},
    {"chapter_id": "chapter-05", "question_number": 4, "question": "What should 'Key Principles' in a SKILL.md contain?", "option_a": "Database schema", "option_b": "Behavioral constraints and guardrails for the skill", "option_c": "Server IP addresses", "option_d": "CSS styles", "correct_answer": "B"},
    {"chapter_id": "chapter-05", "question_number": 5, "question": "Trigger keywords in a SKILL.md are used to:", "option_a": "Restart the server", "option_b": "Identify when the agent should activate this skill", "option_c": "Connect to the database", "option_d": "Generate images", "correct_answer": "B"},
    # chapter-06: Multi-Agent Collaboration
    {"chapter_id": "chapter-06", "question_number": 1, "question": "What is the main benefit of multi-agent collaboration?", "option_a": "Reduced code complexity", "option_b": "Tasks can be divided among specialized agents for parallel execution", "option_c": "Lower API costs always", "option_d": "No need for testing", "correct_answer": "B"},
    {"chapter_id": "chapter-06", "question_number": 2, "question": "In an orchestrator-worker pattern, what does the orchestrator do?", "option_a": "Performs all tasks itself", "option_b": "Coordinates and delegates subtasks to worker agents", "option_c": "Stores data in the database", "option_d": "Handles user authentication", "correct_answer": "B"},
    {"chapter_id": "chapter-06", "question_number": 3, "question": "What challenge must be solved for agents to share information?", "option_a": "Network speed", "option_b": "Shared context or messaging protocol", "option_c": "Font selection", "option_d": "Color scheme", "correct_answer": "B"},
    {"chapter_id": "chapter-06", "question_number": 4, "question": "Which communication pattern allows agents to publish events for others to consume?", "option_a": "Direct function calls", "option_b": "Pub/sub messaging", "option_c": "Shared global variables", "option_d": "File system polling", "correct_answer": "B"},
    {"chapter_id": "chapter-06", "question_number": 5, "question": "What is a 'handoff' in multi-agent systems?", "option_a": "Shutting down an agent", "option_b": "Transferring control or context from one agent to another", "option_c": "A database backup", "option_d": "A model update", "correct_answer": "B"},
    # chapter-07: Agent Memory and State
    {"chapter_id": "chapter-07", "question_number": 1, "question": "What is 'in-context memory' for an agent?", "option_a": "RAM usage", "option_b": "Information stored within the active conversation context window", "option_c": "Long-term database storage", "option_d": "Model weights", "correct_answer": "B"},
    {"chapter_id": "chapter-07", "question_number": 2, "question": "Which type of memory persists across separate agent sessions?", "option_a": "In-context memory", "option_b": "External/persistent memory (database or vector store)", "option_c": "CPU cache", "option_d": "Browser cookies", "correct_answer": "B"},
    {"chapter_id": "chapter-07", "question_number": 3, "question": "What is the main limitation of in-context memory?", "option_a": "It is too expensive", "option_b": "It is bounded by the model's context window size", "option_c": "It cannot store text", "option_d": "It requires internet access", "correct_answer": "B"},
    {"chapter_id": "chapter-07", "question_number": 4, "question": "Semantic memory in agents typically uses:", "option_a": "SQL databases only", "option_b": "Vector embeddings for similarity search", "option_c": "Plain text files", "option_d": "Binary protocols", "correct_answer": "B"},
    {"chapter_id": "chapter-07", "question_number": 5, "question": "Why is state management critical for long-running agents?", "option_a": "To reduce electricity usage", "option_b": "To maintain consistency and enable resumable workflows", "option_c": "To improve graphics rendering", "option_d": "To comply with tax regulations", "correct_answer": "B"},
    # chapter-08: A2A Protocol
    {"chapter_id": "chapter-08", "question_number": 1, "question": "What does A2A stand for?", "option_a": "API to API", "option_b": "Agent to Agent", "option_c": "Async to Async", "option_d": "Authenticate to Authorize", "correct_answer": "B"},
    {"chapter_id": "chapter-08", "question_number": 2, "question": "A2A protocol enables agents to:", "option_a": "Train faster", "option_b": "Communicate and collaborate across different systems and vendors", "option_c": "Reduce model size", "option_d": "Generate images", "correct_answer": "B"},
    {"chapter_id": "chapter-08", "question_number": 3, "question": "What is an 'Agent Card' in the A2A specification?", "option_a": "A credit card for API payments", "option_b": "A metadata document describing an agent's capabilities and endpoints", "option_c": "A user profile", "option_d": "A Docker image tag", "correct_answer": "B"},
    {"chapter_id": "chapter-08", "question_number": 4, "question": "Which HTTP method does A2A use to send tasks to a remote agent?", "option_a": "DELETE", "option_b": "POST", "option_c": "GET", "option_d": "HEAD", "correct_answer": "B"},
    {"chapter_id": "chapter-08", "question_number": 5, "question": "A2A supports streaming responses using:", "option_a": "WebSockets only", "option_b": "Server-Sent Events (SSE)", "option_c": "FTP transfers", "option_d": "SMTP", "correct_answer": "B"},
    # chapter-09: Agent Factory Architecture
    {"chapter_id": "chapter-09", "question_number": 1, "question": "What is the Agent Factory Architecture's primary goal?", "option_a": "Building physical robots", "option_b": "A structured approach for manufacturing production-ready AI agents from specs", "option_c": "Replacing all human workers", "option_d": "Training new foundation models", "correct_answer": "B"},
    {"chapter_id": "chapter-09", "question_number": 2, "question": "In Agent Factory, a 'General Agent' (like Claude Code) is responsible for:", "option_a": "Serving user requests", "option_b": "Manufacturing Custom Agents by writing code from specifications", "option_c": "Managing databases", "option_d": "Hosting websites", "correct_answer": "B"},
    {"chapter_id": "chapter-09", "question_number": 3, "question": "What is a 'Custom Agent' (Digital FTE) in the Agent Factory model?", "option_a": "A developer's personal AI assistant", "option_b": "A domain-specific agent deployed to serve end users at scale", "option_c": "A training dataset", "option_d": "A monitoring dashboard", "correct_answer": "B"},
    {"chapter_id": "chapter-09", "question_number": 4, "question": "Which layer in the 8-layer architecture handles HTTP interfaces?", "option_a": "L0 (Sandbox)", "option_b": "L3 (FastAPI)", "option_c": "L6 (Skills)", "option_d": "L7 (A2A)", "correct_answer": "B"},
    {"chapter_id": "chapter-09", "question_number": 5, "question": "Spec-Driven Development (SDD) in the Agent Factory means:", "option_a": "Writing code before requirements", "option_b": "All agent behavior is defined in specs before implementation begins", "option_c": "Using only open-source tools", "option_d": "Deploying to multiple cloud providers", "correct_answer": "B"},
    # chapter-10: Production Deployment
    {"chapter_id": "chapter-10", "question_number": 1, "question": "What is the recommended first step when deploying an agent to production?", "option_a": "Remove all tests", "option_b": "Validate with a staging environment that mirrors production", "option_c": "Disable logging", "option_d": "Increase max_turns to unlimited", "correct_answer": "B"},
    {"chapter_id": "chapter-10", "question_number": 2, "question": "What does 'observability' mean for deployed agents?", "option_a": "Making the UI look good", "option_b": "Ability to monitor, trace, and debug agent behavior in production", "option_c": "Reducing server costs", "option_d": "Limiting user access", "correct_answer": "B"},
    {"chapter_id": "chapter-10", "question_number": 3, "question": "Why should agents have rate limiting in production?", "option_a": "To slow down all users equally", "option_b": "To prevent cost overruns and protect against abuse", "option_c": "To reduce response quality", "option_d": "To log fewer events", "correct_answer": "B"},
    {"chapter_id": "chapter-10", "question_number": 4, "question": "What is a 'kill switch' for a production agent?", "option_a": "A physical power button", "option_b": "A mechanism to disable or limit the agent quickly if it behaves unexpectedly", "option_c": "A training abort command", "option_d": "A UI dark mode toggle", "correct_answer": "B"},
    {"chapter_id": "chapter-10", "question_number": 5, "question": "Which deployment strategy minimizes risk when updating a production agent?", "option_a": "Replace all instances at once", "option_b": "Canary or blue-green deployment to gradually roll out changes", "option_c": "Delete old version immediately", "option_d": "Never update production", "correct_answer": "B"},
]


async def seed_chapters(conn):
    for ch in CHAPTER_DATA:
        search_text = get_local_content(ch["id"])
        await conn.execute(
            insert(chapters).values(
                id=ch["id"], number=ch["number"], title=ch["title"],
                tier_required=ch["tier_required"], content_key=ch["content_key"],
                search_text=search_text,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={"title": ch["title"], "tier_required": ch["tier_required"],
                      "search_text": search_text}
            )
        )
    print(f"Seeded {len(CHAPTER_DATA)} chapters")


async def seed_quiz_bank(conn):
    for q in QUIZ_DATA:
        await conn.execute(
            insert(quiz_bank).values(
                id=uuid.uuid4(),
                chapter_id=q["chapter_id"],
                question_number=q["question_number"],
                question=q["question"],
                option_a=q["option_a"], option_b=q["option_b"],
                option_c=q["option_c"], option_d=q["option_d"],
                correct_answer=q["correct_answer"],
            ).on_conflict_do_update(
                index_elements=["chapter_id", "question_number"],
                set_={"question": q["question"], "option_a": q["option_a"],
                      "option_b": q["option_b"], "option_c": q["option_c"],
                      "option_d": q["option_d"], "correct_answer": q["correct_answer"]}
            )
        )
    print(f"Seeded {len(QUIZ_DATA)} quiz questions")


async def main(create_tables: bool, seed_quiz: bool):
    if create_tables:
        await create_all_tables()
        print("Tables created")
    async with engine.begin() as conn:
        await seed_chapters(conn)
        if seed_quiz:
            await seed_quiz_bank(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-tables", action="store_true")
    parser.add_argument("--quiz-bank", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(create_tables=args.create_tables, seed_quiz=args.quiz_bank))
