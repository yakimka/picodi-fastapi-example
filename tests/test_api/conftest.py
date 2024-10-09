import os

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from picodi_app.api.main import create_app
from picodi_app.conf import (
    DatabaseSettings,
    RedisDatabaseSettings,
    SqliteDatabaseSettings,
)


# Run tests with different database types.
#   In real project i'd stick with only sqlite memory for tests
#   or even mock the repository. It's faster and more reliable, repositories
#   are usually tested separately with real databases or services.
#   But for the sake of the example
#   i'll show how to run tests with different database types.
@pytest.fixture(params=["sqlite", "redis"])
def settings_for_tests(request, settings_for_tests):
    if request.param == "sqlite":
        db_settings = DatabaseSettings(
            type="sqlite",
            settings=SqliteDatabaseSettings(
                db_name=":memory:",
                create_db=True,
            ),
        )
    elif request.param == "redis":
        # Dirty hack to get the redis url from the environment variable.
        url = os.getenv("DATABASE__SETTINGS__URL", "redis://localhost:6379/1")
        db_settings = DatabaseSettings(
            type="redis",
            settings=RedisDatabaseSettings(
                url=url,
            ),
        )
    else:
        raise ValueError(f"Unsupported database type: {request.param}")

    settings_for_tests.database = db_settings
    return settings_for_tests


@pytest.fixture()
def fastapi_app() -> FastAPI:
    return create_app()


@pytest.fixture()
async def api_client(fastapi_app) -> AsyncClient:
    async with AsyncClient(
        app=fastapi_app, base_url="http://test/api", timeout=1
    ) as client:
        yield client
