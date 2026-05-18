from agents import OpenAIChatCompletionsModel, AsyncOpenAI
import os


def get_llm_model() -> OpenAIChatCompletionsModel:
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
