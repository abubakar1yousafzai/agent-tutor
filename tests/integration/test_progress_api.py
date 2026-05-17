import pytest


@pytest.mark.asyncio
async def test_get_progress_empty(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/progress/{free_user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapters_completed"] == 0
    assert data["completion_percentage"] == 0
    assert data["streak_days"] == 0


@pytest.mark.asyncio
async def test_complete_chapter_increments_streak(test_client, free_user, sample_chapters):
    resp = await test_client.post(
        f"/progress/{free_user['id']}/chapters/chapter-01/complete"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapters_completed"] == 1
    assert data["streak_days"] >= 1
    assert "streak!" in data["message"]


@pytest.mark.asyncio
async def test_complete_chapter_idempotent(test_client, free_user, sample_chapters):
    await test_client.post(f"/progress/{free_user['id']}/chapters/chapter-01/complete")
    resp = await test_client.post(f"/progress/{free_user['id']}/chapters/chapter-01/complete")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complete_premium_chapter_blocked_for_free(test_client, free_user):
    resp = await test_client.post(
        f"/progress/{free_user['id']}/chapters/chapter-05/complete"
    )
    assert resp.status_code in (403, 404)


@pytest.mark.asyncio
async def test_progress_summary_after_completion(test_client, free_user, sample_chapters):
    await test_client.post(f"/progress/{free_user['id']}/chapters/chapter-01/complete")
    await test_client.post(f"/progress/{free_user['id']}/chapters/chapter-02/complete")
    resp = await test_client.get(f"/progress/{free_user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapters_completed"] == 2
    assert data["completion_percentage"] > 0
