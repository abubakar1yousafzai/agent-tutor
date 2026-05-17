"""
Contract tests: verify API responses conform to OpenAPI schema shapes.
"""
import pytest
import uuid


@pytest.mark.asyncio
async def test_health_contract(test_client):
    resp = await test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "llm_calls" in data
    assert data["llm_calls"] == 0


@pytest.mark.asyncio
async def test_user_create_contract(test_client):
    resp = await test_client.post(
        "/users", json={"email": "contract@test.com", "name": "Contract User"}
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    required_fields = {"id", "email", "name", "tier", "streak_days", "created_at"}
    assert required_fields.issubset(data.keys())
    assert data["tier"] in ("free", "premium")


@pytest.mark.asyncio
async def test_chapters_list_contract(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/chapters?user_id={free_user['id']}")
    assert resp.status_code == 200
    for ch in resp.json():
        assert {"id", "number", "title", "tier_required", "is_accessible"}.issubset(ch.keys())


@pytest.mark.asyncio
async def test_access_check_contract(test_client, free_user, sample_chapters):
    resp = await test_client.get(
        f"/access/check?user_id={free_user['id']}&chapter_id=chapter-01"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert {"user_id", "chapter_id", "allowed", "reason"}.issubset(data.keys())
    assert isinstance(data["allowed"], bool)


@pytest.mark.asyncio
async def test_progress_summary_contract(test_client, free_user, sample_chapters):
    resp = await test_client.get(f"/progress/{free_user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    required = {
        "user_id", "chapters_completed", "total_accessible_chapters",
        "completion_percentage", "streak_days", "chapter_progress"
    }
    assert required.issubset(data.keys())
    assert isinstance(data["chapter_progress"], list)
