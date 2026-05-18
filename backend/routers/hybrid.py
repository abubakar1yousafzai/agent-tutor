import asyncio
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.connection import get_db
from backend.db.tables import users, progress, quiz_results

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Hybrid Intelligence"])


class AssessRequest(BaseModel):
    user_id: UUID
    chapter_id: str
    question: str
    student_answer: str


class AssessResponse(BaseModel):
    score: int
    max_score: int
    grade: str
    feedback: str
    what_was_correct: str
    what_was_missing: str
    improvement_tip: str
    estimated_cost_usd: float


class MentorRequest(BaseModel):
    user_id: UUID
    question: str


class MentorResponse(BaseModel):
    mentor_response: str
    chapters_referenced: list[str]
    tools_used: list[str]
    estimated_cost_usd: float


async def _require_premium(user_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(select(users.c.tier).where(users.c.id == user_id))
    row = result.first()
    if row is None or row[0] == "free":
        raise HTTPException(
            status_code=403,
            detail={"error": "premium_required", "detail": "This feature requires a premium subscription."},
        )


async def _fetch_progress_summary(user_id: UUID, db: AsyncSession) -> str:
    prog_result = await db.execute(
        select(progress.c.chapter_id, progress.c.completed)
        .where(progress.c.user_id == user_id, progress.c.completed == True)
    )
    completed_chapters = [row[0] for row in prog_result.all()]

    score_result = await db.execute(
        select(quiz_results.c.chapter_id, func.max(quiz_results.c.score).label("best"))
        .where(quiz_results.c.user_id == user_id)
        .group_by(quiz_results.c.chapter_id)
    )
    score_map = {row[0]: row[1] for row in score_result.all()}

    if not completed_chapters and not score_map:
        return "Student has not completed any chapters or quizzes yet."

    lines = ["Student progress summary:"]
    for chapter_id in completed_chapters:
        best = score_map.get(chapter_id)
        score_str = f" (best quiz score: {best})" if best is not None else ""
        lines.append(f"  - {chapter_id}: completed{score_str}")
    for chapter_id, best in score_map.items():
        if chapter_id not in completed_chapters:
            lines.append(f"  - {chapter_id}: quiz attempted (best score: {best})")
    return "\n".join(lines)


@router.post("/assess", response_model=AssessResponse)
async def assess_answer(body: AssessRequest, db: AsyncSession = Depends(get_db)):
    from backend.agents.assessor_agent import run_assessment
    from backend.storage.content_reader import get_local_content

    await _require_premium(body.user_id, db)

    content = get_local_content(body.chapter_id)
    if content is None:
        raise HTTPException(status_code=404, detail=f"Chapter '{body.chapter_id}' content not found")

    try:
        parsed = await asyncio.to_thread(run_assessment, content, body.question, body.student_answer)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Assessment failed: could not parse AI response")

    logger.info("assess cost=0.014 user=%s chapter=%s", body.user_id, body.chapter_id)
    return AssessResponse(**parsed, estimated_cost_usd=0.014)


@router.post("/mentor", response_model=MentorResponse)
async def mentor_session(body: MentorRequest, db: AsyncSession = Depends(get_db)):
    from backend.agents.mentor_agent import run_mentor

    await _require_premium(body.user_id, db)

    progress_summary = await _fetch_progress_summary(body.user_id, db)

    try:
        mentor_response, chapters_referenced, tools_used = await asyncio.to_thread(
            run_mentor, body.question, progress_summary
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Mentor session failed.")

    logger.info("mentor cost=0.090 user=%s tools=%s", body.user_id, tools_used)
    return MentorResponse(
        mentor_response=mentor_response,
        chapters_referenced=chapters_referenced,
        tools_used=tools_used,
        estimated_cost_usd=0.090,
    )
