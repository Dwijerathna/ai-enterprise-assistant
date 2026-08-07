"""Server-controlled document storage utilities."""

import re
import uuid
from pathlib import Path

from app.core.config import get_settings

# backend/ directory (parent of app/)
BACKEND_ROOT = Path(__file__).resolve().parents[2]

UNSAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._\- ]+")

ALLOWED_DOCUMENT_EXTENSIONS = frozenset({".pdf", ".txt", ".docx"})


class InvalidStoragePathError(ValueError):
    """Raised when a storage path is invalid or outside the uploads boundary."""


class UploadTooLargeError(ValueError):
    """Raised when an uploaded file exceeds the configured size limit."""


def get_uploads_root() -> Path:
    """Return the absolute uploads directory path."""
    settings = get_settings()
    return (BACKEND_ROOT / settings.uploads_dir).resolve()


def sanitize_filename(filename: str) -> str:
    """
    Normalize a client-provided filename to a safe basename.

    Rejects traversal patterns and strips directory components.
    """
    if not filename or not filename.strip():
        raise InvalidStoragePathError("Filename must not be empty")

    basename = Path(filename).name.strip()
    if not basename or basename in {".", ".."}:
        raise InvalidStoragePathError("Invalid filename")

    if ".." in filename or "/" in filename or "\\" in filename:
        raise InvalidStoragePathError("Filename must not contain path separators")

    if Path(filename).is_absolute():
        raise InvalidStoragePathError("Absolute filenames are not allowed")

    cleaned = UNSAFE_FILENAME_PATTERN.sub("_", basename).strip("._ ")
    if not cleaned:
        raise InvalidStoragePathError("Invalid filename")

    return cleaned


def build_unique_stored_filename(safe_filename: str) -> str:
    """Build a collision-resistant stored filename while preserving the original name."""
    unique_prefix = uuid.uuid4().hex[:6]
    return f"{unique_prefix}_{safe_filename}"


def build_storage_path(
    organization_id: uuid.UUID,
    filename: str,
    *,
    unique: bool = True,
) -> str:
    """
    Build an organization-scoped relative storage path.

    Format: uploads/{organization_id}/{uuid}_{filename} when unique=True.
    Legacy format uploads/{organization_id}/{filename} is used when unique=False.
    """
    settings = get_settings()
    safe_filename = sanitize_filename(filename)
    stored_filename = (
        build_unique_stored_filename(safe_filename) if unique else safe_filename
    )
    relative_path = Path(settings.uploads_dir) / str(organization_id) / stored_filename
    return relative_path.as_posix()


def resolve_storage_path(storage_path: str) -> Path:
    """
    Resolve a stored relative path to an absolute path within uploads/.

    Rejects absolute paths, traversal patterns, and paths outside uploads/.
    """
    if not storage_path or not storage_path.strip():
        raise InvalidStoragePathError("Storage path must not be empty")

    if Path(storage_path).is_absolute():
        raise InvalidStoragePathError("Absolute storage paths are not allowed")

    if ".." in Path(storage_path).parts:
        raise InvalidStoragePathError("Path traversal is not allowed")

    uploads_root = get_uploads_root()
    absolute_path = (BACKEND_ROOT / storage_path).resolve()

    try:
        absolute_path.relative_to(uploads_root)
    except ValueError as exc:
        raise InvalidStoragePathError(
            "Storage path is outside the uploads directory"
        ) from exc

    return absolute_path


def ensure_organization_upload_dir(organization_id: uuid.UUID) -> Path:
    """Create the organization upload directory if it does not exist."""
    org_dir = get_uploads_root() / str(organization_id)
    org_dir.mkdir(parents=True, exist_ok=True)
    return org_dir


def validate_document_extension(filename: str) -> None:
    """Reject unsupported document extensions before saving."""
    safe_filename = sanitize_filename(filename)
    suffix = Path(safe_filename).suffix.lower()
    if suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
        supported = ", ".join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))
        raise InvalidStoragePathError(
            f"Unsupported file type '{suffix or '(none)'}'. Supported types: {supported}"
        )


def save_document_file(
    organization_id: uuid.UUID,
    filename: str,
    content: bytes,
) -> tuple[str, str]:
    """
    Persist uploaded document bytes to the organization upload directory.

    Returns the sanitized display filename and unique relative storage path.
    """
    if not content:
        raise InvalidStoragePathError("Uploaded file is empty")

    settings = get_settings()
    if len(content) > settings.max_upload_size_bytes:
        raise UploadTooLargeError(
            f"Upload exceeds maximum size of {settings.max_upload_size_mb}MB"
        )

    validate_document_extension(filename)
    safe_filename = sanitize_filename(filename)
    storage_path = build_storage_path(organization_id, safe_filename, unique=True)
    absolute_path = resolve_storage_path(storage_path)
    ensure_organization_upload_dir(organization_id)
    absolute_path.write_bytes(content)
    return safe_filename, storage_path
