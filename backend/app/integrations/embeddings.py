"""Embedding provider abstractions."""

from abc import ABC, abstractmethod


class EmbeddingProviderError(RuntimeError):
    """Raised when an embedding provider is unavailable or fails."""


class EmbeddingProvider(ABC):
    """Provider-agnostic embedding interface."""

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text input."""

    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple text inputs."""
