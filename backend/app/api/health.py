"""HTTP endpoints for system health monitoring."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse
from app.services.health import HealthService

router = APIRouter(tags=["Health"])


def get_health_service(
    settings: Settings = Depends(get_settings),
) -> HealthService:
    """Provide a HealthService instance for the current request."""
    return HealthService(settings=settings)


@router.get("/health", response_model=HealthResponse)
def health_check(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """
    Return application and database health status.

    Used for system monitoring and deployment readiness checks.
    """
    return health_service.get_health_status()
