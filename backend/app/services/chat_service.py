"""Chat orchestration business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.integrations.llm import LLMProvider, LLMProviderError
from app.integrations.llm_factory import get_llm_provider
from app.models.Message import Message, MessageProcessingStatus, MessageRole
from app.models.MessageChunkReference import MessageChunkReference
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_chunk_reference_repository import MessageChunkReferenceRepository
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, MessageResponse
from app.schemas.retrieval import SearchRequest
from app.services.retrieval_service import RetrievalService
from app.utils.prompts import build_rag_prompt, select_conversation_history

logger = get_logger(__name__)

ASSISTANT_FAILURE_MESSAGE = (
    "Unable to generate a response. The AI service is currently unavailable. "
    "Please try again."
)


class ChatService:
    """Orchestrates RAG retrieval and LLM response generation for conversations."""

    def __init__(
        self,
        db: Session,
        retrieval_service: RetrievalService | None = None,
        llm_client: LLMProvider | None = None,
    ) -> None:
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.citation_repo = MessageChunkReferenceRepository(db)
        self.retrieval_service = retrieval_service or RetrievalService(db)
        self.llm_client = llm_client or get_llm_provider()

    def send_message(
        self,
        conversation_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        request: ChatMessageRequest,
        department_id: uuid.UUID | None = None,
    ) -> ChatMessageResponse:
        """
        Process a user message: retrieve context, generate a response, and persist messages.

        Conversation access is scoped to organization_id and user ownership.
        """
        conversation = self.conversation_repo.get_conversation_with_messages(
            conversation_id=conversation_id,
            organization_id=organization_id,
        )
        if conversation is None or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        conversation_history = select_conversation_history(conversation.messages)

        user_message = Message(
            conversation_id=conversation.id,
            organization_id=organization_id,
            role=MessageRole.USER,
            content=request.content,
            processing_status=MessageProcessingStatus.COMPLETED,
        )
        saved_user_message = self.conversation_repo.add_message(user_message)

        search_response = self.retrieval_service.search(
            organization_id=organization_id,
            request=SearchRequest(
                query=request.content,
                limit=request.retrieval_limit,
            ),
            department_id=department_id,
        )

        prompt = build_rag_prompt(
            context_chunks=search_response.results,
            user_question=request.content,
            conversation_history=conversation_history,
        )

        try:
            assistant_content = self.llm_client.generate_response(prompt)
        except LLMProviderError as exc:
            logger.warning(
                "LLM provider unavailable for conversation_id=%s organization_id=%s",
                conversation_id,
                organization_id,
            )
            failed_assistant_message = Message(
                conversation_id=conversation.id,
                organization_id=organization_id,
                role=MessageRole.ASSISTANT,
                content=ASSISTANT_FAILURE_MESSAGE,
                processing_status=MessageProcessingStatus.FAILED,
                error_message=str(exc),
                model_name=getattr(self.llm_client, "model", None),
            )
            self.conversation_repo.add_message(failed_assistant_message)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI generation service is currently unavailable",
            ) from exc

        assistant_message = Message(
            conversation_id=conversation.id,
            organization_id=organization_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            processing_status=MessageProcessingStatus.COMPLETED,
            model_name=getattr(self.llm_client, "model", None),
        )
        saved_assistant_message = self.conversation_repo.add_message(assistant_message)

        if search_response.results:
            citations = [
                MessageChunkReference(
                    message_id=saved_assistant_message.id,
                    chunk_id=chunk.chunk_id,
                    similarity_score=chunk.similarity_score,
                )
                for chunk in search_response.results
            ]
            self.citation_repo.create_references(citations)

        return ChatMessageResponse(
            user_message=MessageResponse.model_validate(saved_user_message),
            assistant_message=MessageResponse.model_validate(saved_assistant_message),
            sources=search_response.results,
            retrieval_status=search_response.status,
            retrieval_message=search_response.message,
        )
