import os

import picodi
import pytest
from picodi.helpers import enter, lifespan

from picodi_app.conf import (
    DatabaseSettings,
    RedisDatabaseSettings,
    Settings,
    SqliteDatabaseSettings,
)
from picodi_app.deps import get_settings, get_user_repository
from picodi_app.weather import Coordinates

from .object_mother import ObjectMother


@pytest.fixture()
def mother():
    return ObjectMother()


@pytest.fixture(autouse=True)
def vcr_config():
    return {
        "ignore_hosts": ["testserver", "test"],
        "ignore_localhost": True,
    }


# Run tests with different database types.
#   In real project i'd stick with only sqlite memory for tests
#   or even mock the repository. It's faster and more reliable, repositories
#   are usually tested separately with real databases or services.
#   But for the sake of the example
#   i'll show how to run tests with different database types.
@pytest.fixture(params=["sqlite", "redis"])
def settings_for_tests(request):
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

    return Settings(database=db_settings)


@pytest.fixture(autouse=True)
async def _override_deps(settings_for_tests):
    # Picodi Note:
    #   We need to override the settings for tests to ensure that our local settings
    #   won't interfere with the tests. We also need to ensure that the database
    #   will be created in memory.
    #   Also we need to override the lifespan to ensure that all connections
    #   will be closed after each test.
    with picodi.registry.override(get_settings, lambda: settings_for_tests):
        async with lifespan():
            yield


@pytest.fixture()
def user_repository():
    # Picodi Note:
    #   We need to use the `enter` context manager to resolve the dependencies
    #   in the `user_repository` fixture, because we can't use `inject` decorator
    #   in fixtures.
    with enter(get_user_repository) as user_repo:
        yield user_repo


@pytest.fixture()
async def user_in_db(user_repository, mother):
    user = mother.create_user(
        email="me@me.com",
        password="12345678",
        location=Coordinates(
            latitude=51.5074,
            longitude=0.1278,
        ),
    )
    await user_repository.create_user(user=user)
    return user
