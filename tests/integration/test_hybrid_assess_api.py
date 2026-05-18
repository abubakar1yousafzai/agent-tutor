import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_assess_free_user_returns_403(test_client, free_user):
    response = await test_client.post(
        "/hybrid/assess",
        json={
            "user_id": str(free_user["id"]),
            "chapter_id": "chapter-01",
            "question": "What is an agent?",
            "student_answer": "An agent is an AI system.",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "premium_required"


@pytest.mark.asyncio
async def test_assess_premium_user_returns_result(test_client, premium_user):
    mock_parsed = {
        "score": 8,
        "max_score": 10,
        "grade": "B+",
        "feedback": "Good.",
        "what_was_correct": "X",
        "what_was_missing": "Y",
        "improvement_tip": "Z",
    }

    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=mock_parsed):
        response = await test_client.post(
            "/hybrid/assess",
            json={
                "user_id": str(premium_user["id"]),
                "chapter_id": "chapter-01",
                "question": "What is an agent?",
                "student_answer": "An agent perceives and acts on its environment.",
            },
        )

    assert response.status_code == 200
    body = response.json()
    for field in [
        "score", "max_score", "grade", "feedback",
        "what_was_correct", "what_was_missing", "improvement_tip", "estimated_cost_usd",
    ]:
        assert field in body, f"Missing field: {field}"
    assert body["estimated_cost_usd"] == 0.014
