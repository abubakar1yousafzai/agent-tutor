import json
import re

from agents import Agent, Runner
from backend.agents.llm_client import get_llm_model

ASSESSOR_SYSTEM_PROMPT = (
    "You are an expert AI Agent Development instructor grading a student answer.\n"
    "Use only the provided chapter content to evaluate the answer.\n"
    "Be encouraging, constructive, and specific.\n"
    "Return ONLY a JSON object with these exact fields:\n"
    "score (integer 0-10), max_score (always 10), grade (letter grade A-F),\n"
    "feedback (overall feedback string), what_was_correct (string),\n"
    "what_was_missing (string), improvement_tip (string).\n"
    "Do not include markdown fencing or any text outside the JSON object."
)


def extract_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
        return json.loads(stripped)


def run_assessment(chapter_content: str, question: str, student_answer: str) -> dict:
    agent = Agent(name="Assessor", model=get_llm_model(), instructions=ASSESSOR_SYSTEM_PROMPT)
    message = (
        f"Chapter Content:\n{chapter_content}\n\n"
        f"Question: {question}\n\n"
        f"Student Answer: {student_answer}\n\n"
        "Return JSON only."
    )
    result = Runner.run_sync(agent, message)
    return extract_json(result.final_output)
