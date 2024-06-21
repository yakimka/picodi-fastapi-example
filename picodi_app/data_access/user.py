import sqlite3
from collections.abc import Callable

from picodi_app.user import IUserRepository, User
from picodi_app.utils import sync_to_async
from picodi_app.weather import Coordinates


def user_deserializer(row: tuple) -> User:
    id, email, location, hashed_password = row
    return User(
        id=id,
        email=email,
        location=Coordinates.from_string(location),
        hashed_password=hashed_password,
    )


def user_serializer(user: User) -> tuple[str, ...]:
    return (user.id, user.email, user.location.to_string(), user.hashed_password)


class SqliteUserRepository(IUserRepository):
    def __init__(
        self,
        conn: sqlite3.Connection,
        deserializer: Callable[[tuple], User] = user_deserializer,
        serializer: Callable[[User], tuple] = user_serializer,
    ) -> None:
        self._conn = conn
        self._deserializer = deserializer
        self._serializer = serializer

    @sync_to_async
    def get_user_by_email(self, email: str) -> User | None:
        cursor = self._conn.execute(
            "SELECT id, email, location, hashed_password FROM users WHERE email = ?",
            (email,),
        )
        user = cursor.fetchone()
        if user is not None:
            return self._deserializer(user)
        return None

    @sync_to_async
    def create_user(self, user: User) -> None:
        self._conn.execute(
            (
                "INSERT INTO users (id, email, location, hashed_password) "
                "VALUES (?, ?, ?, ?)"
            ),
            self._serializer(user),
        )
        self._conn.commit()
