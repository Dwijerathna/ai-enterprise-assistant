"""Document ingestion business logic."""

from pathlib import Path

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.Document import Document
from app.utils.chunking import create_chunks_from_pages
from app.utils.file_parser import extract_document_pages
from app.utils.sanitizer import clean_text as sanitize_text
from app.utils.storage import InvalidStoragePathError, resolve_storage_path

logger = get_logger(__name__)


class IngestionService:
    """Orchestrates document text extraction, cleaning, and chunk preparation."""

    def process_document(self, document: Document) -> list[dict]:
        """Run the full ingestion pipeline for a document record."""
        pages = self.extract_pages(document.storage_path)
        cleaned_pages = self.clean_pages(pages)
        chunks = self.create_chunks(cleaned_pages)
        return self.prepare_chunk_records(document, chunks)

    def extract_pages(self, storage_path: str) -> list[dict]:
        """Extract page-aware sections from a validated storage path."""
        absolute_path = self._resolve_document_path(storage_path)
        self._validate_file_exists(absolute_path)
        return extract_document_pages(str(absolute_path))

    def extract_text(self, storage_path: str) -> str:
        """Extract raw text from a validated server-controlled storage path."""
        pages = self.extract_pages(storage_path)
        return "\n\n".join(str(page.get("text", "")) for page in pages if page.get("text"))

    def clean_text(self, text: str) -> str:
        """Clean extracted text before chunking."""
        return sanitize_text(text)

    def clean_pages(self, pages: list[dict]) -> list[dict]:
        """Clean text for each extracted page section."""
        return [
            {
                **page,
                "text": self.clean_text(str(page.get("text", ""))),
            }
            for page in pages
        ]

    def create_chunks(
        self,
        pages: list[dict],
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[dict]:
        """Split cleaned page sections into semantic-friendly chunks."""
        return create_chunks_from_pages(pages, chunk_size=chunk_size, overlap=overlap)

    def prepare_chunk_records(
        self,
        document: Document,
        chunks: list[dict],
    ) -> list[dict]:
        """Attach tenant and embedding metadata to prepared chunks."""
        embedding_model = get_settings().embedding_model
        prepared_chunks: list[dict] = []

        for chunk in chunks:
            prepared_chunks.append(
                {
                    "document_id": document.id,
                    "organization_id": document.organization_id,
                    "content": chunk["content"],
                    "chunk_index": chunk["chunk_index"],
                    "page_number": chunk.get("page_number"),
                    "section_title": chunk.get("section_title"),
                    "token_count": chunk.get("token_count", 0),
                    "embedding_model": embedding_model,
                }
            )

        logger.info(
            "Prepared %d chunks for document_id=%s",
            len(prepared_chunks),
            document.id,
        )
        return prepared_chunks

    def _resolve_document_path(self, storage_path: str) -> Path:
        try:
            return resolve_storage_path(storage_path)
        except InvalidStoragePathError as exc:
            raise FileNotFoundError(str(exc)) from exc

    def _validate_file_exists(self, absolute_path: Path) -> None:
        if not absolute_path.exists() or not absolute_path.is_file():
            raise FileNotFoundError(f"Document file not found: {absolute_path}")
