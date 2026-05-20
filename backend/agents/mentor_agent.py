from agents import Agent, Runner, function_tool
from backend.agents.llm_client import get_llm_model
from backend.storage.content_reader import get_local_content

MENTOR_SYSTEM_PROMPT = (
    "You are an expert AI Agent Development mentor for AgentTutor. You have tools\n"
    "to fetch chapter content and check student progress. Always fetch relevant\n"
    "chapter content before answering any question. Check student progress to\n"
    "personalize your response based on what the student has already learned.\n"
    "Guide students using the Socratic method — ask guiding questions rather than\n"
    "giving direct answers. Be patient, encouraging, and specific."
)


def _extract_tool_calls(result) -> tuple[list[str], list[str]]:
    tools_used = []
    chapters_referenced = []
    for msg in result.raw_responses:
        for block in getattr(msg, "content", []):
            if getattr(block, "type", None) == "tool_use":
                name = block.name
                if name not in tools_used:
                    tools_used.append(name)
                if name == "get_chapter_content":
                    chapter_id = block.input.get("chapter_id", "")
                    if chapter_id and chapter_id not in chapters_referenced:
                        chapters_referenced.append(chapter_id)
    return tools_used, chapters_referenced


def run_mentor(question: str, progress_summary: str) -> tuple[str, list[str], list[str]]:
    @function_tool
    def get_chapter_content(chapter_id: str) -> str:
        """Fetch the full markdown content of the chapter with the given chapter_id."""
        content = get_local_content(chapter_id)
        return content if content is not None else "Chapter not found."

    @function_tool
    def get_student_progress(user_id: str) -> str:
        """Return the student's completed chapters and quiz scores."""
        return progress_summary

    mentor_agent = Agent(
        name="Mentor",
        model=get_llm_model(),
        tools=[get_chapter_content, get_student_progress],
        instructions=MENTOR_SYSTEM_PROMPT,
    )
    result = Runner.run_sync(mentor_agent, question)
    tools_used, chapters_referenced = _extract_tool_calls(result)
    return result.final_output, chapters_referenced, tools_used
