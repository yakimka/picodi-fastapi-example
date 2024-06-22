import pytest

from picodi_app.weather import WindDirection

pytestmark = [pytest.mark.integration, pytest.mark.block_network]


def test_anonymous_cant_get_current_weather_not_specifying_coords(api_client):
    response = api_client.get("/weather/current", auth=("", ""))

    assert response.status_code == 400, response.text
    assert "latitude and longitude are required" in response.json()["detail"].lower()


@pytest.mark.vcr
def test_anonymous_can_get_current_weather_specifying_coords(api_client):
    response = api_client.get(
        "/weather/current",
        params={
            "latitude": 50.45466,
            "longitude": 30.5238,
        },
        auth=("", ""),
    )

    assert response.status_code == 200, response.text
    check_weather_resp_data(response.json())


@pytest.mark.usefixtures("user_in_db")
@pytest.mark.vcr
def test_user_can_get_current_weather_by_coords(api_client):
    response = api_client.get(
        "/weather/current",
        params={
            "latitude": 50.45466,
            "longitude": 30.5238,
        },
        auth=("me@me.com", "12345678"),
    )

    assert response.status_code == 200, response.text
    check_weather_resp_data(response.json())


@pytest.mark.usefixtures("user_in_db")
@pytest.mark.vcr
def test_user_can_get_current_weather_by_coords_from_profile(api_client):
    response = api_client.get(
        "/weather/current",
        auth=("me@me.com", "12345678"),
    )

    assert response.status_code == 200, response.text
    check_weather_resp_data(response.json())


def check_weather_resp_data(data):
    __tracebackhide__ = True

    assert set(data.keys()) == {
        "humidity",
        "precipitation",
        "temperature",
        "wind_direction",
        "wind_speed",
    }

    assert isinstance(data["humidity"], int)
    assert isinstance(data["precipitation"], bool)
    assert isinstance(data["temperature"], int)
    assert data["wind_direction"] in [item.value for item in WindDirection]
    assert isinstance(data["wind_speed"], int)
