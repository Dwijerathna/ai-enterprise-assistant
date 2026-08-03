"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the FastAPI application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Enterprise AI Assistant"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "enterprise_ai"
    # Security
secret_key: str
jwt_algorithm: str = "HS256"

access_token_expire_minutes: int = 15
refresh_token_expire_days: int = 7

refresh_cookie_name: str = "refresh_token"
cookie_secure: bool = False
cookie_httponly: bool = True
    

    # Logging
    log_level: str = "INFO"

    @computed_field
    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy connection URL from individual settings."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
