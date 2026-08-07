"""Mock embedding provider for development without Ollama."""

import hashlib
import math
import struct

from app.core.config import Settings, get_settings
from app.integrations.embeddings import EmbeddingProvider, EmbeddingProviderError


class MockEmbeddingProvider(EmbeddingProvider):
    """Generates deterministic hash-based vectors for local RAG testing."""

    embedding_model = "mock-embedding"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.vector_size = self.settings.embedding_vector_size

    def generate_embedding(self, text: str) -> list[float]:
        if not text.strip():
            raise EmbeddingProviderError("Cannot generate embedding for empty text")
        return self._hash_vector(text.strip())

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        normalized = [text.strip() for text in texts if text.strip()]
        if not normalized:
            raise EmbeddingProviderError("Cannot generate embeddings for empty text list")
        return [self._hash_vector(text) for text in normalized]

    def _hash_vector(self, text: str) -> list[float]:
        """Build a deterministic, L2-normalized vector from text."""
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []

        for index in range(self.vector_size):
            block = hashlib.sha256(seed + index.to_bytes(4, "big")).digest()
            raw = struct.unpack(">I", block[:4])[0]
            values.append((raw / 4294967295.0) * 2.0 - 1.0)

        norm = math.sqrt(sum(value * value for value in values))
        if norm == 0:
            return values
        return [value / norm for value in values]
