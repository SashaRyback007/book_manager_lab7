"""initial schema: authors and books

Revision ID: 0001
Revises:
Create Date: 2026-10-25
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("name", name="uq_authors_name"),
    )
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("pages", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"], name="fk_books_author_id"),
        sa.CheckConstraint("pages > 0", name="ck_books_pages_positive"),
        sa.CheckConstraint("year > 0", name="ck_books_year_positive"),
    )


def downgrade() -> None:
    op.drop_table("books")
    op.drop_table("authors")
