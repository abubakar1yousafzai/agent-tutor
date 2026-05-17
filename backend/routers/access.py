from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from backend.db.connection import get_db
from backend.db.tables import users, chapters
from backend.models.access import AccessCheck, TierInfo
from backend.routers.chapters import FREE_CHAPTERS

router = APIRouter(prefix="/access", tags=["Access"])

UPGRADE_MESSAGE = "Upgrade to Premium to unlock chapters 4–10 and the full quiz bank."


@router.get("/check", response_model=AccessCheck)
async def check_access(
    user_id: UUID = Query(...),
    chapter_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(users.c.tier).where(users.c.id == user_id))
    user_row = user_result.first()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    user_tier = user_row[0]

    if chapter_id in FREE_CHAPTERS:
        return AccessCheck(
            user_id=user_id, chapter_id=chapter_id,
            allowed=True, reason="free_chapter",
        )
    if user_tier == "premium":
        return AccessCheck(
            user_id=user_id, chapter_id=chapter_id,
            allowed=True, reason="premium_user",
        )
    return AccessCheck(
        user_id=user_id, chapter_id=chapter_id,
        allowed=False, reason="premium_required",
        upgrade_message=UPGRADE_MESSAGE,
    )


@router.get("/{user_id}/tier", response_model=TierInfo)
async def get_tier_info(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(users.c.tier).where(users.c.id == user_id))
    user_row = user_result.first()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    user_tier = user_row[0]

    free_count = await db.scalar(
        select(func.count()).select_from(chapters)
        .where(chapters.c.tier_required == "free")
    )
    total_count = await db.scalar(select(func.count()).select_from(chapters))

    if user_tier == "premium":
        accessible = total_count
        locked = 0
    else:
        accessible = free_count
        locked = (total_count or 0) - (free_count or 0)

    return TierInfo(
        user_id=user_id,
        tier=user_tier,
        free_chapters_count=free_count or 0,
        total_chapters_accessible=accessible or 0,
        locked_chapters_count=locked,
    )
