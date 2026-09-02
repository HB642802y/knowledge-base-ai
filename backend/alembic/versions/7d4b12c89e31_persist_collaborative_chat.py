"""Persist collaborative chat questions and comments.

Revision ID: 7d4b12c89e31
Revises: 018232b6e756
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d4b12c89e31"
down_revision: Union[str, Sequence[str], None] = "018232b6e756"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("author_id", sa.Integer(), nullable=True))
    op.add_column("conversations", sa.Column("author_name", sa.String(), nullable=True))
    op.add_column("conversations", sa.Column("ai_answer", sa.Text(), nullable=True))
    op.add_column("conversations", sa.Column("ai_sources", sa.Text(), nullable=True))
    op.add_column("messages", sa.Column("author_id", sa.Integer(), nullable=True))
    op.add_column("messages", sa.Column("author_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "author_name")
    op.drop_column("messages", "author_id")
    op.drop_column("conversations", "ai_sources")
    op.drop_column("conversations", "ai_answer")
    op.drop_column("conversations", "author_name")
    op.drop_column("conversations", "author_id")
