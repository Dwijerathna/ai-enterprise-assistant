"""Ollama integration for generation and embeddings."""

from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.integrations.embeddings import EmbeddingProvider, EmbeddingProviderError
from app.integrations.llm import LLMProvider, LLMProviderError

logger = get_logger(__name__)

DEFAULT_EMBEDDING_TIMEOUT_SECONDS = 30.0
DEFAULT_LLM_TIMEOUT_SECONDS = 120.0


class OllamaClient(EmbeddingProvider, LLMProvider):
    """HTTP client wrapper for Ollama generation and embedding requests."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self.llm_model = self.settings.llm_model
        self.embedding_model = self.settings.embedding_model
        self.embedding_timeout = httpx.Timeout(DEFAULT_EMBEDDING_TIMEOUT_SECONDS)
        self.llm_timeout = httpx.Timeout(DEFAULT_LLM_TIMEOUT_SECONDS)

    @property
    def model(self) -> str:
        """LLM model name used for generation and message metadata."""
        return self.llm_model

    def generate_response(self, prompt: str) -> str:
        """Generate a model response from Ollama using the configured LLM model."""
        if not prompt.strip():
            raise LLMProviderError("Cannot generate response for empty prompt")

        payload = {
            "model": self.llm_model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            with httpx.Client(base_url=self.base_url, timeout=self.llm_timeout) as client:
                response = client.post("/api/generate", json=payload)
                response.raise_for_status()
                data: dict[str, Any] = response.json()
                content = str(data.get("response", "")).strip()
                if not content:
                    raise LLMProviderError("Ollama returned an empty response")
                return content
        except LLMProviderError:
            raise
        except httpx.TimeoutException as exc:
            logger.warning(
                "Ollama LLM request timed out at %s (model=%s)",
                self.base_url,
                self.llm_model,
            )
            raise LLMProviderError(
                f"LLM request timed out: {self.base_url}"
            ) from exc
        except httpx.ConnectError as exc:
            logger.warning("Ollama LLM connection failed at %s", self.base_url)
            raise LLMProviderError(
                f"LLM provider unavailable: {self.base_url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Ollama LLM request failed at %s with status %s",
                self.base_url,
                exc.response.status_code,
            )
            raise LLMProviderError(
                f"LLM provider returned HTTP {exc.response.status_code}"
            ) from exc
        except Exception as exc:
            logger.warning("Ollama LLM request failed at %s", self.base_url)
            raise LLMProviderError(
                f"LLM provider unavailable: {self.base_url}"
            ) from exc

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
            with httpx.Client(base_url=self.base_url, timeout=self.embedding_timeout) as client:
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
            with httpx.Client(base_url=self.base_url, timeout=self.embedding_timeout) as client:
                response = client.get("/api/tags")
                return response.status_code == 200
        except Exception:
            return False
