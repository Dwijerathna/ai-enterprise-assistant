"""Health check response schema."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""

    status: str = Field(..., examples=["healthy"])
    environment: str = Field(..., examples=["development"])
    database: str = Field(..., examples=["connected"])
    version: str = Field(..., examples=["1.0.0"])
