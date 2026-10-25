from __future__ import annotations

import sqlite3
from contextlib import closing

from sqlalchemy.orm import Session

from book_manager.db_api import find_books_by_author
from book_manager.services import add_author_with_books


def test_find_books_by_author_db_api(session: Session, db_path: str) -> None:
    add_author_with_books(
        session, "Taras Shevchenko",
        [{"title": "Kobzar", "year": 1840, "pages": 120}],
    )
    add_author_with_books(
        session, "Lesya Ukrainka",
        [{"title": "Lisova pisnia", "year": 1911, "pages": 150}],
    )
    assert find_books_by_author(db_path, "Taras Shevchenko") == [("Kobzar", 1840, 120)]
    assert find_books_by_author(db_path, "Nobody") == []


def test_parameterized_query_resists_sql_injection(session: Session, db_path: str) -> None:
    add_author_with_books(
        session, "Taras Shevchenko",
        [{"title": "Kobzar", "year": 1840, "pages": 120}],
    )
    malicious = "x' OR '1'='1"
    assert find_books_by_author(db_path, malicious) == []

    with closing(sqlite3.connect(db_path)) as connection:
        count = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    assert count == 1
