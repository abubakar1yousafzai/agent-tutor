import pytest


@pytest.mark.asyncio
async def test_free_chapter_accessible_to_free(test_client, free_user, sample_chapters):
    resp = await test_client.get(
        f"/access/check?user_id={free_user['id']}&chapter_id=chapter-01"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is True
    assert data["reason"] == "free_chapter"


@pytest.mark.asyncio
async def test_premium_chapter_blocked_for_free(test_client, free_user, sample_chapters):
    resp = await test_client.get(
        f"/access/check?user_id={free_user['id']}&chapter_id=chapter-05"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is False
    assert data["reason"] == "premium_required"
    assert data["upgrade_message"] is not None


@pytest.mark.asyncio
async def test_premium_chapter_accessible_to_premium(test_client, premium_user, sample_chapters):
    resp = await test_client.get(
        f"/access/check?user_id={premium_user['id']}&chapter_id=chapter-05"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is True
    assert data["reason"] == "premium_user"


@pytest.mark.asyncio
async def test_tier_info_free(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/access/{free_user['id']}/tier")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "free"
    assert data["locked_chapters_count"] >= 0


@pytest.mark.asyncio
async def test_tier_info_premium(test_client, premium_user, sample_chapters):
    resp = await test_client.get(f"/access/{premium_user['id']}/tier")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "premium"
    assert data["locked_chapters_count"] == 0
