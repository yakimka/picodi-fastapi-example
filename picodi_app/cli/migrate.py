import sqlite3

from picodi import Provide, inject

from picodi_app.data_access.sqlite import create_tables
from picodi_app.deps import get_sqlite_connection


@inject
def run_migrations(
    sqlite_conn: sqlite3.Connection = Provide(get_sqlite_connection),
) -> None:
    create_tables(sqlite_conn)


if __name__ == "__main__":
    run_migrations()
