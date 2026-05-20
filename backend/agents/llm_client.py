from agents import OpenAIChatCompletionsModel, AsyncOpenAI
from backend.config import settings


def get_llm_model() -> OpenAIChatCompletionsModel:
    client = AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
