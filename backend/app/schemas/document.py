"""Document request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.Document import DocumentStatus


class DocumentCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=512)
    file_path: str = Field(..., min_length=1, max_length=1024)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    uploaded_by: UUID | None
    filename: str
    file_path: str
    status: DocumentStatus
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
