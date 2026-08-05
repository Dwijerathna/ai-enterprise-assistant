"""Server-controlled document storage utilities."""

import re
import uuid
from pathlib import Path

from app.core.config import get_settings

# backend/ directory (parent of app/)
BACKEND_ROOT = Path(__file__).resolve().parents[2]

UNSAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._\- ]+")


class InvalidStoragePathError(ValueError):
    """Raised when a storage path is invalid or outside the uploads boundary."""


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


def build_storage_path(organization_id: uuid.UUID, filename: str) -> str:
    """
    Build an organization-scoped relative storage path.

    Format: uploads/{organization_id}/{filename}
    """
    settings = get_settings()
    safe_filename = sanitize_filename(filename)
    relative_path = Path(settings.uploads_dir) / str(organization_id) / safe_filename
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
