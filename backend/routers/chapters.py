from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from backend.db.connection import get_db
from backend.db.tables import users, chapters
from backend.models.chapter import ChapterSummary, ChapterContent, ChapterNavigation
from backend.storage.content_reader import fetch_chapter_content

router = APIRouter(prefix="/chapters", tags=["Chapters"])

FREE_CHAPTERS = {"chapter-01", "chapter-02", "chapter-03"}
UPGRADE_MESSAGE = "This chapter requires a Premium subscription. Upgrade to unlock all 10 chapters and the full quiz bank."


async def _get_user_tier(user_id: UUID, db: AsyncSession) -> str:
    result = await db.execute(select(users.c.tier).where(users.c.id == user_id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row[0]


def _is_accessible(chapter_tier: str, user_tier: str, chapter_id: str) -> bool:
    if chapter_id in FREE_CHAPTERS:
        return True
    return user_tier == "premium"


async def _chapter_nav(row, user_tier: str) -> ChapterNavigation | None:
    if row is None:
        return None
    return ChapterNavigation(
        id=row["id"], number=row["number"], title=row["title"],
        tier_required=row["tier_required"],
        is_accessible=_is_accessible(row["tier_required"], user_tier, row["id"]),
    )


@router.get("", response_model=list[ChapterSummary])
async def list_chapters(
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    user_tier = await _get_user_tier(user_id, db)
    result = await db.execute(select(chapters).order_by(chapters.c.number))
    rows = result.mappings().all()
    return [
        ChapterSummary(
            id=r["id"], number=r["number"], title=r["title"],
            tier_required=r["tier_required"],
            is_accessible=_is_accessible(r["tier_required"], user_tier, r["id"]),
        )
        for r in rows
    ]


@router.get("/{chapter_id}/content", response_model=ChapterContent)
async def get_chapter_content(
    chapter_id: str,
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    user_tier = await _get_user_tier(user_id, db)

    result = await db.execute(select(chapters).where(chapters.c.id == chapter_id))
    ch = result.mappings().first()
    if not ch:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_id}' not found")

    if not _is_accessible(ch["tier_required"], user_tier, chapter_id):
        raise HTTPException(
            status_code=403,
            detail={"error": "premium_required", "message": UPGRADE_MESSAGE},
        )

    content = await fetch_chapter_content(chapter_id)

    prev_result = await db.execute(
        select(chapters).where(chapters.c.number == ch["number"] - 1)
    )
    next_result = await db.execute(
        select(chapters).where(chapters.c.number == ch["number"] + 1)
    )

    return ChapterContent(
        id=ch["id"], number=ch["number"], title=ch["title"],
        content=content,
        previous_chapter=await _chapter_nav(prev_result.mappings().first(), user_tier),
        next_chapter=await _chapter_nav(next_result.mappings().first(), user_tier),
    )


@router.get("/{chapter_id}/next", response_model=ChapterNavigation | None)
async def get_next_chapter(
    chapter_id: str,
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    user_tier = await _get_user_tier(user_id, db)
    result = await db.execute(select(chapters.c.number).where(chapters.c.id == chapter_id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Chapter not found")

    next_result = await db.execute(
        select(chapters).where(chapters.c.number == row[0] + 1)
    )
    return await _chapter_nav(next_result.mappings().first(), user_tier)


@router.get("/{chapter_id}/previous", response_model=ChapterNavigation | None)
async def get_previous_chapter(
    chapter_id: str,
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    user_tier = await _get_user_tier(user_id, db)
    result = await db.execute(select(chapters.c.number).where(chapters.c.id == chapter_id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Chapter not found")

    prev_result = await db.execute(
        select(chapters).where(chapters.c.number == row[0] - 1)
    )
    return await _chapter_nav(prev_result.mappings().first(), user_tier)
