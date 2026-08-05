"""rag retrieval foundation

Revision ID: d4e5f6a7b8c9
Revises: ccc346f01b1a
Create Date: 2026-08-05 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "ccc346f01b1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "message_chunk_references",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("chunk_id", sa.UUID(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chunk_id"], ["document_chunks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_message_chunk_references_chunk_id"),
        "message_chunk_references",
        ["chunk_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_chunk_references_message_id"),
        "message_chunk_references",
        ["message_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_message_chunk_references_message_id"), table_name="message_chunk_references")
    op.drop_index(op.f("ix_message_chunk_references_chunk_id"), table_name="message_chunk_references")
    op.drop_table("message_chunk_references")
