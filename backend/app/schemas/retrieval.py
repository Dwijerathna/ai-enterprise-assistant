"""Retrieval request and response schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    limit: int = Field(default=5, ge=1, le=20)


class RetrievedChunkResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    content: str
    page_number: int | None = None
    section_title: str | None = None
    document_name: str | None = None
    similarity_score: float
    chunk_index: int
    embedding_model: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunkResponse]
    total: int
    status: str = "ok"
    message: str | None = None
