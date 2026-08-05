"""Document chunk data access layer."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.DocumentChunk import DocumentChunk
from app.repositories.base import BaseRepository


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for tenant-scoped document chunk persistence."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, DocumentChunk)

    def create_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        """Persist a single chunk record."""
        return self.create(chunk)

    def create_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        """Persist multiple chunk records in a single transaction."""
        for chunk in chunks:
            self.add(chunk)
        self.db.commit()
        for chunk in chunks:
            self.db.refresh(chunk)
        return chunks

    def get_document_chunks(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[DocumentChunk]:
        """Return chunks for a document scoped to an organization."""
        stmt = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.organization_id == organization_id,
            )
            .order_by(DocumentChunk.chunk_index.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_org_chunks(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentChunk]:
        """Return chunks belonging to an organization."""
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.organization_id == organization_id)
            .order_by(DocumentChunk.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_chunks_by_ids(
        self,
        chunk_ids: list[uuid.UUID],
        organization_id: uuid.UUID,
    ) -> list[DocumentChunk]:
        """Return chunks by ID scoped to an organization."""
        if not chunk_ids:
            return []

        stmt = select(DocumentChunk).where(
            DocumentChunk.id.in_(chunk_ids),
            DocumentChunk.organization_id == organization_id,
        )
        return list(self.db.scalars(stmt).all())

    def delete_chunks_by_document(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> None:
        """Remove all chunks for a document within an organization."""
        stmt = delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.organization_id == organization_id,
        )
        self.db.execute(stmt)
        self.db.commit()
