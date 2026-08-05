"""Logging configuration for the application."""

import logging
import sys

from app.core.config import Settings


def setup_logging(settings: Settings) -> None:
    """
    Configure application-wide logging.

    Uses a single stream handler with a consistent format so log output
    is readable in both local development and container environments.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries in non-debug environments.
    if not settings.debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for module-level use."""
    return logging.getLogger(name)
