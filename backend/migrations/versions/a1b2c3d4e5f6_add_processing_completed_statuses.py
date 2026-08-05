"""add processing and completed document statuses

Revision ID: a1b2c3d4e5f6
Revises: 750d05d989ed
Create Date: 2026-08-05 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "750d05d989ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ingestion lifecycle statuses to the document_status enum."""
    op.execute("ALTER TYPE document_status ADD VALUE IF NOT EXISTS 'PROCESSING'")
    op.execute("ALTER TYPE document_status ADD VALUE IF NOT EXISTS 'COMPLETED'")


def downgrade() -> None:
    """PostgreSQL does not support removing enum values safely."""
    pass
