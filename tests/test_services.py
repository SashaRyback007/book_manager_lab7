from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from book_manager.repositories import AuthorRepository, BookRepository
from book_manager.services import add_author_with_books


def test_add_author_with_books_commit(session: Session) -> None:
    author = add_author_with_books(
        session,
        "Taras Shevchenko",
        [
            {"title": "Kobzar", "year": 1840, "pages": 120},
            {"title": "Haidamaky", "year": 1841, "pages": 90},
        ],
    )
    assert author.id is not None
    books = BookRepository(session).find_by_author(author.id)
    assert [b.title for b in books] == ["Kobzar", "Haidamaky"]


def test_rollback_when_one_book_is_invalid(session: Session) -> None:
    with pytest.raises(ValueError):
        add_author_with_books(
            session,
            "Broken Author",
            [
                {"title": "Good", "year": 2000, "pages": 100},
                {"title": "Bad", "year": 2000, "pages": 0},
            ],
        )
    # Atomicity: не збережено ні автора, ні першої (коректної) книги.
    assert AuthorRepository(session).get_by_name("Broken Author") is None
    assert BookRepository(session).get_all() == []


def test_rollback_on_database_constraint_error(session: Session) -> None:
    with pytest.raises(IntegrityError):
        add_author_with_books(
            session,
            "Dup Author",
            [
                {"title": "A", "year": 2000, "pages": 100, "isbn": "X-1"},
                {"title": "B", "year": 2001, "pages": 110, "isbn": "X-1"},
            ],
        )
    assert AuthorRepository(session).get_by_name("Dup Author") is None
    assert BookRepository(session).get_all() == []


def test_session_usable_after_rollback(session: Session) -> None:
    with pytest.raises(ValueError):
        add_author_with_books(session, "Broken", [{"title": "", "year": 1, "pages": 1}])
    author = add_author_with_books(session, "Fine", [{"title": "T", "year": 2000, "pages": 10}])
    assert author.id is not None
