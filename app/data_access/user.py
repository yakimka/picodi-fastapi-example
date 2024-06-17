import sqlite3

from app.user import IUserRepository, User
from app.utils import sync_to_async


class SqliteUserRepository(IUserRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    @sync_to_async
    def get_user_by_id(self, id: str) -> User | None:
        cursor = self._conn.execute(
            "SELECT id, nickname, hashed_password FROM users WHERE id = ?", (id,)
        )
        user = cursor.fetchone()
        if user is not None:
            return User(*user)
        return None

    @sync_to_async
    def get_user_by_nickname(self, nickname: str) -> User | None:
        cursor = self._conn.execute(
            "SELECT id, nickname, hashed_password FROM users WHERE nickname = ?",
            (nickname,),
        )
        user = cursor.fetchone()
        if user is not None:
            return User(*user)
        return None

    @sync_to_async
    def create_user(self, user: User) -> None:
        self._conn.execute(
            "INSERT INTO users (id, nickname, hashed_password) VALUES (?, ?, ?)",
            (user.id, user.nickname, user.hashed_password),
        )
        self._conn.commit()
