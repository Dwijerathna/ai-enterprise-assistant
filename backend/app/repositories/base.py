"""Base repository providing shared database access patterns."""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository skeleton for data access.

    Concrete repositories will extend this class and enforce
    organization-scoped queries when business entities are added.
    """

    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model
