from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[1]


def make_config(db_file: Path) -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_file.as_posix()}")
    return config


def book_columns(db_file: Path) -> list[str]:
    with closing(sqlite3.connect(db_file)) as connection:
        return [row[1] for row in connection.execute("PRAGMA table_info(books)")]


def test_migration_adds_and_removes_isbn(tmp_path: Path) -> None:
    db_file = tmp_path / "migration_test.db"
    config = make_config(db_file)

    command.upgrade(config, "0001")
    assert "isbn" not in book_columns(db_file)

    command.upgrade(config, "head")
    assert "isbn" in book_columns(db_file)

    command.downgrade(config, "0001")
    assert "isbn" not in book_columns(db_file)
