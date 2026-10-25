"""Service layer: бізнес-логіка поверх репозиторіїв."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from book_manager.models import Author, Book
from book_manager.repositories import BookRepository


class BookService:
    def __init__(self, session: Session) -> None:
        self.books = BookRepository(session)

    def largest_book(self) -> Book | None:
        return self.books.largest_book()

    def average_pages(self) -> float:
        return self.books.average_pages()

    def books_after_year(self, year: int) -> list[Book]:
        return self.books.filter_by_year_range(year, 9999)


def _validate_book_data(data: dict[str, Any]) -> None:
    if not str(data.get("title", "")).strip():
        raise ValueError("Book title must not be empty")
    if int(data.get("year", 0)) <= 0:
        raise ValueError(f"Invalid year for '{data.get('title')}'")
    if int(data.get("pages", 0)) <= 0:
        raise ValueError(f"Invalid pages for '{data.get('title')}'")


def add_author_with_books(
    session: Session,
    author_name: str,
    books: list[dict[str, Any]],
) -> Author:
    """Транзакція: автор + усі його книги зберігаються як єдине ціле.

    Atomicity: якщо будь-яка книга некоректна (ValueError) або порушує
    обмеження БД (IntegrityError), виконується rollback, і в БД не
    залишається ні автора, ні жодної з книг.
    """
    try:
        author = Author(name=author_name)
        session.add(author)
        session.flush()  # отримуємо author.id без commit

        for data in books:
            _validate_book_data(data)
            session.add(
                Book(
                    title=data["title"],
                    year=int(data["year"]),
                    pages=int(data["pages"]),
                    isbn=data.get("isbn"),
                    author_id=author.id,
                )
            )
        session.flush()  # перевірка UNIQUE/CHECK/FK ще до commit

        session.commit()
        return author
    except Exception:
        session.rollback()
        raise
