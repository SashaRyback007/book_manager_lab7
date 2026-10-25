"""Демонстраційний запуск: python -m book_manager.main"""

from __future__ import annotations

from book_manager.database import DATABASE_PATH, SessionLocal, engine
from book_manager.db_api import find_books_by_author
from book_manager.models import Base, Book
from book_manager.repositories import AuthorRepository, BookRepository
from book_manager.services import BookService, add_author_with_books


def main() -> None:
    # Для демо; у "бойовому" режимі схему створює `alembic upgrade head`.
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        authors = AuthorRepository(session)
        books = BookRepository(session)
        service = BookService(session)

        if authors.get_by_name("Taras Shevchenko") is None:
            add_author_with_books(
                session,
                "Taras Shevchenko",
                [
                    {"title": "Kobzar", "year": 1840, "pages": 120},
                    {"title": "Haidamaky", "year": 1841, "pages": 90},
                ],
            )
        if authors.get_by_name("Lesya Ukrainka") is None:
            author = authors.add("Lesya Ukrainka")
            books.add(
                Book(
                    title="Lisova pisnia",
                    year=1911,
                    pages=150,
                    author_id=author.id,
                )
            )

        print("Books:")
        for book in books.get_all():
            print(f"{book.id:3} {book.title:20} {book.year} {book.pages:4} p.")

        print("\nBy author (ORM):", [b.title for b in books.find_by_author_name("Taras Shevchenko")])
        print("By author (DB-API):", find_books_by_author(DATABASE_PATH, "Taras Shevchenko"))
        print("Year 1841:", [b.title for b in books.filter_by_year(1841)])

        largest = service.largest_book()
        if largest is not None:
            print("Largest book:", largest.title, largest.pages)
        print(f"Average pages: {service.average_pages():.2f}")

        # Демонстрація rollback: друга книга некоректна.
        try:
            add_author_with_books(
                session,
                "Broken Author",
                [
                    {"title": "Good", "year": 2000, "pages": 100},
                    {"title": "Bad", "year": 2000, "pages": 0},
                ],
            )
        except ValueError as error:
            print("\nRollback:", error)
        print("Broken Author saved?", authors.get_by_name("Broken Author") is not None)


if __name__ == "__main__":
    main()
