"""Document API endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.User import User
from app.schemas.document import DocumentCreate, DocumentListResponse, DocumentResponse
from app.security.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.tasks.document_tasks import process_document_task

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    data: DocumentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Create a document record and queue background processing.

    Accepts filename only — storage_path is generated server-side.
    """
    document = document_service.create_document(data, current_user)
    background_tasks.add_task(
        process_document_task,
        str(document.id),
        str(current_user.organization_id),
    )
    return document


@router.get("", response_model=DocumentListResponse)
def list_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    """Return documents accessible to the authenticated user."""
    documents = document_service.get_user_documents(current_user)
    return DocumentListResponse(documents=documents, total=len(documents))
