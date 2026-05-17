from pydantic import BaseModel
from typing import Literal


class Question(BaseModel):
    question_number: int
    question: str
    options: dict[str, str]  # {"A": "...", "B": "...", "C": "...", "D": "..."}
    # correct_answer intentionally excluded


class QuizQuestions(BaseModel):
    chapter_id: str
    chapter_title: str
    total_questions: int
    questions: list[Question]


class QuizSubmission(BaseModel):
    answers: dict[str, Literal["A", "B", "C", "D"]]  # {"1": "B", "2": "A", ...}


class QuizResult(BaseModel):
    chapter_id: str
    score: int
    total: int
    percentage: int
    passed: bool
    wrong_question_numbers: list[int]
