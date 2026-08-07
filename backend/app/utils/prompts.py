"""Prompt construction utilities for RAG chat."""

import uuid
from dataclasses import dataclass

from app.models.Message import Message, MessageProcessingStatus, MessageRole
from app.schemas.retrieval import RetrievedChunkResponse

RAG_SYSTEM_INSTRUCTIONS = """You are an enterprise AI assistant. Answer the user's question using ONLY the provided context documents.

Rules:
- Use only facts explicitly stated in the context.
- If the context does not contain enough information, clearly state that the provided documents do not contain enough information to answer.
- Do not invent, assume, or supplement with outside knowledge.
- When referencing specific information, mention the source document name.
- Be concise, accurate, and professional.
- Use recent conversation history only to understand follow-up questions — do not treat it as authoritative document context."""

NO_CONTEXT_NOTICE = (
    "No relevant document context was retrieved. "
    "Tell the user you do not have relevant document context to answer their question."
)

DEFAULT_MAX_HISTORY_MESSAGES = 10
DEFAULT_MAX_HISTORY_CHARACTERS = 4000


@dataclass(frozen=True)
class ChatHistoryEntry:
    role: MessageRole
    content: str


def select_conversation_history(
    messages: list[Message],
    *,
    exclude_message_id: uuid.UUID | None = None,
    max_messages: int = DEFAULT_MAX_HISTORY_MESSAGES,
    max_characters: int = DEFAULT_MAX_HISTORY_CHARACTERS,
) -> list[ChatHistoryEntry]:
    """
    Select recent completed conversation messages for prompt context.

    Limits by message count first, then trims oldest entries to stay within
    the character budget.
    """
    eligible = [
        message
        for message in sorted(messages, key=lambda item: item.created_at)
        if (exclude_message_id is None or message.id != exclude_message_id)
        and message.processing_status == MessageProcessingStatus.COMPLETED
        and message.content.strip()
    ]
    recent = eligible[-max_messages:]

    while recent:
        total_chars = sum(len(message.content) for message in recent)
        if total_chars <= max_characters:
            break
        recent = recent[1:]

    return [
        ChatHistoryEntry(role=message.role, content=message.content.strip())
        for message in recent
    ]


def format_history_entry(entry: ChatHistoryEntry) -> str:
    """Format a single conversation history entry."""
    role_label = entry.role.value.capitalize()
    return f"{role_label}: {entry.content}"


def format_conversation_history(history: list[ChatHistoryEntry]) -> str:
    """Format conversation history for inclusion in the prompt."""
    if not history:
        return "No prior conversation history."
    return "\n".join(format_history_entry(entry) for entry in history)


def format_context_block(chunk: RetrievedChunkResponse, index: int) -> str:
    """Format a single retrieved chunk for inclusion in the prompt."""
    header_parts = [f"[Source {index}: {chunk.document_name or 'Unknown document'}"]
    if chunk.page_number is not None:
        header_parts.append(f"page {chunk.page_number}")
    if chunk.section_title:
        header_parts.append(f"section '{chunk.section_title}'")
    header = ", ".join(header_parts) + "]"
    return f"{header}\n{chunk.content.strip()}"


def build_rag_prompt(
    *,
    context_chunks: list[RetrievedChunkResponse],
    user_question: str,
    conversation_history: list[ChatHistoryEntry] | None = None,
) -> str:
    """
    Build a RAG prompt with system instructions, history, retrieved context,
    and the user question.
    """
    question = user_question.strip()
    if not question:
        raise ValueError("User question cannot be empty")

    history_section = format_conversation_history(conversation_history or [])

    if context_chunks:
        context_body = "\n\n".join(
            format_context_block(chunk, index)
            for index, chunk in enumerate(context_chunks, start=1)
        )
        context_section = f"Context documents:\n\n{context_body}"
    else:
        context_section = f"Context documents:\n\n{NO_CONTEXT_NOTICE}"

    return (
        f"{RAG_SYSTEM_INSTRUCTIONS}\n\n"
        f"Recent conversation:\n{history_section}\n\n"
        f"{context_section}\n\n"
        f"User question:\n{question}\n\n"
        "Assistant answer:"
    )
