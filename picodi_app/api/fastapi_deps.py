from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from picodi import Provide, inject

from picodi_app.deps import get_user_repository
from picodi_app.user import IUserRepository, User
from picodi_app.utils import verify_password

security = HTTPBasic()


@inject
async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_repo: IUserRepository = Depends(Provide(get_user_repository)),
) -> User | None:
    user = await user_repo.get_user_by_email(credentials.username)
    if user is None:
        return None
    if not verify_password(user.hashed_password, credentials.password):
        return None

    return user


async def get_current_user_or_raise_error(
    user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
