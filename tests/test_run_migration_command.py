import pytest
from picodi.helpers import enter

from picodi_app.cli.migrate import main as migrate_main
from picodi_app.deps import get_sqlite_connection


@pytest.fixture()
def sqlite_conn():
    with enter(get_sqlite_connection) as conn:
        yield conn


def test_run_migration_command(sqlite_conn):
    migrate_main()

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    assert ("users",) in tables
