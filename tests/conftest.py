import picodi
import pytest
from picodi.helpers import enter, lifespan

from picodi_app.conf import DatabaseSettings, Settings, SqliteDatabaseSettings
from picodi_app.deps import get_redis_client, get_settings, get_user_repository
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


@pytest.fixture()
def settings_for_tests():
    return Settings(
        database=DatabaseSettings(
            type="sqlite",
            settings=SqliteDatabaseSettings(
                db_name=":memory:",
                create_db=True,
            ),
        )
    )


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


# Fixture for clearing the Redis database after each test
@pytest.fixture(autouse=True)
async def _clear_redis(_override_deps, settings_for_tests):
    if settings_for_tests.database.type != "redis":
        yield
    else:
        async with enter(get_redis_client) as redis:
            await redis.flushdb()
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
