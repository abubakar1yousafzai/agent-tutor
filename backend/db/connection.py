from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from backend.config import settings
from backend.db.tables import metadata

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_all_tables():
    async with engine.begin() as conn:
        # Enable pgcrypto for gen_random_uuid() if on PostgreSQL
        try:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
        except Exception:
            pass  # SQLite test environments don't support extensions
        await conn.run_sync(metadata.create_all)
