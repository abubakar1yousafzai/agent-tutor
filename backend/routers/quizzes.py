from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from uuid import UUID
import uuid

from backend.db.connection import get_db
from backend.db.tables import users, chapters, quiz_bank, quiz_results
from backend.models.quiz import Question, QuizQuestions, QuizSubmission, QuizResult
from backend.routers.chapters import FREE_CHAPTERS

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

QUIZ_PASS_THRESHOLD = 4


def grade_quiz(
    student_answers: dict[str, str],
    correct_answers: dict[int, str],
) -> dict:
    wrong = [
        int(q) for q, ans in student_answers.items()
        if correct_answers.get(int(q)) != ans
    ]
    score = len(student_answers) - len(wrong)
    total = len(correct_answers)
    return {
        "score": score,
        "total": total,
        "percentage": round(score / total * 100) if total > 0 else 0,
        "passed": score >= QUIZ_PASS_THRESHOLD,
        "wrong_question_numbers": sorted(wrong),
    }


async def _check_chapter_access(chapter_id: str, user_id: UUID, db: AsyncSession) -> str:
    user_result = await db.execute(select(users.c.tier).where(users.c.id == user_id))
    user_row = user_result.first()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    user_tier = user_row[0]

    ch_result = await db.execute(select(chapters.c.tier_required).where(chapters.c.id == chapter_id))
    ch_row = ch_result.first()
    if not ch_row:
        raise HTTPException(status_code=404, detail="Chapter not found")

    if chapter_id not in FREE_CHAPTERS and user_tier != "premium":
        raise HTTPException(
            status_code=403,
            detail={"error": "premium_required", "message": "This quiz requires a Premium subscription."},
        )
    return user_tier


@router.get("/{chapter_id}/questions", response_model=QuizQuestions)
async def get_quiz_questions(
    chapter_id: str,
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    await _check_chapter_access(chapter_id, user_id, db)

    ch_result = await db.execute(select(chapters.c.title).where(chapters.c.id == chapter_id))
    ch_row = ch_result.first()
    if not ch_row:
        raise HTTPException(status_code=404, detail="Chapter not found")

    qb_result = await db.execute(
        select(quiz_bank)
        .where(quiz_bank.c.chapter_id == chapter_id)
        .order_by(quiz_bank.c.question_number)
    )
    rows = qb_result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No quiz found for this chapter")

    questions = [
        Question(
            question_number=r["question_number"],
            question=r["question"],
            options={"A": r["option_a"], "B": r["option_b"], "C": r["option_c"], "D": r["option_d"]},
        )
        for r in rows
    ]
    return QuizQuestions(
        chapter_id=chapter_id,
        chapter_title=ch_row[0],
        total_questions=len(questions),
        questions=questions,
    )


@router.post("/{chapter_id}/submit", response_model=QuizResult)
async def submit_quiz(
    chapter_id: str,
    body: QuizSubmission,
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    await _check_chapter_access(chapter_id, user_id, db)

    qb_result = await db.execute(
        select(quiz_bank.c.question_number, quiz_bank.c.correct_answer)
        .where(quiz_bank.c.chapter_id == chapter_id)
    )
    correct_answers = {r[0]: r[1] for r in qb_result.all()}
    if not correct_answers:
        raise HTTPException(status_code=404, detail="No quiz found for this chapter")

    graded = grade_quiz(body.answers, correct_answers)

    await db.execute(insert(quiz_results).values(
        id=uuid.uuid4(),
        user_id=user_id,
        chapter_id=chapter_id,
        score=graded["score"],
        total_questions=graded["total"],
        answers=body.answers,
    ))
    await db.commit()

    return QuizResult(chapter_id=chapter_id, **graded)
