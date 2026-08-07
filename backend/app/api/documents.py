"""Document API endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
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


def _queue_document_processing(
    background_tasks: BackgroundTasks,
    document: DocumentResponse,
    organization_id: str,
) -> None:
    background_tasks.add_task(
        process_document_task,
        str(document.id),
        organization_id,
    )


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
    The file must already exist at the resolved storage path.
    """
    document = document_service.create_document(data, current_user)
    _queue_document_processing(
        background_tasks,
        document,
        str(current_user.organization_id),
    )
    return document


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document file",
    description=(
        "Upload a document using multipart/form-data. Supported file types: "
        ".pdf, .txt, .docx. The file is stored under uploads/{organization_id}/ "
        "and ingestion is queued automatically."
    ),
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file (.pdf, .txt, .docx)"),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Upload a document file and queue background ingestion."""
    content = await file.read()
    document = document_service.upload_document(
        filename=file.filename or "upload",
        content=content,
        current_user=current_user,
    )
    _queue_document_processing(
        background_tasks,
        document,
        str(current_user.organization_id),
    )
    return document


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Return a single document scoped to the authenticated user's organization."""
    return document_service.get_document_response(document_id, current_user)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    """Return documents accessible to the authenticated user."""
    documents = document_service.get_user_documents(current_user)
    return DocumentListResponse(documents=documents, total=len(documents))
