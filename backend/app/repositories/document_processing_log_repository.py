"""Document processing log data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.DocumentProcessingLog import DocumentProcessingLog, ProcessingLogStatus
from app.repositories.base import BaseRepository


class DocumentProcessingLogRepository(BaseRepository[DocumentProcessingLog]):
    """Repository for ingestion stage logs."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, DocumentProcessingLog)

    def create_log(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        stage: str,
        status: ProcessingLogStatus,
        error_message: str | None = None,
    ) -> DocumentProcessingLog:
        log = DocumentProcessingLog(
            document_id=document_id,
            organization_id=organization_id,
            stage=stage,
            status=status,
            error_message=error_message,
        )
        return self.create(log)

    def get_logs_for_document(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[DocumentProcessingLog]:
        stmt = (
            select(DocumentProcessingLog)
            .where(
                DocumentProcessingLog.document_id == document_id,
                DocumentProcessingLog.organization_id == organization_id,
            )
            .order_by(DocumentProcessingLog.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())
