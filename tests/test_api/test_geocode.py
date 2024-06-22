import pytest

pytestmark = [pytest.mark.integration, pytest.mark.block_network]


@pytest.mark.vcr
async def test_can_geocode_city_by_name(api_client):
    response = await api_client.get("/weather/geocode", params={"city": "Kyiv"})

    assert response.status_code == 200, response.text
    check_geocode_resp_data(response.json())


def check_geocode_resp_data(data):
    __tracebackhide__ = True

    assert isinstance(data, list)
    assert len(data) > 0

    for city in data:
        check_geocoded_city_data(city)


def check_geocoded_city_data(data):
    __tracebackhide__ = True

    assert isinstance(data, dict)
    assert set(data.keys()) == {"name", "coordinates", "description"}

    assert isinstance(data["name"], str)
    assert "kyiv" in data["name"].lower()
    assert isinstance(data["coordinates"], dict)
    assert set(data["coordinates"].keys()) == {"latitude", "longitude"}
    assert isinstance(data["coordinates"]["latitude"], float)
    assert isinstance(data["coordinates"]["longitude"], float)
    assert isinstance(data["description"], str)
    assert len(data["description"]) > 5
