"""Conversation business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.Conversation import Conversation
from app.models.User import User
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ConversationCreate, ConversationResponse


class ConversationService:
    """Handles conversation creation and organization-scoped queries."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversation_repo = ConversationRepository(db)

    def create_conversation(
        self,
        data: ConversationCreate,
        current_user: User,
    ) -> ConversationResponse:
        """Create a new conversation for the authenticated user."""
        conversation = Conversation(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            title=data.title,
        )
        created = self.conversation_repo.create_conversation(conversation)
        return ConversationResponse.model_validate(created)

    def get_user_conversations(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConversationResponse]:
        """Return conversations owned by the current user."""
        conversations = self.conversation_repo.get_user_conversations(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            skip=skip,
            limit=limit,
        )
        return [ConversationResponse.model_validate(conv) for conv in conversations]

    def get_conversation(
        self,
        conversation_id: uuid.UUID,
        current_user: User,
    ) -> ConversationResponse:
        """Return a conversation with messages, scoped to the user's organization."""
        conversation = self.conversation_repo.get_conversation_with_messages(
            conversation_id=conversation_id,
            organization_id=current_user.organization_id,
        )
        if conversation is None or conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        return ConversationResponse.model_validate(conversation)
