"""Conversation and message data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.Conversation import Conversation
from app.models.Message import Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for conversation and message operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Conversation)

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation record."""
        return self.create(conversation)

    def get_user_conversations(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Conversation]:
        """Return conversations owned by a user within an organization."""
        stmt = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.organization_id == organization_id,
            )
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def add_message(self, message: Message) -> Message:
        """Persist a new message in a conversation."""
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(
        self,
        conversation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[Message]:
        """Return messages for a conversation scoped to an organization."""
        stmt = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.organization_id == organization_id,
            )
            .order_by(Message.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_conversation_with_messages(
        self,
        conversation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Conversation | None:
        """Return a conversation with eagerly loaded messages."""
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id,
            )
        )
        return self.db.scalars(stmt).first()
