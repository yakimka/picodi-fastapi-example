from typing import Any

from httpx import AsyncClient, HTTPError

from app.utils import rewrite_error
from app.weather import (
    CantGetDataError,
    City,
    Coordinates,
    IGeocoderClient,
    IWeatherClient,
    Speed,
    SpeedUnit,
    Temperature,
    TemperatureUnit,
    WeatherData,
    WindDirection,
)


class OpenMeteoWeatherClient(IWeatherClient):
    BASE_URL = "https://api.open-meteo.com/v1"

    def __init__(self, http_client: AsyncClient) -> None:
        self._http_client = http_client

    @rewrite_error(HTTPError, new_error=CantGetDataError("Can't get weather data"))
    async def get_current_weather(self, coords: Coordinates) -> WeatherData:
        needed_data = [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ]
        resp = await self._http_client.get(
            f"{self.BASE_URL}/forecast",
            params={
                "latitude": coords.latitude,
                "longitude": coords.longitude,
                "current": ",".join(needed_data),
            },
        )
        resp.raise_for_status()
        current_units: dict[str, str] = resp.json()["current_units"]
        current_data: dict[str, Any] = resp.json()["current"]
        return WeatherData(
            temperature=Temperature(
                value=float(current_data["temperature_2m"]),
                unit=TemperatureUnit(current_units["temperature_2m"]),
            ),
            humidity=float(current_data["relative_humidity_2m"]),
            precipitation=bool(current_data["precipitation"]),
            wind_speed=Speed(
                value=float(current_data["wind_speed_10m"]),
                unit=SpeedUnit(current_units["wind_speed_10m"]),
            ),
            wind_direction=WindDirection.from_degrees(
                current_data["wind_direction_10m"]
            ),
        )


class OpenMeteoGeocoderClient(IGeocoderClient):
    BASE_URL = "https://geocoding-api.open-meteo.com/v1"

    def __init__(self, http_client: AsyncClient) -> None:
        self._http_client = http_client

    @rewrite_error(HTTPError, new_error=CantGetDataError("Can't get coordinates"))
    async def get_coordinates_by_city(self, city: str) -> list[City]:
        resp = await self._http_client.get(
            f"{self.BASE_URL}/search",
            params={"name": city, "count": 10, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        results = resp.json()["results"]
        return [
            City(
                name=item["name"],
                coordinates=Coordinates(
                    latitude=item["latitude"], longitude=item["longitude"]
                ),
                description="; ".join(
                    item[key]
                    for key in ("country", "admin1", "admin2", "admin3")
                    if key in item
                ),
            )
            for item in results
        ]
