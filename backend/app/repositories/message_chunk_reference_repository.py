"""Message chunk reference data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.MessageChunkReference import MessageChunkReference
from app.repositories.base import BaseRepository


class MessageChunkReferenceRepository(BaseRepository[MessageChunkReference]):
    """Repository for message citation references."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, MessageChunkReference)

    def create_reference(self, reference: MessageChunkReference) -> MessageChunkReference:
        return self.create(reference)

    def create_references(
        self,
        references: list[MessageChunkReference],
    ) -> list[MessageChunkReference]:
        for reference in references:
            self.add(reference)
        self.db.commit()
        for reference in references:
            self.db.refresh(reference)
        return references

    def get_references_for_message(
        self,
        message_id: uuid.UUID,
    ) -> list[MessageChunkReference]:
        stmt = (
            select(MessageChunkReference)
            .where(MessageChunkReference.message_id == message_id)
            .order_by(MessageChunkReference.similarity_score.desc())
        )
        return list(self.db.scalars(stmt).all())
