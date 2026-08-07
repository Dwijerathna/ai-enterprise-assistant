"""LLM provider abstractions."""

from abc import ABC, abstractmethod


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider is unavailable or fails."""


class LLMProvider(ABC):
    """Provider-agnostic text generation interface."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a model response from a prompt."""
