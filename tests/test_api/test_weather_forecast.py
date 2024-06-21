import pytest

pytestmark = [pytest.mark.integration, pytest.mark.block_network]


def test_anonymous_cant_get_current_weather_not_specifying_coords(api_client):
    response = api_client.get("/weather/current", auth=("", ""))

    assert response.status_code == 400, response.text
    assert "latitude and longitude are required" in response.json()["detail"].lower()
