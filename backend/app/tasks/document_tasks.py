"""Background document processing tasks."""

from app.core.logging import get_logger

logger = get_logger(__name__)


def process_document_task(document_id: str) -> None:
    """
    Placeholder for the async document ingestion pipeline.

    Future flow:
    Upload Document → Extract Text → Chunk → Generate Embeddings → Store in Qdrant
    """
    logger.info("Placeholder: process_document_task started for document_id=%s", document_id)
    # TODO: Wire up text extraction, chunking, and embedding pipeline
    logger.info("Placeholder: process_document_task completed for document_id=%s", document_id)
