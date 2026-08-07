"""Embedding provider factory."""

from app.core.config import Settings, get_settings
from app.integrations.embeddings import EmbeddingProvider
from app.integrations.mock_embedding import MockEmbeddingProvider
from app.integrations.ollama_client import OllamaClient

SUPPORTED_EMBEDDING_PROVIDERS = frozenset({"mock", "ollama"})


def get_embedding_provider(settings: Settings | None = None) -> EmbeddingProvider:
    """Return the configured embedding provider implementation."""
    resolved_settings = settings or get_settings()
    provider_name = resolved_settings.embedding_provider.lower().strip()

    if provider_name == "mock":
        return MockEmbeddingProvider(resolved_settings)
    if provider_name == "ollama":
        return OllamaClient(resolved_settings)

    supported = ", ".join(sorted(SUPPORTED_EMBEDDING_PROVIDERS))
    raise ValueError(
        f"Unsupported embedding provider '{resolved_settings.embedding_provider}'. "
        f"Supported values: {supported}"
    )
