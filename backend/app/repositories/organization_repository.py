"""Organization data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.Organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for organization CRUD operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Organization)

    def stage_organization(self, organization: Organization) -> Organization:
        """Stage an organization in the session without committing."""
        return self.add(organization)

    def create_organization(self, organization: Organization) -> Organization:
        """Persist a new organization record."""
        return self.create(organization)

    def get_by_name(self, name: str) -> Organization | None:
        """Find an organization by its display name."""
        stmt = select(Organization).where(Organization.name == name)
        return self.db.scalars(stmt).first()

    def get_by_id(self, record_id: uuid.UUID) -> Organization | None:
        """Return an organization by primary key."""
        return super().get_by_id(record_id)

    def update_organization(
        self,
        organization: Organization,
        data: dict,
    ) -> Organization:
        """Update an existing organization record."""
        return self.update(organization, data)
