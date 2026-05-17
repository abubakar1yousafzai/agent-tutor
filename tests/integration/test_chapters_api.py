import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_list_chapters_free_user(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/chapters?user_id={free_user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(sample_chapters)
    for ch in data:
        if ch["id"] in {"chapter-01", "chapter-02", "chapter-03"}:
            assert ch["is_accessible"] is True


@pytest.mark.asyncio
async def test_list_chapters_premium_user(test_client, premium_user, sample_chapters):
    resp = await test_client.get(f"/chapters?user_id={premium_user['id']}")
    assert resp.status_code == 200
    for ch in resp.json():
        assert ch["is_accessible"] is True


@pytest.mark.asyncio
async def test_get_chapter_content_free(test_client, free_user, sample_chapters):
    fake_content = "# Chapter 1\n\nIntro content."
    with patch("backend.routers.chapters.fetch_chapter_content", return_value=fake_content):
        resp = await test_client.get(f"/chapters/chapter-01/content?user_id={free_user['id']}")
    assert resp.status_code == 200
    assert resp.json()["content"] == fake_content


@pytest.mark.asyncio
async def test_get_premium_chapter_blocked_for_free(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/chapters/chapter-04/content?user_id={free_user['id']}")
    assert resp.status_code in (403, 404)


@pytest.mark.asyncio
async def test_next_chapter(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/chapters/chapter-01/next?user_id={free_user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data is None or data["number"] == 2


@pytest.mark.asyncio
async def test_previous_chapter_none_for_first(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/chapters/chapter-01/previous?user_id={free_user['id']}")
    assert resp.status_code == 200
    assert resp.json() is None
