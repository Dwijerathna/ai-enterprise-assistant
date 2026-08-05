"""Base repository providing shared database access patterns."""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository with reusable CRUD operations.

    Concrete repositories extend this class and add tenant-scoped queries.
    """

    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    def get_by_id(self, record_id: uuid.UUID) -> ModelType | None:
        """Return a single record by primary key."""
        return self.db.get(self.model, record_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Return paginated records."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def add(self, obj: ModelType) -> ModelType:
        """Stage a new record in the session without committing."""
        self.db.add(obj)
        return obj

    def flush(self) -> None:
        """Flush pending changes within the current transaction."""
        self.db.flush()

    def create(self, obj: ModelType) -> ModelType:
        """Persist a new record."""
        self.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType, data: dict[str, Any]) -> ModelType:
        """Apply partial updates to an existing record."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Remove a record from the database."""
        self.db.delete(obj)
        self.db.commit()
