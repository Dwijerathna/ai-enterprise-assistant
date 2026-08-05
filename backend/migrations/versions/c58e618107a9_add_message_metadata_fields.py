"""add message metadata fields

Revision ID: c58e618107a9
Revises: c58e618107a9
Create Date: 2026-08-06 00:01:09.990526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c58e618107a9'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True
        )
    )

    op.add_column(
        "messages",
        sa.Column(
            "token_usage",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "messages",
        sa.Column(
            "model_name",
            sa.String(length=255),
            nullable=True
        )
    )

def downgrade() -> None:
    op.execute("""
        ALTER TABLE messages
        DROP COLUMN IF EXISTS model_name
    """)

    op.execute("""
        ALTER TABLE messages
        DROP COLUMN IF EXISTS token_usage
    """)

    op.execute("""
        ALTER TABLE messages
        DROP COLUMN IF EXISTS error_message
    """)
