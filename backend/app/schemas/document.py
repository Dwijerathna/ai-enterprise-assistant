"""Document request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.Document import DocumentStatus


class DocumentCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=512)

    @field_validator("filename")
    @classmethod
    def reject_path_like_filename(cls, value: str) -> str:
        if ".." in value or "/" in value or "\\" in value:
            raise ValueError("Filename must not contain path separators or traversal patterns")
        return value.strip()


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    uploaded_by: UUID | None
    filename: str
    status: DocumentStatus
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
