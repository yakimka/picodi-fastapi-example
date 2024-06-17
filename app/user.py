import abc
import uuid
from dataclasses import dataclass


@dataclass
class User:
    id: str
    nickname: str
    hashed_password: str


class IUserRepository(abc.ABC):
    @abc.abstractmethod
    async def get_user_by_id(self, id: str) -> User | None:
        pass

    @abc.abstractmethod
    async def get_user_by_nickname(self, nickname: str) -> User | None:
        pass

    @abc.abstractmethod
    async def create_user(self, user: User) -> None:
        pass


def generate_new_user_id() -> str:
    return uuid.uuid4().hex
