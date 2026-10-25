from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from book_manager.models import Book
from book_manager.repositories import AuthorRepository, BookRepository
from book_manager.services import BookService


def make_book(author_id: int, title: str = "Kobzar", year: int = 1840,
              pages: int = 120, isbn: str | None = None) -> Book:
    return Book(title=title, year=year, pages=pages, author_id=author_id, isbn=isbn)


# ---------- Author CRUD ----------

def test_author_crud(session: Session) -> None:
    repo = AuthorRepository(session)

    author = repo.add("Taras Shevchenko")                 # Create
    assert author.id is not None

    assert repo.get_by_id(author.id).name == "Taras Shevchenko"   # Read
    assert repo.get_by_name("Taras Shevchenko") is not None
    assert len(repo.get_all()) == 1

    updated = repo.update_name(author.id, "T. Shevchenko")        # Update
    assert updated is not None and updated.name == "T. Shevchenko"

    assert repo.delete(author.id) is True                         # Delete
    assert repo.get_by_id(author.id) is None
    assert repo.delete(author.id) is False


def test_author_name_is_unique(session: Session) -> None:
    repo = AuthorRepository(session)
    repo.add("Ivan Franko")
    with pytest.raises(IntegrityError):
        repo.add("Ivan Franko")


# ---------- Book CRUD ----------

def test_create_book(session: Session) -> None:
    author = AuthorRepository(session).add("Taras Shevchenko")
    saved = BookRepository(session).add(make_book(author.id))
    assert saved.id is not None
    assert saved.title == "Kobzar"
    assert saved.pages == 120


def test_read_book(session: Session) -> None:
    author = AuthorRepository(session).add("Lesya Ukrainka")
    repo = BookRepository(session)
    book = repo.add(make_book(author.id, title="Lisova pisnia", year=1911, pages=150))
    loaded = repo.get_by_id(book.id)
    assert loaded is not None
    assert loaded.title == "Lisova pisnia"
    assert repo.get_by_id(999999) is None


def test_update_book(session: Session) -> None:
    author = AuthorRepository(session).add("Taras Shevchenko")
    repo = BookRepository(session)
    book = repo.add(make_book(author.id))
    updated = repo.update(book.id, pages=200, title="Kobzar (2nd ed.)")
    assert updated is not None
    assert updated.pages == 200
    assert updated.title == "Kobzar (2nd ed.)"
    assert repo.update(999999, pages=1) is None
    with pytest.raises(ValueError):
        repo.update(book.id, unknown_field=1)


def test_delete_book(session: Session) -> None:
    author = AuthorRepository(session).add("Taras Shevchenko")
    repo = BookRepository(session)
    book = repo.add(make_book(author.id))
    assert repo.delete(book.id) is True
    assert repo.get_by_id(book.id) is None
    assert repo.delete(book.id) is False


# ---------- Relationship author -> books ----------

def test_author_books_relationship(session: Session) -> None:
    author = AuthorRepository(session).add("Taras Shevchenko")
    repo = BookRepository(session)
    repo.add(make_book(author.id, title="Kobzar"))
    repo.add(make_book(author.id, title="Haidamaky", year=1841, pages=90))

    session.refresh(author)
    assert [b.title for b in author.books] == ["Kobzar", "Haidamaky"]
    assert author.books[0].author.name == "Taras Shevchenko"


def test_find_by_author(session: Session) -> None:
    authors = AuthorRepository(session)
    first = authors.add("Taras Shevchenko")
    second = authors.add("Lesya Ukrainka")
    repo = BookRepository(session)
    repo.add(make_book(first.id, title="Kobzar"))
    repo.add(make_book(second.id, title="Lisova pisnia", year=1911, pages=150))

    assert [b.title for b in repo.find_by_author(first.id)] == ["Kobzar"]
    assert [b.title for b in repo.find_by_author_name("Lesya Ukrainka")] == ["Lisova pisnia"]
    assert repo.find_by_author_name("Nobody") == []


def test_cascade_delete_author_deletes_books(session: Session) -> None:
    author = AuthorRepository(session).add("Taras Shevchenko")
    repo = BookRepository(session)
    repo.add(make_book(author.id))
    AuthorRepository(session).delete(author.id)
    assert repo.get_all() == []


# ---------- Filters and aggregates ----------

def _seed(session: Session) -> None:
    author = AuthorRepository(session).add("Author")
    repo = BookRepository(session)
    repo.add(make_book(author.id, title="A", year=1990, pages=100))
    repo.add(make_book(author.id, title="B", year=2000, pages=300))
    repo.add(make_book(author.id, title="C", year=2000, pages=200))
    repo.add(make_book(author.id, title="D", year=2010, pages=400))


def test_filter_by_year(session: Session) -> None:
    _seed(session)
    repo = BookRepository(session)
    assert [b.title for b in repo.filter_by_year(2000)] == ["B", "C"]
    assert repo.filter_by_year(1800) == []
    assert [b.title for b in repo.filter_by_year_range(1995, 2010)] == ["B", "C", "D"]


def test_largest_book(session: Session) -> None:
    _seed(session)
    largest = BookRepository(session).largest_book()
    assert largest is not None
    assert largest.title == "D"
    assert largest.pages == 400


def test_average_pages(session: Session) -> None:
    _seed(session)
    assert BookService(session).average_pages() == 250.0


def test_aggregates_on_empty_table(session: Session) -> None:
    repo = BookRepository(session)
    assert repo.largest_book() is None
    assert repo.average_pages() == 0.0


# ---------- Constraints ----------

def test_unique_isbn(session: Session) -> None:
    author = AuthorRepository(session).add("Author")
    repo = BookRepository(session)
    repo.add(make_book(author.id, title="A", isbn="978-0-00-000000-1"))
    with pytest.raises(IntegrityError):
        repo.add(make_book(author.id, title="B", isbn="978-0-00-000000-1"))
    assert len(repo.get_all()) == 1  # сесія після помилки залишилась робочою


def test_multiple_books_without_isbn_allowed(session: Session) -> None:
    author = AuthorRepository(session).add("Author")
    repo = BookRepository(session)
    repo.add(make_book(author.id, title="A"))
    repo.add(make_book(author.id, title="B"))
    assert len(repo.get_all()) == 2


def test_pages_must_be_positive(session: Session) -> None:
    author = AuthorRepository(session).add("Author")
    with pytest.raises(IntegrityError):
        BookRepository(session).add(make_book(author.id, pages=0))


def test_foreign_key_is_enforced(session: Session) -> None:
    with pytest.raises(IntegrityError):
        BookRepository(session).add(make_book(author_id=999999))
