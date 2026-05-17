from pydantic import BaseModel
from typing import Literal
from uuid import UUID


class AccessCheck(BaseModel):
    user_id: UUID
    chapter_id: str
    allowed: bool
    reason: Literal["free_chapter", "premium_user", "premium_required"]
    upgrade_message: str | None = None


class TierInfo(BaseModel):
    user_id: UUID
    tier: Literal["free", "premium"]
    free_chapters_count: int
    total_chapters_accessible: int
    locked_chapters_count: int
