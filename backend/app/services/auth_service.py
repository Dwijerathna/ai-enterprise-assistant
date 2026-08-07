"""Authentication business logic."""

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.User import User, UserRole
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.security.jwt import create_access_token, create_refresh_token
from app.security.password import hash_password, verify_password
from app.services.organization_service import OrganizationService

logger = get_logger(__name__)


class AuthService:
    """Handles registration, login, and token generation."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.org_service = OrganizationService(db)

    def register_user(self, data: RegisterRequest) -> RegisterResponse:
        """
        Register flow:
        Organization → Create User → Hash Password → Save Database

        Organization and admin user are persisted atomically in one transaction.
        """
        organization = self.org_service.new_organization(data.organization_name)

        try:
            if self.org_repo.get_by_name(data.organization_name):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Organization name already exists",
                )

            self.org_repo.stage_organization(organization)
            self.db.flush()

            if self.user_repo.get_by_email(data.email, organization.id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered in this organization",
                )

            if self.user_repo.get_by_username(data.username, organization.id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken in this organization",
                )

            user = User(
                organization_id=organization.id,
                username=data.username,
                email=data.email,
                password_hash=hash_password(data.password),
                role=UserRole.ADMIN,
            )
            self.user_repo.stage_user(user)
            self.db.flush()

            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Registration transaction failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed",
            ) from None

        return RegisterResponse(
            message="Registration successful",
            user_id=user.id,
            organization_id=organization.id,
        )

    def authenticate_user(self, data: LoginRequest) -> User:
        """
        Login flow:
        Email/password → Verify Password → Return User
        """
        if data.organization_name:
            organization = self.org_service.get_by_name(data.organization_name)
            if organization is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )
            user = self.user_repo.get_by_email(data.email, organization.id)
        else:
            matching_users = self.user_repo.get_users_by_email(data.email)
            if len(matching_users) > 1:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=(
                        "organization_name is required when the email exists "
                        "in multiple organizations"
                    ),
                )
            user = matching_users[0] if matching_users else None

        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """Generate access and refresh tokens for an authenticated user."""
        access_token = create_access_token(
            subject=user.id,
            organization_id=user.organization_id,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            organization_id=user.organization_id,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
