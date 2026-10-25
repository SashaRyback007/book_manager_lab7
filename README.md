# Book Manager — Лабораторна робота №7 (варіант 2)

Облік книг із persistence layer: SQLite, SQLAlchemy ORM, Repository Pattern,
транзакції, міграції Alembic та integration tests.

## Схема БД

```
authors                     books
-------                     -----
id PK                       id PK
name UNIQUE NOT NULL        title NOT NULL
                            year NOT NULL        CHECK (year > 0)
                            pages NOT NULL       CHECK (pages > 0)
                            author_id FK -> authors.id
                            isbn UNIQUE NULL     (додається міграцією 0002)
```

Зв'язок: один автор — багато книг (one-to-many), `cascade="all, delete-orphan"`.

## Архітектура

```
main.py -> Service Layer -> Repository -> SQLAlchemy ORM -> SQLite
                      \-> db_api.py (чистий sqlite3 DB-API, parameterized query)
```

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[test]"

alembic upgrade head               # створити/оновити схему (0001 + 0002)
alembic current                    # поточна версія
python -m book_manager.main        # демо
pytest -v                          # integration tests
```

Нова міграція (приклад): `alembic revision --autogenerate -m "message"`.

## Транзакція і ACID

`add_author_with_books()` додає автора разом із набором книг.

- **Atomicity** — при помилці будь-якої книги (`ValueError` або `IntegrityError`) виконується
  `session.rollback()`: не зберігається ні автор, ні жодна з книг.
- **Consistency** — PRIMARY/FOREIGN KEY, UNIQUE (`authors.name`, `books.isbn`) та CHECK
  (`pages > 0`, `year > 0`) не дозволяють потрапити в БД некоректним даним;
  у SQLite для цього вмикається `PRAGMA foreign_keys=ON`.
- **Isolation** — до `commit()` зміни видимі лише поточній сесії/транзакції.
- **Durability** — після `commit()` зміни записані у файл БД.

## Тести (`tests/`)

| Файл | Що перевіряє |
|------|--------------|
| `test_repositories.py` | CRUD автора і книги, relationship, `filter_by_year`, `largest_book`, `average_pages`, UNIQUE/CHECK/FK |
| `test_services.py` | транзакція `add_author_with_books`: commit і rollback |
| `test_db_api.py` | параметризований DB-API запит, захист від SQL injection |
| `test_migration.py` | `upgrade`/`downgrade` міграції `isbn` |

Тести працюють з окремою тестовою SQLite-базою у тимчасовій теці (`conftest.py`).
