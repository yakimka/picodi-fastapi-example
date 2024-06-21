import pytest

pytestmark = pytest.mark.integration


def test_whoami_for_anonymous_return_401(api_client):
    response = api_client.get("/users/whoami")

    assert response.status_code == 401, response.text


async def test_whoami_with_wrong_password_return_401(
    api_client, user_repository, mother
):
    await user_repository.create_user(
        user=mother.create_user(
            id="00000000000000000000000000000001",
            email="me@me.com",
            password="12345678",
        )
    )

    response = api_client.get("/users/whoami", auth=("me@me.com", "wrong"))

    assert response.status_code == 401, response.text


async def test_whoami_with_valid_password_return_user_info(
    api_client, user_repository, mother
):
    await user_repository.create_user(
        user=mother.create_user(
            id="00000000000000000000000000000001",
            email="me@me.com",
            password="12345678",
        )
    )
    response = api_client.get("/users/whoami", auth=("me@me.com", "12345678"))

    assert response.status_code == 200, response.text
    assert response.json() == {
        "id": "00000000000000000000000000000001",
        "email": "me@me.com",
    }
