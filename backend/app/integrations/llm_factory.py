"""LLM provider factory."""

from app.core.config import Settings, get_settings
from app.integrations.llm import LLMProvider
from app.integrations.mock_llm import MockLLMProvider
from app.integrations.ollama_client import OllamaClient

SUPPORTED_LLM_PROVIDERS = frozenset({"mock", "ollama"})


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    """Return the configured LLM provider implementation."""
    resolved_settings = settings or get_settings()
    provider_name = resolved_settings.llm_provider.lower().strip()

    if provider_name == "mock":
        return MockLLMProvider()
    if provider_name == "ollama":
        return OllamaClient(resolved_settings)

    supported = ", ".join(sorted(SUPPORTED_LLM_PROVIDERS))
    raise ValueError(
        f"Unsupported LLM provider '{resolved_settings.llm_provider}'. "
        f"Supported values: {supported}"
    )
