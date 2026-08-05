"""FastAPI application entry point and startup lifecycle."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.session import check_database_connection, create_db_engine, dispose_db_engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage application startup and shutdown events.

    Startup:
    - Load settings
    - Configure logging
    - Initialize the database engine
    - Verify database connectivity

    Shutdown:
    - Dispose database connections
    """
    settings = get_settings()
    setup_logging(settings)

    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Environment: %s", settings.environment)

    create_db_engine(settings)

    if check_database_connection():
        logger.info("Database connection established")
    else:
        logger.warning(
            "Database connection failed — API will start in degraded mode"
        )

    yield

    dispose_db_engine()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Application factory used by Uvicorn and tests."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/", tags=["Root"])
    def root() -> dict[str, str]:
        """Simple root endpoint for quick smoke tests."""
        return {
            "status": "healthy",
            "message": f"{settings.app_name} API running",
            "docs": "/docs",
        }

    return application


app = create_app()
