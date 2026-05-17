from pydantic import BaseModel


class SearchResult(BaseModel):
    chapter_id: str
    chapter_title: str
    chapter_number: int
    excerpt: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
