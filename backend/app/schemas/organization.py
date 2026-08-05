"""Organization request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    qdrant_collection_name: str
    created_at: datetime


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
