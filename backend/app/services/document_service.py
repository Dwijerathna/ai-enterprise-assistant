"""Document business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.Document import Document, DocumentStatus
from app.models.User import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentResponse
from app.utils.storage import (
    InvalidStoragePathError,
    build_storage_path,
    ensure_organization_upload_dir,
)


class DocumentService:
    """Handles document creation and organization-scoped queries."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.document_repo = DocumentRepository(db)

    def create_document(
        self,
        data: DocumentCreate,
        current_user: User,
    ) -> DocumentResponse:
        """Create a document record with a server-controlled storage path."""
        try:
            ensure_organization_upload_dir(current_user.organization_id)
            storage_path = build_storage_path(
                organization_id=current_user.organization_id,
                filename=data.filename,
            )
        except InvalidStoragePathError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        document = Document(
            organization_id=current_user.organization_id,
            uploaded_by=current_user.id,
            filename=data.filename,
            storage_path=storage_path,
            status=DocumentStatus.PENDING,
        )
        created = self.document_repo.create_document(document)
        return DocumentResponse.model_validate(created)

    def get_user_documents(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentResponse]:
        """Return documents uploaded by the current user."""
        documents = self.document_repo.get_user_documents(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            skip=skip,
            limit=limit,
        )
        return [DocumentResponse.model_validate(doc) for doc in documents]

    def get_org_documents(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentResponse]:
        """Return all documents in an organization."""
        documents = self.document_repo.get_org_documents(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
        )
        return [DocumentResponse.model_validate(doc) for doc in documents]

    def get_document(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Document:
        """Return a document scoped to an organization or raise 404."""
        document = self.document_repo.get_by_id(document_id)
        if document is None or document.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document
