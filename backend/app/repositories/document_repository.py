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

    def get_by_id(self, record_id: uuid.UUID) -> Document | None:
        """Return a single record by primary key."""
        return self.db.get(self.model, record_id)

    def get_by_id_and_organization(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Document | None:
        """Return a document scoped to an organization."""
        stmt = select(Document).where(
            Document.id == document_id,
            Document.organization_id == organization_id,
        )
        return self.db.scalars(stmt).first()

    def increment_retry_count(self, document: Document) -> Document:
        """Increment the document retry counter."""
        return self.update(document, {"retry_count": document.retry_count + 1})

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
