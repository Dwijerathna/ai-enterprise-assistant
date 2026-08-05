"""Background document processing tasks."""

import uuid

from app.core.logging import get_logger
from app.db.session import create_session_factory
from app.models.Document import DocumentStatus
from app.models.DocumentChunk import DocumentChunk
from app.models.DocumentProcessingLog import ProcessingLogStatus
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_processing_log_repository import DocumentProcessingLogRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.ingestion_service import IngestionService
from app.tasks.embedding_tasks import generate_embeddings_task

logger = get_logger(__name__)

MAX_RETRY_COUNT = 3


def process_document_task(document_id: str, organization_id: str) -> None:
    """
    Background ingestion pipeline for an uploaded document.

    Always scopes document lookup by organization_id for tenant isolation.
    """
    db = create_session_factory()()
    document_repo = DocumentRepository(db)
    chunk_repo = DocumentChunkRepository(db)
    log_repo = DocumentProcessingLogRepository(db)
    org_repo = OrganizationRepository(db)
    ingestion_service = IngestionService()

    doc_uuid = uuid.UUID(document_id)
    org_uuid = uuid.UUID(organization_id)
    current_stage = DocumentStatus.PENDING.value

    try:
        document = document_repo.get_by_id_and_organization(doc_uuid, org_uuid)
        if document is None:
            logger.error(
                "Document not found for background task: document_id=%s organization_id=%s",
                document_id,
                organization_id,
            )
            return

        try:
            current_stage = DocumentStatus.EXTRACTING.value
            document_repo.update_status(document, DocumentStatus.EXTRACTING)
            pages = ingestion_service.extract_pages(document.storage_path)
            cleaned_pages = ingestion_service.clean_pages(pages)
            log_repo.create_log(
                document.id,
                document.organization_id,
                stage=current_stage,
                status=ProcessingLogStatus.SUCCESS,
            )

            current_stage = DocumentStatus.CHUNKING.value
            document_repo.update_status(document, DocumentStatus.CHUNKING)
            chunks = ingestion_service.create_chunks(cleaned_pages)
            prepared_chunks = ingestion_service.prepare_chunk_records(document, chunks)
            log_repo.create_log(
                document.id,
                document.organization_id,
                stage=current_stage,
                status=ProcessingLogStatus.SUCCESS,
            )

            chunk_models = [
                DocumentChunk(
                    document_id=document.id,
                    organization_id=document.organization_id,
                    chunk_index=int(chunk["chunk_index"]),
                    content=str(chunk["content"]),
                    page_number=chunk.get("page_number"),
                    section_title=chunk.get("section_title"),
                    token_count=int(chunk.get("token_count", 0)),
                    embedding_model=chunk.get("embedding_model"),
                )
                for chunk in prepared_chunks
            ]
            saved_chunks = chunk_repo.create_chunks(chunk_models)
            organization = org_repo.get_by_id(document.organization_id)

            current_stage = DocumentStatus.EMBEDDING.value
            document_repo.update_status(document, DocumentStatus.EMBEDDING)
            chunk_payloads = [
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "organization_id": chunk.organization_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "document_name": document.filename,
                    "embedding_model": chunk.embedding_model,
                    "collection_name": organization.qdrant_collection_name if organization else None,
                    "department_id": None,
                }
                for chunk in saved_chunks
            ]
            embedding_results = generate_embeddings_task(chunk_payloads)
            if saved_chunks and not embedding_results:
                error_message = "Embedding provider unavailable"
                logger.warning(
                    "Embedding failed for document %s: %s",
                    document_id,
                    error_message,
                )
                document = document_repo.increment_retry_count(document)
                log_repo.create_log(
                    document.id,
                    document.organization_id,
                    stage=DocumentStatus.EMBEDDING.value,
                    status=ProcessingLogStatus.FAILED,
                    error_message=error_message,
                )
                if document.retry_count >= MAX_RETRY_COUNT:
                    document_repo.update_status(document, DocumentStatus.FAILED)
                else:
                    document_repo.update_status(document, DocumentStatus.PENDING)
                return

            log_repo.create_log(
                document.id,
                document.organization_id,
                stage=current_stage,
                status=ProcessingLogStatus.SUCCESS,
            )

            current_stage = DocumentStatus.INDEXING.value
            document_repo.update_status(document, DocumentStatus.INDEXING)
            log_repo.create_log(
                document.id,
                document.organization_id,
                stage=current_stage,
                status=ProcessingLogStatus.SUCCESS,
            )

            current_stage = DocumentStatus.COMPLETED.value
            document_repo.update_status(document, DocumentStatus.COMPLETED)
            log_repo.create_log(
                document.id,
                document.organization_id,
                stage=current_stage,
                status=ProcessingLogStatus.SUCCESS,
            )
            logger.info("Document processing completed: %s", document_id)
        except Exception as exc:
            logger.exception("Document processing failed: %s", document_id)
            document = document_repo.increment_retry_count(document)
            log_repo.create_log(
                document.id,
                document.organization_id,
                stage=current_stage,
                status=ProcessingLogStatus.FAILED,
                error_message=str(exc),
            )
            if document.retry_count >= MAX_RETRY_COUNT:
                document_repo.update_status(document, DocumentStatus.FAILED)
            else:
                document_repo.update_status(document, DocumentStatus.PENDING)
    finally:
        db.close()
