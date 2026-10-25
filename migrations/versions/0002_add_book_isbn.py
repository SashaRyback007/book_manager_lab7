"""add book isbn

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-25
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(sa.Column("isbn", sa.String(length=20), nullable=True))
        batch_op.create_unique_constraint("uq_books_isbn", ["isbn"])


def downgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_constraint("uq_books_isbn", type_="unique")
        batch_op.drop_column("isbn")
