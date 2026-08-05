"""Qdrant vector database integration."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

REQUIRED_PAYLOAD_FIELDS = (
    "organization_id",
    "document_id",
    "chunk_id",
    "embedding_model",
    "created_at",
)


class QdrantServiceError(RuntimeError):
    """Raised when Qdrant operations fail or metadata is invalid."""


class QdrantService:
    """
    Wrapper around Qdrant vector operations with tenant-aware metadata.
    """

    def __init__(
        self,
        collection_name: str,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.collection_name = collection_name
        self._client: Any | None = None
        self._available = False
        self._initialize_client()

    @property
    def is_available(self) -> bool:
        return self._available

    def _initialize_client(self) -> None:
        try:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
            )
            self._client.get_collections()
            self._available = True
            logger.info(
                "Connected to Qdrant at %s:%s",
                self.settings.qdrant_host,
                self.settings.qdrant_port,
            )
        except Exception:
            logger.warning(
                "Qdrant unavailable at %s:%s — operating in offline mode",
                self.settings.qdrant_host,
                self.settings.qdrant_port,
            )
            self._client = None
            self._available = False

    @staticmethod
    def build_vector_payload(
        *,
        organization_id: UUID,
        document_id: UUID,
        chunk_id: UUID,
        embedding_model: str,
        document_name: str,
        page_number: int | None = None,
        section_title: str | None = None,
        department_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Build a standardized Qdrant payload for a document chunk vector."""
        payload: dict[str, Any] = {
            "organization_id": str(organization_id),
            "document_id": str(document_id),
            "chunk_id": str(chunk_id),
            "page_number": page_number,
            "section_title": section_title,
            "document_name": document_name,
            "embedding_model": embedding_model,
            "created_at": (created_at or datetime.now(UTC)).isoformat(),
        }
        if department_id is not None:
            payload["department_id"] = str(department_id)
        return payload

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        missing = [field for field in REQUIRED_PAYLOAD_FIELDS if not payload.get(field)]
        if missing:
            raise QdrantServiceError(f"Vector payload missing required fields: {missing}")
        if not payload.get("document_name"):
            raise QdrantServiceError("Vector payload missing document_name")

    def create_collection(self, vector_size: int = 768) -> bool:
        """Create a collection if it does not already exist."""
        if not self._available or self._client is None:
            logger.info("Offline mode: create_collection(%s)", self.collection_name)
            return True

        from qdrant_client.http import models as qmodels

        if self._client.collection_exists(self.collection_name):
            return True

        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )
        return True

    def upsert_vectors(
        self,
        organization_id: UUID,
        points: list[dict[str, Any]],
    ) -> None:
        """Insert or update vector points in the collection."""
        expected_org = str(organization_id)
        for point in points:
            payload = point.get("payload", {})
            self._validate_payload(payload)
            if payload.get("organization_id") != expected_org:
                raise QdrantServiceError(
                    "Vector payload organization_id does not match upsert context"
                )

        if not self._available or self._client is None:
            logger.info(
                "Offline mode: upsert_vectors collection=%s count=%d",
                self.collection_name,
                len(points),
            )
            return

        from qdrant_client.http import models as qmodels

        qdrant_points = [
            qmodels.PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point["payload"],
            )
            for point in points
        ]
        self._client.upsert(collection_name=self.collection_name, points=qdrant_points)

    def search_vectors(
        self,
        query_vector: list[float],
        organization_id: UUID,
        *,
        limit: int = 5,
        department_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors scoped to an organization.

        organization_id is mandatory for tenant isolation.
        """
        if organization_id is None:
            raise QdrantServiceError("organization_id is required for vector search")

        if not self._available or self._client is None:
            logger.info(
                "Offline mode: search_vectors collection=%s org=%s",
                self.collection_name,
                organization_id,
            )
            return []

        from qdrant_client.http import models as qmodels

        must_conditions = [
            qmodels.FieldCondition(
                key="organization_id",
                match=qmodels.MatchValue(value=str(organization_id)),
            )
        ]
        if department_id is not None:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="department_id",
                    match=qmodels.MatchValue(value=str(department_id)),
                )
            )

        results = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qmodels.Filter(must=must_conditions),
        )
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "payload": result.payload or {},
            }
            for result in results
        ]

    def delete_vectors(self, document_id: UUID, organization_id: UUID) -> None:
        """Delete all vectors associated with a document within an organization."""
        if organization_id is None:
            raise QdrantServiceError("organization_id is required for vector deletion")

        if not self._available or self._client is None:
            logger.info(
                "Offline mode: delete_vectors collection=%s document=%s org=%s",
                self.collection_name,
                document_id,
                organization_id,
            )
            return

        from qdrant_client.http import models as qmodels

        self._client.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=str(document_id)),
                        ),
                        qmodels.FieldCondition(
                            key="organization_id",
                            match=qmodels.MatchValue(value=str(organization_id)),
                        ),
                    ]
                )
            ),
        )
