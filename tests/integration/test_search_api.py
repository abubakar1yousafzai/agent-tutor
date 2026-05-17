import pytest
from sqlalchemy import update
from backend.db.tables import chapters


@pytest.mark.asyncio
async def test_search_returns_results(test_client, free_user, sample_chapters, async_session):
    await async_session.execute(
        update(chapters)
        .where(chapters.c.id == "chapter-01")
        .values(search_text="Python is a versatile programming language used in many domains.")
    )
    await async_session.commit()

    resp = await test_client.get(f"/search?user_id={free_user['id']}&q=Python")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "Python"
    assert data["total"] >= 1
    assert any("Python" in r["excerpt"] for r in data["results"])


@pytest.mark.asyncio
async def test_search_min_length(test_client, free_user):
    resp = await test_client.get(f"/search?user_id={free_user['id']}&q=a")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_no_results(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/search?user_id={free_user['id']}&q=xyznonexistent")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_search_user_not_found(test_client):
    resp = await test_client.get(
        "/search?user_id=00000000-0000-0000-0000-000000000000&q=test"
    )
    assert resp.status_code == 404
