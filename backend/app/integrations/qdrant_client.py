"""Qdrant vector database integration."""

from typing import Any
from uuid import UUID

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class QdrantService:
    """
    Wrapper around Qdrant vector operations.

    Falls back to in-memory placeholder behavior when Qdrant is unavailable.
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

    def _initialize_client(self) -> None:
        try:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
            )
            self._client.get_collections()
            self._available = True
            logger.info("Connected to Qdrant at %s:%s", self.settings.qdrant_host, self.settings.qdrant_port)
        except Exception:
            logger.warning(
                "Qdrant unavailable at %s:%s — using placeholder mode",
                self.settings.qdrant_host,
                self.settings.qdrant_port,
            )
            self._client = None
            self._available = False

    def create_collection(self, vector_size: int = 384) -> bool:
        """Create a collection if it does not already exist."""
        if not self._available or self._client is None:
            logger.info("Placeholder: create_collection(%s)", self.collection_name)
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
        points: list[dict[str, Any]],
    ) -> None:
        """Insert or update vector points in the collection."""
        if not self._available or self._client is None:
            logger.info(
                "Placeholder: upsert_vectors collection=%s count=%d",
                self.collection_name,
                len(points),
            )
            return

        from qdrant_client.http import models as qmodels

        qdrant_points = [
            qmodels.PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point.get("payload", {}),
            )
            for point in points
        ]
        self._client.upsert(collection_name=self.collection_name, points=qdrant_points)

    def search_vectors(
        self,
        query_vector: list[float],
        organization_id: UUID,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors scoped to an organization."""
        if not self._available or self._client is None:
            logger.info(
                "Placeholder: search_vectors collection=%s org=%s",
                self.collection_name,
                organization_id,
            )
            return []

        from qdrant_client.http import models as qmodels

        results = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="organization_id",
                        match=qmodels.MatchValue(value=str(organization_id)),
                    )
                ]
            ),
        )
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "payload": result.payload or {},
            }
            for result in results
        ]

    def delete_vectors(self, document_id: UUID) -> None:
        """Delete all vectors associated with a document."""
        if not self._available or self._client is None:
            logger.info(
                "Placeholder: delete_vectors collection=%s document=%s",
                self.collection_name,
                document_id,
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
                        )
                    ]
                )
            ),
        )
