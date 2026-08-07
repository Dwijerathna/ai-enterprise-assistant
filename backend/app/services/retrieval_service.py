"""Retrieval business logic for RAG search."""

import uuid

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.integrations.embedding_factory import get_embedding_provider
from app.integrations.embeddings import EmbeddingProvider, EmbeddingProviderError
from app.integrations.qdrant_client import QdrantService
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.retrieval import RetrievedChunkResponse, SearchRequest, SearchResponse

logger = get_logger(__name__)


class RetrievalService:
    """Orchestrates query embedding and tenant-scoped vector retrieval."""

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.db = db
        self.chunk_repo = DocumentChunkRepository(db)
        self.document_repo = DocumentRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.embedding_provider = embedding_provider or get_embedding_provider()

    def search(
        self,
        organization_id: uuid.UUID,
        request: SearchRequest,
        department_id: uuid.UUID | None = None,
    ) -> SearchResponse:
        """
        Retrieve ranked document chunks for a user query.

        Does not invoke an LLM — retrieval only.
        """
        organization = self.org_repo.get_by_id(organization_id)
        if organization is None:
            return SearchResponse(query=request.query, results=[], total=0)

        try:
            query_vector = self.embedding_provider.generate_embedding(request.query)
        except EmbeddingProviderError:
            logger.warning(
                "Embedding provider unavailable — returning degraded search response "
                "for organization_id=%s",
                organization_id,
            )
            return SearchResponse(
                query=request.query,
                results=[],
                total=0,
                status="degraded",
                message="Retrieval unavailable: embedding service is offline",
            )

        qdrant = QdrantService(collection_name=organization.qdrant_collection_name)

        vector_results = qdrant.search_vectors(
            query_vector=query_vector,
            organization_id=organization_id,
            limit=request.limit,
            department_id=department_id,
        )

        if not vector_results:
            return SearchResponse(query=request.query, results=[], total=0)

        chunk_ids: list[uuid.UUID] = []
        score_by_chunk: dict[uuid.UUID, float] = {}
        payload_by_chunk: dict[uuid.UUID, dict] = {}

        for result in vector_results:
            payload = result.get("payload", {})
            chunk_id_raw = payload.get("chunk_id") or result.get("id")
            if not chunk_id_raw:
                continue
            chunk_id = uuid.UUID(str(chunk_id_raw))
            chunk_ids.append(chunk_id)
            score_by_chunk[chunk_id] = float(result.get("score", 0.0))
            payload_by_chunk[chunk_id] = payload

        chunks = self.chunk_repo.get_chunks_by_ids(chunk_ids, organization_id)
        chunk_map = {chunk.id: chunk for chunk in chunks}

        ranked_results: list[RetrievedChunkResponse] = []
        for chunk_id in chunk_ids:
            chunk = chunk_map.get(chunk_id)
            if chunk is None:
                continue

            document = self.document_repo.get_by_id_and_organization(
                chunk.document_id,
                organization_id,
            )
            payload = payload_by_chunk.get(chunk_id, {})

            ranked_results.append(
                RetrievedChunkResponse(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    document_name=payload.get("document_name")
                    or (document.filename if document else None),
                    similarity_score=score_by_chunk.get(chunk_id, 0.0),
                    chunk_index=chunk.chunk_index,
                    embedding_model=chunk.embedding_model,
                )
            )

        return SearchResponse(
            query=request.query,
            results=ranked_results,
            total=len(ranked_results),
        )
