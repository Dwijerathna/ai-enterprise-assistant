"""Health check business logic."""

from app.core.config import Settings
from app.db.session import check_database_connection
from app.schemas.health import HealthResponse


class HealthService:
    """Provides system health information for monitoring."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_health_status(self) -> HealthResponse:
        """Build the health response including database connectivity."""
        database_connected = check_database_connection()

        return HealthResponse(
            status="healthy" if database_connected else "degraded",
            environment=self.settings.environment,
            database="connected" if database_connected else "disconnected",
            version=self.settings.app_version,
        )
