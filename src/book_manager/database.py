"""Підключення до БД: engine та фабрика сесій."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

DATABASE_PATH = "books.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


def _enable_sqlite_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:
    """SQLite за замовчуванням ігнорує FOREIGN KEY, тому вмикаємо перевірку."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_engine(url: str = DATABASE_URL, echo: bool = False) -> Engine:
    engine = create_engine(url, echo=echo)
    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


engine = create_db_engine()
SessionLocal = make_session_factory(engine)
