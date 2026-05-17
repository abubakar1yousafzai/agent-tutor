import pytest


@pytest.mark.asyncio
async def test_get_quiz_questions_free_chapter(test_client, free_user, sample_quiz_bank):
    resp = await test_client.get(f"/quizzes/chapter-01/questions?user_id={free_user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapter_id"] == "chapter-01"
    assert data["total_questions"] == 5
    for q in data["questions"]:
        assert "correct_answer" not in q
        assert "options" in q


@pytest.mark.asyncio
async def test_quiz_blocked_for_free_user_premium_chapter(test_client, free_user):
    resp = await test_client.get(f"/quizzes/chapter-05/questions?user_id={free_user['id']}")
    assert resp.status_code in (403, 404)


@pytest.mark.asyncio
async def test_submit_quiz_perfect(test_client, free_user, sample_quiz_bank):
    answers = {str(i): "A" for i in range(1, 6)}
    resp = await test_client.post(
        f"/quizzes/chapter-01/submit?user_id={free_user['id']}",
        json={"answers": answers},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 5
    assert data["passed"] is True
    assert "correct_answer" not in data


@pytest.mark.asyncio
async def test_submit_quiz_fail(test_client, free_user, sample_quiz_bank):
    answers = {str(i): "D" for i in range(1, 6)}
    resp = await test_client.post(
        f"/quizzes/chapter-01/submit?user_id={free_user['id']}",
        json={"answers": answers},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is False
