import pytest
from picodi.helpers import enter

from picodi_app.cli.migrate import main as migrate_main
from picodi_app.conf import SqliteDatabaseSettings
from picodi_app.deps import get_sqlite_connection


@pytest.fixture()
def settings_for_tests(settings_for_tests, tmpdir):
    settings_for_tests.database.type = "sqlite"
    settings_for_tests.database.settings = SqliteDatabaseSettings(
        db_name=str(tmpdir / "db.sqlite"),
        create_db=False,
    )
    return settings_for_tests


def test_run_migration_command():
    migrate_main()

    with enter(get_sqlite_connection) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

    assert ("users",) in tables
