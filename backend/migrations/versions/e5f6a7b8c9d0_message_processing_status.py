"""message processing status

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-05 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

message_processing_status = sa.Enum(
    "COMPLETED",
    "FAILED",
    name="message_processing_status",
)


def upgrade() -> None:
    message_processing_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "messages",
        sa.Column(
            "processing_status",
            message_processing_status,
            nullable=False,
            server_default="COMPLETED",
        ),
    )
    op.alter_column("messages", "processing_status", server_default=None)


def downgrade() -> None:
    op.drop_column("messages", "processing_status")
    message_processing_status.drop(op.get_bind(), checkfirst=True)
