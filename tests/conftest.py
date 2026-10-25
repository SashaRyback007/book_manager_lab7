from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from book_manager.database import create_db_engine, make_session_factory
from book_manager.models import Base


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    """Окрема тестова SQLite-база (файл у тимчасовій теці)."""
    test_engine = create_db_engine(f"sqlite:///{(tmp_path / 'test_books.db').as_posix()}")
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    factory = make_session_factory(engine)
    with factory() as db_session:
        yield db_session


@pytest.fixture
def db_path(engine: Engine) -> str:
    assert engine.url.database is not None
    return engine.url.database
