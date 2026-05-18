import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_mentor_free_user_returns_403(test_client, free_user):
    response = await test_client.post(
        "/hybrid/mentor",
        json={
            "user_id": str(free_user["id"]),
            "question": "Can you explain what an AI agent is?",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "premium_required"


@pytest.mark.asyncio
async def test_mentor_premium_user_returns_result(test_client, premium_user):
    mock_return = ("Great question! Let me check the chapter.", [], [])

    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=mock_return):
        response = await test_client.post(
            "/hybrid/mentor",
            json={
                "user_id": str(premium_user["id"]),
                "question": "Can you explain what an AI agent is?",
            },
        )

    assert response.status_code == 200
    body = response.json()
    for field in ["mentor_response", "chapters_referenced", "tools_used", "estimated_cost_usd"]:
        assert field in body, f"Missing field: {field}"
    assert body["estimated_cost_usd"] == 0.090
