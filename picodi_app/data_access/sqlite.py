import sqlite3


def create_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            location TEXT NOT NULL,
            hashed_password TEXT NOT NULL
        )
        """
    )
    conn.commit()
