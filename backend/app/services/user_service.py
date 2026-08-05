"""User business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.User import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse


class UserService:
    """Handles user queries and organization-scoped operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def get_current_user_profile(self, user: User) -> UserResponse:
        """Return the authenticated user's profile."""
        return UserResponse.model_validate(user)

    def get_organization_users(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserResponse]:
        """Return all users in the caller's organization."""
        users = self.user_repo.get_users_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
        )
        return [UserResponse.model_validate(user) for user in users]

    def get_user_by_id(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> User:
        """Return a user scoped to an organization or raise 404."""
        user = self.user_repo.get_by_id(user_id)
        if user is None or user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
