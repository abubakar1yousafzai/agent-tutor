import os
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import insert

from backend.db.tables import users, chapters, quiz_bank, metadata
from backend.db.connection import get_db
from backend.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_client(async_engine):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def free_user(async_engine):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    user_id = uuid.uuid4()
    async with factory() as session:
        await session.execute(
            insert(users).values(
                id=user_id,
                email=f"free_{user_id.hex[:8]}@test.com",
                name="Free User",
                tier="free",
                streak_days=0,
            )
        )
        await session.commit()
    return {"id": user_id, "tier": "free"}


@pytest_asyncio.fixture
async def premium_user(async_engine):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    user_id = uuid.uuid4()
    async with factory() as session:
        await session.execute(
            insert(users).values(
                id=user_id,
                email=f"premium_{user_id.hex[:8]}@test.com",
                name="Premium User",
                tier="premium",
                streak_days=0,
            )
        )
        await session.commit()
    return {"id": user_id, "tier": "premium"}


@pytest_asyncio.fixture
async def sample_chapters(async_engine):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    chapter_rows = [
        {
            "id": f"chapter-0{i}", "number": i, "title": f"Chapter {i}",
            "tier_required": "free" if i <= 3 else "premium",
            "content_key": f"chapter-0{i}.md",
        }
        for i in range(1, 4)
    ]
    async with factory() as session:
        await session.execute(insert(chapters), chapter_rows)
        await session.commit()
    return chapter_rows


@pytest_asyncio.fixture
async def sample_quiz_bank(async_engine, sample_chapters):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    rows = []
    for ch in sample_chapters:
        for q in range(1, 6):
            rows.append({
                "id": uuid.uuid4(),
                "chapter_id": ch["id"],
                "question_number": q,
                "question": f"Q{q} for {ch['id']}?",
                "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
                "correct_answer": "A",
            })
    async with factory() as session:
        await session.execute(insert(quiz_bank), rows)
        await session.commit()
    return rows


@pytest_asyncio.fixture
async def async_session(async_engine):
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
