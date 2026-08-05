"""Organization business logic."""

import re
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.Organization import Organization
from app.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    """Handles organization creation and lookup."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.org_repo = OrganizationRepository(db)

    def _generate_qdrant_collection_name(self, name: str) -> str:
        """Build a unique, Qdrant-safe collection name from an org name."""
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        suffix = uuid.uuid4().hex[:8]
        return f"org_{slug}_{suffix}"[:255]

    def new_organization(self, name: str) -> Organization:
        """Build an unsaved organization entity with a unique Qdrant collection name."""
        return Organization(
            name=name,
            qdrant_collection_name=self._generate_qdrant_collection_name(name),
        )

    def create_organization(self, name: str) -> Organization:
        """Create a new organization with a unique Qdrant collection name."""
        if self.org_repo.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization name already exists",
            )

        organization = self.new_organization(name)
        return self.org_repo.create_organization(organization)

    def get_by_name(self, name: str) -> Organization | None:
        """Return an organization by name."""
        return self.org_repo.get_by_name(name)

    def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        """Return an organization by ID."""
        return self.org_repo.get_by_id(organization_id)
