"""Repository Pattern: уся робота з БД прихована тут."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from book_manager.models import Author, Book


def _commit(session: Session) -> None:
    """commit із rollback при помилці (IntegrityError тощо)."""
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise


class AuthorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, name: str) -> Author:
        author = Author(name=name)
        self.session.add(author)
        _commit(self.session)
        self.session.refresh(author)
        return author

    def get_by_id(self, author_id: int) -> Author | None:
        return self.session.get(Author, author_id)

    def get_by_name(self, name: str) -> Author | None:
        statement = select(Author).where(Author.name == name)
        return self.session.scalar(statement)

    def get_all(self) -> list[Author]:
        statement = select(Author).order_by(Author.id)
        return list(self.session.scalars(statement))

    def update_name(self, author_id: int, name: str) -> Author | None:
        author = self.get_by_id(author_id)
        if author is None:
            return None
        author.name = name
        _commit(self.session)
        self.session.refresh(author)
        return author

    def delete(self, author_id: int) -> bool:
        """Видаляє автора разом із його книгами (cascade)."""
        author = self.get_by_id(author_id)
        if author is None:
            return False
        self.session.delete(author)
        _commit(self.session)
        return True


class BookRepository:
    _UPDATABLE = {"title", "year", "pages", "author_id", "isbn"}

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- Create ---
    def add(self, book: Book) -> Book:
        self.session.add(book)
        _commit(self.session)
        self.session.refresh(book)
        return book

    # --- Read ---
    def get_by_id(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id)

    def get_all(self) -> list[Book]:
        statement = select(Book).order_by(Book.id)
        return list(self.session.scalars(statement))

    def find_by_author(self, author_id: int) -> list[Book]:
        statement = (
            select(Book).where(Book.author_id == author_id).order_by(Book.id)
        )
        return list(self.session.scalars(statement))

    def find_by_author_name(self, name: str) -> list[Book]:
        statement = (
            select(Book)
            .join(Author, Book.author_id == Author.id)
            .where(Author.name == name)
            .order_by(Book.id)
        )
        return list(self.session.scalars(statement))

    def filter_by_year(self, year: int) -> list[Book]:
        statement = select(Book).where(Book.year == year).order_by(Book.id)
        return list(self.session.scalars(statement))

    def filter_by_year_range(self, year_from: int, year_to: int) -> list[Book]:
        statement = (
            select(Book)
            .where(Book.year.between(year_from, year_to))
            .order_by(Book.year, Book.id)
        )
        return list(self.session.scalars(statement))

    def largest_book(self) -> Book | None:
        """Книга з найбільшою кількістю сторінок."""
        statement = select(Book).order_by(Book.pages.desc(), Book.id).limit(1)
        return self.session.scalar(statement)

    def average_pages(self) -> float:
        """Середня кількість сторінок (SQL AVG)."""
        result = self.session.scalar(select(func.avg(Book.pages)))
        return 0.0 if result is None else float(result)

    # --- Update ---
    def update(self, book_id: int, **changes: Any) -> Book | None:
        unknown = set(changes) - self._UPDATABLE
        if unknown:
            raise ValueError(f"Unknown fields: {sorted(unknown)}")
        book = self.get_by_id(book_id)
        if book is None:
            return None
        for field, value in changes.items():
            setattr(book, field, value)
        _commit(self.session)
        self.session.refresh(book)
        return book

    # --- Delete ---
    def delete(self, book_id: int) -> bool:
        book = self.get_by_id(book_id)
        if book is None:
            return False
        self.session.delete(book)
        _commit(self.session)
        return True
