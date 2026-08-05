"""Ollama integration for generation and embeddings."""

from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.integrations.embeddings import EmbeddingProvider, EmbeddingProviderError

logger = get_logger(__name__)

PLACEHOLDER_RESPONSE = (
    "Ollama is unavailable. This is a placeholder response for development."
)


class OllamaClient(EmbeddingProvider):
    """HTTP client wrapper for Ollama generation and embedding requests."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self.llm_model = self.settings.llm_model
        self.embedding_model = self.settings.embedding_model
        self.timeout = httpx.Timeout(30.0)

    def generate_response(self, prompt: str) -> str:
        """
        Generate a model response from Ollama.

        Returns a placeholder response when Ollama is unavailable.
        """
        payload = {
            "model": self.llm_model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post("/api/generate", json=payload)
                response.raise_for_status()
                data: dict[str, Any] = response.json()
                return str(data.get("response", "")).strip() or PLACEHOLDER_RESPONSE
        except Exception:
            logger.warning(
                "Ollama unavailable at %s — returning placeholder response",
                self.base_url,
            )
            return PLACEHOLDER_RESPONSE

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text input."""
        if not text.strip():
            raise EmbeddingProviderError("Cannot generate embedding for empty text")
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple text inputs."""
        normalized = [text.strip() for text in texts if text.strip()]
        if not normalized:
            raise EmbeddingProviderError("Cannot generate embeddings for empty text list")

        payload = {
            "model": self.embedding_model,
            "input": normalized if len(normalized) > 1 else normalized[0],
        }

        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post("/api/embed", json=payload)
                response.raise_for_status()
                data: dict[str, Any] = response.json()
                embeddings = data.get("embeddings")
                if embeddings is None and "embedding" in data:
                    embeddings = [data["embedding"]]
                if not embeddings:
                    raise EmbeddingProviderError("Ollama returned no embedding vectors")
                return [list(map(float, vector)) for vector in embeddings]
        except EmbeddingProviderError:
            raise
        except Exception as exc:
            logger.warning("Ollama embedding request failed at %s", self.base_url)
            raise EmbeddingProviderError(
                f"Embedding provider unavailable: {self.base_url}"
            ) from exc

    def is_available(self) -> bool:
        """Check whether the Ollama server responds to health requests."""
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get("/api/tags")
                return response.status_code == 200
        except Exception:
            return False
