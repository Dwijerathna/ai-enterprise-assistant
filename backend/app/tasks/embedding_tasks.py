"""Background embedding generation tasks."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.logging import get_logger
from app.integrations.embeddings import EmbeddingProviderError
from app.integrations.ollama_client import OllamaClient
from app.integrations.qdrant_client import QdrantService

logger = get_logger(__name__)


def _get_embedding_provider() -> OllamaClient:
    return OllamaClient()


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector using the configured provider."""
    return _get_embedding_provider().generate_embedding(text)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for multiple texts."""
    return _get_embedding_provider().generate_embeddings(texts)


def generate_embeddings_task(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Generate embeddings and prepare Qdrant upsert payloads for document chunks.
    """
    if not chunks:
        return []

    provider = _get_embedding_provider()
    texts = [str(chunk.get("content", "")) for chunk in chunks]

    try:
        vectors = provider.generate_embeddings(texts)
    except EmbeddingProviderError:
        logger.warning("Embedding provider unavailable — skipping vector persistence")
        return []

    prepared: list[dict[str, Any]] = []
    organization_id = chunks[0].get("organization_id")
    collection_name = chunks[0].get("collection_name")
    department_id = chunks[0].get("department_id")

    if not organization_id or not collection_name:
        logger.warning("Missing organization or collection metadata for embedding task")
        return []

    qdrant = QdrantService(collection_name=str(collection_name))
    if vectors:
        qdrant.create_collection(vector_size=len(vectors[0]))

    qdrant_points: list[dict[str, Any]] = []

    for chunk, vector in zip(chunks, vectors, strict=False):
        chunk_id = chunk.get("id")
        document_id = chunk.get("document_id")
        if chunk_id is None or document_id is None:
            continue

        payload = QdrantService.build_vector_payload(
            organization_id=UUID(str(organization_id)),
            department_id=UUID(str(department_id)) if department_id else None,
            document_id=UUID(str(document_id)),
            chunk_id=UUID(str(chunk_id)),
            page_number=chunk.get("page_number"),
            section_title=chunk.get("section_title"),
            document_name=str(chunk.get("document_name", "unknown")),
            embedding_model=str(chunk.get("embedding_model", provider.embedding_model)),
            created_at=datetime.now(UTC),
        )
        point = {
            "id": str(chunk_id),
            "vector": vector,
            "payload": payload,
        }
        qdrant_points.append(point)
        prepared.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "organization_id": organization_id,
                "vector": vector,
                "payload": payload,
            }
        )

    if qdrant_points:
        qdrant.upsert_vectors(UUID(str(organization_id)), qdrant_points)

    logger.info("Prepared embeddings for %d chunks", len(prepared))
    return prepared
