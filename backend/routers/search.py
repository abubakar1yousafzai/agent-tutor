from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from uuid import UUID

from backend.db.connection import get_db
from backend.db.tables import users, chapters
from backend.models.search import SearchResult, SearchResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
async def search_content(
    user_id: UUID = Query(...),
    q: str = Query(..., min_length=2),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(users.c.tier).where(users.c.id == user_id))
    user_row = user_result.first()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    user_tier = user_row[0]

    allowed_tiers = ["free"] if user_tier == "free" else ["free", "premium"]
    pattern = f"%{q.lower()}%"

    result = await db.execute(
        select(
            chapters.c.id,
            chapters.c.title,
            chapters.c.number,
            chapters.c.search_text,
        )
        .where(
            chapters.c.tier_required.in_(allowed_tiers),
            chapters.c.search_text.isnot(None),
        )
        .order_by(chapters.c.number)
        .limit(limit)
    )
    rows = result.mappings().all()

    results = []
    for r in rows:
        text_lower = (r["search_text"] or "").lower()
        pos = text_lower.find(q.lower())
        if pos == -1:
            continue
        start = max(0, pos - 100)
        excerpt = r["search_text"][start: start + 300].strip()
        results.append(SearchResult(
            chapter_id=r["id"],
            chapter_title=r["title"],
            chapter_number=r["number"],
            excerpt=excerpt,
        ))

    return SearchResponse(query=q, results=results, total=len(results))
