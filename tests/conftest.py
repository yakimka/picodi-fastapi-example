import picodi
import pytest
from picodi.helpers import enter

from picodi_app.conf import DatabaseSettings, Settings, SqliteDatabaseSettings
from picodi_app.deps import get_redis_client, get_settings, get_user_repository
from picodi_app.weather import Coordinates

from .object_mother import ObjectMother

pytest_plugins = [
    "picodi.integrations._pytest",
    "picodi.integrations._pytest_asyncio",
]


def pytest_collection_modifyitems(items):
    for item in items:
        if "/test_api/" in str(item.fspath):
            item.add_marker(pytest.mark.picodi_init_dependencies)


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


# Picodi Note:
#   We need to override the settings for tests to ensure that our local settings
#   won't interfere with the tests.
@pytest.fixture()
def picodi_overrides(settings_for_tests):
    return [(get_settings, lambda: settings_for_tests)]


# Fixture for clearing the Redis database after each test
@pytest.fixture(autouse=True)
async def _clear_redis():
    if get_redis_client in picodi.registry.touched:
        async with enter(get_redis_client) as redis:
            await redis.flushdb()


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
