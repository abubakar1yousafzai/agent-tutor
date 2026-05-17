from pathlib import Path
from fastapi import HTTPException

# Chapter files live at backend/content/chapters/chapter-XX.md
CHAPTERS_DIR = Path(__file__).parent.parent / "content" / "chapters"


async def fetch_chapter_content(chapter_id: str) -> str:
    """Read chapter markdown from local filesystem."""
    file_path = CHAPTERS_DIR / f"{chapter_id}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_id}' content not found")
    return file_path.read_text(encoding="utf-8")


def get_local_content(chapter_id: str) -> str | None:
    """Synchronous read for seeding — returns None if file missing."""
    file_path = CHAPTERS_DIR / f"{chapter_id}.md"
    if not file_path.exists():
        return None
    return file_path.read_text(encoding="utf-8")
