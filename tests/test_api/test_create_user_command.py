from unittest.mock import ANY

import pytest

from picodi_app.cli.create_user import main as create_user_main
from picodi_app.conf import SqliteDatabaseSettings

pytestmark = pytest.mark.integration


@pytest.fixture()
def settings_for_tests(settings_for_tests, tmpdir):
    if not isinstance(settings_for_tests.database.settings, SqliteDatabaseSettings):
        return settings_for_tests

    # `create_user` will close the database connection,
    #   so we need to use a file-based database
    settings_for_tests.database.settings.db_name = str(tmpdir / "db.sqlite")
    return settings_for_tests


@pytest.mark.parametrize(
    "invalid_coords",
    [
        "50,45466.30,5238",
        "50.45466,30.5238,",
        "50.45466,30.5238,1",
        "50.45466,30.5238,1,2",
    ],
)
def test_cant_create_user_with_invalid_coords(invalid_coords):
    with pytest.raises(SystemExit, match="Invalid location format"):
        create_user_main(["me@me.com", "mypassword", invalid_coords])


async def test_can_create_user_from_cli_and_use_it_in_api(api_client):
    await create_user_main(["me@me.com", "mypassword", "50.45466,30.5238"])

    response = await api_client.get("/users/whoami", auth=("me@me.com", "mypassword"))

    assert response.status_code == 200, response.text
    response_data = response.json()
    assert response_data == {
        "id": ANY,
        "email": "me@me.com",
    }
    assert isinstance(response_data["id"], str)
