"""Conversation and chat request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.Message import MessageRole, MessageProcessingStatus
from app.schemas.retrieval import RetrievedChunkResponse


class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    organization_id: UUID
    role: MessageRole
    content: str
    processing_status: MessageProcessingStatus
    model_name: str | None = None
    error_message: str | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    messages: list[MessageResponse] = []


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)
    retrieval_limit: int = Field(default=5, ge=1, le=20)


class ChatMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: list[RetrievedChunkResponse] = []
    retrieval_status: str = "ok"
    retrieval_message: str | None = None
