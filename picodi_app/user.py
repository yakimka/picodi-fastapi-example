from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from picodi_app.weather import Coordinates


@dataclass
class User:
    id: str
    email: str
    location: Coordinates
    hashed_password: str


class IUserRepository(abc.ABC):
    @abc.abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        pass

    @abc.abstractmethod
    async def create_user(self, user: User) -> None:
        pass


def generate_new_user_id() -> str:
    return uuid.uuid4().hex
