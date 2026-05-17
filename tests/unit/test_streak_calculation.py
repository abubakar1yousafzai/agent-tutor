from datetime import date, timedelta
from backend.routers.progress import update_streak


def test_first_activity():
    streak, last = update_streak(None, 0)
    assert streak == 1
    assert last == date.today()


def test_same_day_idempotent():
    today = date.today()
    streak, last = update_streak(today, 5)
    assert streak == 5
    assert last == today


def test_consecutive_day_increments():
    yesterday = date.today() - timedelta(days=1)
    streak, last = update_streak(yesterday, 3)
    assert streak == 4
    assert last == date.today()


def test_gap_resets_streak():
    two_days_ago = date.today() - timedelta(days=2)
    streak, last = update_streak(two_days_ago, 10)
    assert streak == 1
    assert last == date.today()


def test_large_gap_resets():
    old_date = date.today() - timedelta(days=30)
    streak, last = update_streak(old_date, 25)
    assert streak == 1


def test_first_day_streak_is_one():
    streak, _ = update_streak(None, 0)
    assert streak == 1
