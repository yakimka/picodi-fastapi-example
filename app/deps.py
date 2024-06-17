from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING

from picodi import ContextVarScope, Provide, dependency, inject

from app.data_access.user import SqliteUserRepository

if TYPE_CHECKING:
    from collections.abc import Generator

    from app.user import IUserRepository

logger = logging.getLogger(__name__)


class FastApiScope(ContextVarScope):
    pass


@dependency(scope_class=FastApiScope)
def get_sqlite_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect("db.sqlite", check_same_thread=False)
    logger.info("Connected to SQLite database. ID: %s", id(conn))
    try:
        yield conn
    finally:
        conn.close()
        logger.info("Closed SQLite connection. ID: %s", id(conn))


@inject
def get_user_repository(
    conn: sqlite3.Connection = Provide(get_sqlite_connection),
) -> IUserRepository:
    logger.info(
        "Creating SqliteUserRepository instance with connection ID: %s", id(conn)
    )
    return SqliteUserRepository(conn)
