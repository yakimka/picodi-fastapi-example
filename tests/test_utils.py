import pytest

from picodi_app.utils import (
    hash_password,
    rewrite_error,
    sync_to_async,
    verify_password,
)


def test_check_hash_of_valid_password():
    hashed = hash_password("12345678")

    assert verify_password(hashed, "12345678") is True


def test_not_verify_wrong_password():
    hashed = hash_password("12345678")

    assert verify_password(hashed, "87654321") is False


async def test_sync_to_async():
    @sync_to_async
    def sync_fn():
        return 42

    result = await sync_fn()

    assert result == 42


async def test_rewrite_error():
    @rewrite_error(ValueError, ValueError("new error"))
    async def raise_error():
        raise ValueError("old error")

    with pytest.raises(ValueError, match="new error"):
        await raise_error()
