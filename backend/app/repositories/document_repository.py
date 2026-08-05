"""Document data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.Document import Document, DocumentStatus
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for document CRUD and tenant-scoped queries."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Document)

    def create_document(self, document: Document) -> Document:
        """Persist a new document record."""
        return self.create(document)

    def update_status(
        self,
        document: Document,
        status: DocumentStatus,
    ) -> Document:
        """Update the processing status of a document."""
        return self.update(document, {"status": status})

    def get_user_documents(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        """Return documents uploaded by a user within an organization."""
        stmt = (
            select(Document)
            .where(
                Document.uploaded_by == user_id,
                Document.organization_id == organization_id,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_org_documents(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        """Return all documents belonging to an organization."""
        stmt = (
            select(Document)
            .where(Document.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
