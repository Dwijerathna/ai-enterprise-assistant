"""Conversation API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.User import User
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
)
from app.security.dependencies import get_current_user
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


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


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "AI generation service unavailable"},
    },
)
def send_message(
    conversation_id: UUID,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatMessageResponse:
    """Send a message to an existing conversation."""
    return chat_service.send_message(
        conversation_id=conversation_id,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        request=request,
    )
