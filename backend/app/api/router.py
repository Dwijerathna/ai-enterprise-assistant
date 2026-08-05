"""Central API router aggregating all versioned endpoints."""

from fastapi import APIRouter

from app.api import auth, conversations, documents, health, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)
api_router.include_router(conversations.router)
