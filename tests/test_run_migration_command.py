import sqlite3

import pytest
from picodi import Provide, inject

from picodi_app.cli.migrate import main as migrate_main
from picodi_app.deps import get_sqlite_connection


@pytest.fixture()
@inject
def sqlite_conn(conn: sqlite3.Connection = Provide(get_sqlite_connection)):
    return conn


def test_run_migration_command(sqlite_conn):
    migrate_main()

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    assert ("users",) in tables
