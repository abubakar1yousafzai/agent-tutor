import pytest
from backend.routers.quizzes import grade_quiz, QUIZ_PASS_THRESHOLD


CORRECT = {1: "A", 2: "B", 3: "C", 4: "D", 5: "A"}


def test_perfect_score():
    answers = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A"}
    result = grade_quiz(answers, CORRECT)
    assert result["score"] == 5
    assert result["total"] == 5
    assert result["percentage"] == 100
    assert result["passed"] is True
    assert result["wrong_question_numbers"] == []


def test_fail_below_threshold():
    answers = {"1": "B", "2": "A", "3": "A", "4": "A", "5": "B"}
    result = grade_quiz(answers, CORRECT)
    assert result["score"] == 0
    assert result["passed"] is False
    assert sorted(result["wrong_question_numbers"]) == [1, 2, 3, 4, 5]


def test_pass_at_threshold():
    answers = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "B"}
    result = grade_quiz(answers, CORRECT)
    assert result["score"] == QUIZ_PASS_THRESHOLD
    assert result["passed"] is True


def test_one_wrong():
    answers = {"1": "B", "2": "B", "3": "C", "4": "D", "5": "A"}
    result = grade_quiz(answers, CORRECT)
    assert result["score"] == 4
    assert result["wrong_question_numbers"] == [1]
    assert result["passed"] is True


def test_correct_answer_not_exposed():
    """Verify grade_quiz never returns correct answers to caller."""
    result = grade_quiz({"1": "A"}, {1: "A"})
    assert "correct_answer" not in result
    assert "correct_answers" not in result


def test_percentage_calculation():
    answers = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "B"}
    result = grade_quiz(answers, CORRECT)
    assert result["percentage"] == 80


def test_empty_submission():
    result = grade_quiz({}, CORRECT)
    assert result["score"] == 0
    assert result["passed"] is False
