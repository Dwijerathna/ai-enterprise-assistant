"""Background embedding generation tasks."""

from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

PLACEHOLDER_VECTOR = [0.123, 0.456]


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for a text chunk.

    Returns a placeholder vector until an external embedding model is connected.
    """
    if not text.strip():
        return PLACEHOLDER_VECTOR.copy()

    logger.debug("Placeholder embedding generated for text length=%d", len(text))
    return PLACEHOLDER_VECTOR.copy()


def generate_embeddings_task(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Prepare embedding payloads for a list of document chunks.

    Does not persist vectors yet — preparation only for the future RAG pipeline.
    """
    prepared: list[dict[str, Any]] = []

    for chunk in chunks:
        content = str(chunk.get("content", ""))
        vector = generate_embedding(content)
        prepared.append(
            {
                "chunk_id": chunk.get("id"),
                "document_id": chunk.get("document_id"),
                "organization_id": chunk.get("organization_id"),
                "chunk_index": chunk.get("chunk_index"),
                "vector": vector,
            }
        )

    logger.info("Prepared embeddings for %d chunks", len(prepared))
    return prepared
