import sqlite3


def create_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            nickname TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL
        )
        """
    )
    conn.commit()
