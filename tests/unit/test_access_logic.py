import pytest
from backend.routers.chapters import FREE_CHAPTERS, _is_accessible


@pytest.mark.parametrize("chapter_id,user_tier,expected", [
    ("chapter-01", "free", True),
    ("chapter-02", "free", True),
    ("chapter-03", "free", True),
    ("chapter-04", "free", False),
    ("chapter-10", "free", False),
    ("chapter-04", "premium", True),
    ("chapter-10", "premium", True),
    ("chapter-01", "premium", True),
])
def test_is_accessible(chapter_id, user_tier, expected):
    assert _is_accessible("free" if chapter_id in FREE_CHAPTERS else "premium", user_tier, chapter_id) == expected


def test_free_chapters_set():
    assert FREE_CHAPTERS == {"chapter-01", "chapter-02", "chapter-03"}
    assert len(FREE_CHAPTERS) == 3


def test_premium_chapters_not_in_free():
    for i in range(4, 11):
        assert f"chapter-0{i}" not in FREE_CHAPTERS
