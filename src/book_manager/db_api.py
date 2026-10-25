"""Робота з БД через Python DB-API (sqlite3), без ORM."""

from __future__ import annotations

import sqlite3
from contextlib import closing


def find_books_by_author(
    database_path: str,
    author_name: str,
) -> list[tuple[str, int, int]]:
    """Параметризований пошук книг за автором: (title, year, pages)."""
    with closing(sqlite3.connect(database_path)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT books.title, books.year, books.pages
            FROM books
            JOIN authors
                ON books.author_id = authors.id
            WHERE authors.name = ?
            ORDER BY books.id
            """,
            (author_name,),
        )
        return cursor.fetchall()
