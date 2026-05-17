from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func
from datetime import date, timedelta, datetime, timezone
from uuid import UUID
import uuid

from backend.db.connection import get_db
from backend.db.tables import users, chapters, progress, quiz_results
from backend.models.progress import ProgressSummary, StreakUpdate, ChapterProgressItem
from backend.routers.chapters import FREE_CHAPTERS

router = APIRouter(prefix="/progress", tags=["Progress"])

STREAK_MESSAGES = [
    "Great work! Keep it up!",
    "You're on a roll! 🔥",
    "Amazing dedication! 🎯",
    "Unstoppable! 🚀",
]


def update_streak(last_active: date | None, streak_days: int) -> tuple[int, date]:
    today = date.today()
    if last_active is None:
        return 1, today
    if last_active == today:
        return streak_days, today
    if last_active == today - timedelta(days=1):
        return streak_days + 1, today
    return 1, today


@router.get("/{user_id}", response_model=ProgressSummary)
async def get_progress(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(
        select(users.c.tier, users.c.streak_days, users.c.last_active)
        .where(users.c.id == user_id)
    )
    user_row = user_result.first()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    user_tier, streak_days, last_active = user_row

    allowed_tiers = ["free"] if user_tier == "free" else ["free", "premium"]
    ch_result = await db.execute(
        select(chapters).where(chapters.c.tier_required.in_(allowed_tiers)).order_by(chapters.c.number)
    )
    all_chapters = ch_result.mappings().all()
    total_accessible = len(all_chapters)

    prog_result = await db.execute(
        select(progress).where(progress.c.user_id == user_id)
    )
    prog_map = {r["chapter_id"]: r for r in prog_result.mappings().all()}

    qr_result = await db.execute(
        select(quiz_results.c.chapter_id, func.max(quiz_results.c.score).label("best"))
        .where(quiz_results.c.user_id == user_id)
        .group_by(quiz_results.c.chapter_id)
    )
    score_map = {r[0]: r[1] for r in qr_result.all()}

    chapter_progress = []
    completed_count = 0
    for ch in all_chapters:
        p = prog_map.get(ch["id"])
        completed = p["completed"] if p else False
        if completed:
            completed_count += 1
        chapter_progress.append(ChapterProgressItem(
            chapter_id=ch["id"],
            chapter_title=ch["title"],
            completed=completed,
            completed_at=p["completed_at"] if p else None,
            best_quiz_score=score_map.get(ch["id"]),
        ))

    pct = round(completed_count / total_accessible * 100) if total_accessible > 0 else 0
    return ProgressSummary(
        user_id=user_id,
        chapters_completed=completed_count,
        total_accessible_chapters=total_accessible,
        completion_percentage=pct,
        streak_days=streak_days,
        last_active=last_active,
        chapter_progress=chapter_progress,
    )


@router.post("/{user_id}/chapters/{chapter_id}/complete", response_model=StreakUpdate)
async def complete_chapter(
    user_id: UUID,
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(
        select(users.c.tier, users.c.streak_days, users.c.last_active)
        .where(users.c.id == user_id)
    )
    user_row = user_result.first()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    user_tier, streak_days, last_active = user_row

    if chapter_id not in FREE_CHAPTERS and user_tier != "premium":
        raise HTTPException(status_code=403, detail="Access denied to this chapter")

    ch_result = await db.execute(select(chapters.c.id).where(chapters.c.id == chapter_id))
    if not ch_result.first():
        raise HTTPException(status_code=404, detail="Chapter not found")

    now = datetime.now(timezone.utc)
    existing = await db.execute(
        select(progress).where(
            progress.c.user_id == user_id,
            progress.c.chapter_id == chapter_id,
        )
    )
    if existing.first():
        await db.execute(
            update(progress)
            .where(progress.c.user_id == user_id, progress.c.chapter_id == chapter_id)
            .values(completed=True, completed_at=now)
        )
    else:
        await db.execute(insert(progress).values(
            id=uuid.uuid4(),
            user_id=user_id,
            chapter_id=chapter_id,
            completed=True,
            completed_at=now,
        ))

    new_streak, new_last_active = update_streak(last_active, streak_days)
    await db.execute(
        update(users)
        .where(users.c.id == user_id)
        .values(streak_days=new_streak, last_active=new_last_active)
    )
    await db.commit()

    count_result = await db.execute(
        select(func.count()).select_from(progress)
        .where(progress.c.user_id == user_id, progress.c.completed == True)
    )
    completed_count = count_result.scalar() or 0

    msg_idx = min(new_streak - 1, len(STREAK_MESSAGES) - 1)
    return StreakUpdate(
        user_id=user_id,
        chapter_id=chapter_id,
        streak_days=new_streak,
        chapters_completed=completed_count,
        message=f"{STREAK_MESSAGES[msg_idx]} {new_streak}-day streak!",
    )
