# Zero-Backend-LLM Architecture — No LLM calls permitted in this codebase.
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.connection import create_all_tables
from backend.routers import chapters, quizzes, progress, search, access, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(
    title="AgentTutor API",
    description="Zero-Backend-LLM Course Companion — all intelligence in the ChatGPT App frontend.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(chapters.router)
app.include_router(quizzes.router)
app.include_router(progress.router)
app.include_router(search.router)
app.include_router(access.router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "llm_calls": 0}
