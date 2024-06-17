import argparse
import asyncio

from picodi import Provide, inject

from app.deps import get_user_repository
from app.user import IUserRepository, User, generate_new_user_id
from app.utils import hash_password


@inject
async def create_user(
    nickname: str,
    password: str,
    user_repo: IUserRepository = Provide(get_user_repository),
):
    new_user = User(
        id=generate_new_user_id(),
        nickname=nickname,
        hashed_password=hash_password(password),
    )
    await user_repo.create_user(new_user)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("nickname", type=str, help="User nickname")
    parser.add_argument("password", type=str, help="User password")
    args = parser.parse_args()
    asyncio.run(create_user(args.nickname, args.password))


if __name__ == "__main__":
    main()
