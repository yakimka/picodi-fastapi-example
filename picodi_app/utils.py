import asyncio
import hashlib
import os
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from functools import partial, wraps
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


def sync_to_async(sync_fn: Callable[P, T]) -> Callable[P, Coroutine[None, None, T]]:
    """
    Wrapper to convert a synchronous function to an asynchronous function.
    Under the hood, it uses a thread pool to run the synchronous function.
    """

    @wraps(sync_fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(sync_fn, *args, **kwargs))

    return wrapper


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{pwdhash.hex()}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    salt, pwdhash = stored_password.split(":")
    pwdhash_check = hashlib.pbkdf2_hmac(
        "sha256", provided_password.encode("utf-8"), bytes.fromhex(salt), 100000
    )
    return pwdhash == pwdhash_check.hex()


@asynccontextmanager
async def rewrite_error(
    error: type[Exception] | tuple[type[Exception], ...], new_error: Exception
) -> AsyncGenerator[None, None]:
    try:
        yield
    except error as e:
        raise new_error from e
