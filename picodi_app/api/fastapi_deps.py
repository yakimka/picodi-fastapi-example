"""
This module contains FastAPI dependencies.

# Picodi Note:

FastAPI has a built-in dependency injection system. It's a great way to manage
dependencies in your application. However, it lacks some features that Picodi
provides. For example, Picodi allows you to use scopes for your dependencies.
This is useful when you want to manage the lifecycle of your dependencies.
Another drawback of FastAPI's dependency injection system is that it works only
in FastAPI views. If you want to use dependencies in other parts of your
application, like workers, cli commands, etc., you need to pass them manually.

Picodi is a general-purpose dependency injection library that works with any
Python application. It provides a more flexible dependency injection system.
You can use it with FastAPI, Django, Flask, or any other Python framework.

So, this file contains only FastAPI dependencies that related only to FastAPI views.
Parsing query strings, request bodies, and headers, and other FastAPI-specific
dependencies are placed here.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from picodi.integrations.fastapi import Provide

from picodi_app.deps import get_user_repository
from picodi_app.user import IUserRepository, User
from picodi_app.utils import verify_password

security = HTTPBasic()


async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_repo: IUserRepository = Provide(get_user_repository, wrap=True),
) -> User | None:
    user = await user_repo.get_user_by_email(credentials.username)
    if user is None:
        return None
    if not verify_password(user.hashed_password, credentials.password):
        return None

    return user


# Picodi Note:
#   This dependency requires `get_current_user` dependency to be resolved first.
#   Even though `get_current_user` uses Picodi dependency `get_user_repository`,
#   you can use it here without `Provide` and `inject` because it's already
#   resolved in `get_current_user`.
async def get_current_user_or_raise_error(
    user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
