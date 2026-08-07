"""Mock LLM provider for development without Ollama."""

from app.integrations.llm import LLMProvider


class MockLLMProvider(LLMProvider):
    """Returns a deterministic simulated response for RAG pipeline testing."""

    model = "mock-llm"

    def generate_response(self, prompt: str) -> str:
        if not prompt.strip():
            return (
                "This is a simulated AI response. No prompt content was provided."
            )
        return (
            "This is a simulated AI response.\n\n"
            "The RAG pipeline successfully:\n"
            "- received the question\n"
            "- retrieved context\n"
            "- generated a response"
        )
