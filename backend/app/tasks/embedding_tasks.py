"""Background embedding generation tasks."""

from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_embeddings_task(document_id: str, collection_name: str) -> None:
    """
    Placeholder for embedding generation and Qdrant storage.

    Future flow:
    Chunk Document → Generate Embeddings → Store in Qdrant
    """
    logger.info(
        "Placeholder: generate_embeddings_task document_id=%s collection=%s",
        document_id,
        collection_name,
    )
    # TODO: Integrate Ollama embedding model and VectorRepository
    logger.info(
        "Placeholder: generate_embeddings_task completed document_id=%s",
        document_id,
    )
