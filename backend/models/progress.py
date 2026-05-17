from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID


class ChapterProgressItem(BaseModel):
    chapter_id: str
    chapter_title: str
    completed: bool
    completed_at: datetime | None
    best_quiz_score: int | None


class ProgressSummary(BaseModel):
    user_id: UUID
    chapters_completed: int
    total_accessible_chapters: int
    completion_percentage: int
    streak_days: int
    last_active: date | None
    chapter_progress: list[ChapterProgressItem]


class StreakUpdate(BaseModel):
    user_id: UUID
    chapter_id: str
    streak_days: int
    chapters_completed: int
    message: str
