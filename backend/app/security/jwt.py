"""JWT token creation and decoding."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import Settings, get_settings


def create_access_token(
    subject: UUID,
    organization_id: UUID,
    role: str,
    settings: Settings | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access token."""
    settings = settings or get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "organization_id": str(organization_id),
        "role": role,
        "type": "access",
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    subject: UUID,
    organization_id: UUID,
    settings: Settings | None = None,
) -> str:
    """Create a long-lived refresh token."""
    settings = settings or get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": str(subject),
        "organization_id": str(organization_id),
        "type": "refresh",
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Raises JWTError if the token is invalid or expired.
    """
    settings = settings or get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
