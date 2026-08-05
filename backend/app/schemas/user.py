"""User request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.User import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
