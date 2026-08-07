"""User data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.User import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user CRUD and organization-scoped queries."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def get_by_email(
        self,
        email: str,
        organization_id: uuid.UUID | None = None,
    ) -> User | None:
        """Find a user by email, optionally scoped to an organization."""
        stmt = select(User).where(User.email == email)
        if organization_id is not None:
            stmt = stmt.where(User.organization_id == organization_id)
        return self.db.scalars(stmt).first()

    def get_users_by_email(self, email: str) -> list[User]:
        """Return all users matching an email address across organizations."""
        stmt = select(User).where(User.email == email)
        return list(self.db.scalars(stmt).all())

    def get_by_username(
        self,
        username: str,
        organization_id: uuid.UUID,
    ) -> User | None:
        """Find a user by username within an organization."""
        stmt = select(User).where(
            User.username == username,
            User.organization_id == organization_id,
        )
        return self.db.scalars(stmt).first()

    def stage_user(self, user: User) -> User:
        """Stage a user in the session without committing."""
        return self.add(user)

    def create_user(self, user: User) -> User:
        """Persist a new user record."""
        return self.create(user)

    def get_users_by_organization(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Return users belonging to an organization."""
        stmt = (
            select(User)
            .where(User.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def update_user(self, user: User, data: dict) -> User:
        """Update an existing user record."""
        return self.update(user, data)

    def delete_user(self, user: User) -> None:
        """Delete a user record."""
        self.delete(user)
