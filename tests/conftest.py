import picodi
import pytest
from picodi import Provide, inject

from picodi_app.conf import DatabaseSettings, Settings, SqliteDatabaseSettings
from picodi_app.deps import get_settings, get_user_repository
from picodi_app.user import IUserRepository
from picodi_app.weather import Coordinates

from .object_mother import ObjectMother


@pytest.fixture()
def mother():
    return ObjectMother()


@pytest.fixture(autouse=True)
def vcr_config():
    return {"ignore_hosts": ["testserver"]}


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
    with picodi.registry.override(get_settings, lambda: settings_for_tests):
        await picodi.init_dependencies()
        yield
        await picodi.shutdown_dependencies()


@pytest.fixture()
@inject
def user_repository(user_repo: IUserRepository = Provide(get_user_repository)):
    return user_repo


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