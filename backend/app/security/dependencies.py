"""FastAPI security dependencies."""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.User import User
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate the JWT from the Authorization header,
    then load the corresponding user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        organization_id = payload.get("organization_id")
        if user_id is None or organization_id is None:
            raise credentials_exception

        user_uuid = uuid.UUID(user_id)
        org_uuid = uuid.UUID(organization_id)
    except (JWTError, ValueError):
        raise credentials_exception from None

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_uuid)

    if user is None or user.organization_id != org_uuid:
        raise credentials_exception

    return user
