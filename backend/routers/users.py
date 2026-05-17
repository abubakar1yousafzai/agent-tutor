from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from uuid import UUID
import uuid

from backend.db.connection import get_db
from backend.db.tables import users
from backend.models.user import User, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=User, status_code=201)
async def upsert_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(users).where(users.c.email == body.email))
    row = result.mappings().first()
    if row:
        return User.model_validate(dict(row))

    new_id = uuid.uuid4()
    await db.execute(insert(users).values(id=new_id, email=body.email, name=body.name))
    await db.commit()

    result = await db.execute(select(users).where(users.c.id == new_id))
    return User.model_validate(dict(result.mappings().one()))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(users).where(users.c.id == user_id))
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return User.model_validate(dict(row))
