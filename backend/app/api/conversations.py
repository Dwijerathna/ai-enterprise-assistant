"""Conversation API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.User import User
from app.schemas.chat import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
)
from app.security.dependencies import get_current_user
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """Create a new AI conversation for the authenticated user."""
    return conversation_service.create_conversation(data, current_user)


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationListResponse:
    """Return conversations owned by the authenticated user."""
    conversations = conversation_service.get_user_conversations(current_user)
    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations),
    )
