"""Database engine and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def create_db_engine(settings: Settings | None = None) -> Engine:
    """Create and cache the SQLAlchemy engine."""
    global _engine

    if _engine is not None:
        return _engine

    settings = settings or get_settings()
    _engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )
    return _engine


def create_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Create and cache the session factory bound to the engine."""
    global _session_factory

    if _session_factory is not None:
        return _session_factory

    engine = engine or create_db_engine()
    _session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request.

    The session is always closed after the request completes.
    """
    session_factory = create_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Verify that the database is reachable."""
    engine = create_db_engine()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database connection check failed")
        return False


def dispose_db_engine() -> None:
    """Dispose of the engine and reset cached database resources."""
    global _engine, _session_factory

    if _engine is not None:
        _engine.dispose()
        logger.info("Database engine disposed")

    _engine = None
    _session_factory = None
