"""ORM-моделі: authors (1) -> (N) books."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("name", name="uq_authors_name"),)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id"),
        nullable=False,
    )
    # Додається міграцією 0002.
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)

    author: Mapped["Author"] = relationship(back_populates="books")

    __table_args__ = (
        CheckConstraint("pages > 0", name="ck_books_pages_positive"),
        CheckConstraint("year > 0", name="ck_books_year_positive"),
        UniqueConstraint("isbn", name="uq_books_isbn"),
    )
