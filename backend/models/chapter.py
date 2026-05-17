from pydantic import BaseModel
from typing import Literal


class ChapterNavigation(BaseModel):
    id: str
    number: int
    title: str
    tier_required: Literal["free", "premium"]
    is_accessible: bool


class ChapterSummary(BaseModel):
    id: str
    number: int
    title: str
    tier_required: Literal["free", "premium"]
    is_accessible: bool


class ChapterContent(BaseModel):
    id: str
    number: int
    title: str
    content: str
    next_chapter: ChapterNavigation | None
    previous_chapter: ChapterNavigation | None
