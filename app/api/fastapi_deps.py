from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from picodi import Provide, inject

from app.deps import get_user_repository
from app.user import IUserRepository, User
from app.utils import verify_password

security = HTTPBasic()


@inject
async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_repo: IUserRepository = Depends(Provide(get_user_repository)),
) -> User:
    user = await user_repo.get_user_by_email(credentials.username)
    auth_error = HTTPException(status_code=401, detail="Invalid credentials")
    if user is None:
        raise auth_error
    if not verify_password(user.hashed_password, credentials.password):
        raise auth_error

    return user
