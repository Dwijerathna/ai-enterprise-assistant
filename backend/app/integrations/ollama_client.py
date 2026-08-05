"""Ollama LLM integration."""

from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

PLACEHOLDER_RESPONSE = (
    "Ollama is unavailable. This is a placeholder response for development."
)


class OllamaClient:
    """HTTP client wrapper for Ollama generation requests."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self.model = self.settings.llm_model
        self.timeout = httpx.Timeout(30.0)

    def generate_response(self, prompt: str) -> str:
        """
        Generate a model response from Ollama.

        Returns a placeholder response when Ollama is unavailable.
        """
        payload = {
            "model": self.model,
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

    def is_available(self) -> bool:
        """Check whether the Ollama server responds to health requests."""
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get("/api/tags")
                return response.status_code == 200
        except Exception:
            return False
