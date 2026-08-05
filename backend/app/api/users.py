"""User API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.User import User
from app.schemas.user import UserListResponse, UserResponse
from app.security.dependencies import get_current_user
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Return the authenticated user's profile."""
    return user_service.get_current_user_profile(current_user)


@router.get("", response_model=UserListResponse)
def list_users(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """Return all users in the caller's organization."""
    users = user_service.get_organization_users(current_user.organization_id)
    return UserListResponse(users=users, total=len(users))
