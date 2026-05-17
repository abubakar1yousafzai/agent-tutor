from pydantic import BaseModel, EmailStr
from typing import Literal
from datetime import date, datetime
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class User(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    tier: Literal["free", "premium"]
    streak_days: int
    last_active: date | None
    created_at: datetime

    model_config = {"from_attributes": True}
