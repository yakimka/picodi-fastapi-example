from datetime import datetime
from typing import Any

from httpx import AsyncClient, HTTPError

from picodi_app.utils import rewrite_error
from picodi_app.weather import (
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

    @rewrite_error(
        HTTPError, new_error=CantGetDataError("Can't get current weather data")
    )
    async def get_current_weather(self, coords: Coordinates) -> WeatherData:
        needed_data = [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
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
        resp_data = resp.json()
        current_units: dict[str, str] = resp_data["current_units"]
        current_data: dict[str, Any] = resp_data["current"]
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

    @rewrite_error(HTTPError, new_error=CantGetDataError("Can't get forecast data"))
    async def get_forecast(
        self, coords: Coordinates, days: int
    ) -> list[tuple[datetime, WeatherData]]:
        needed_data = [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "wind_speed_10m",
            "wind_direction_10m",
        ]
        resp = await self._http_client.get(
            f"{self.BASE_URL}/forecast",
            params={
                "latitude": coords.latitude,
                "longitude": coords.longitude,
                "forecast_days": days,
                "hourly": ",".join(needed_data),
            },
        )
        resp.raise_for_status()
        resp_data = resp.json()
        hourly_units: dict[str, str] = resp_data["hourly_units"]
        hourly_data: dict[str, list[Any]] = resp_data["hourly"]

        time_data = hourly_data["time"]
        temp_data = hourly_data["temperature_2m"]
        humidity_data = hourly_data["relative_humidity_2m"]
        precipitation_data = hourly_data["precipitation_probability"]
        wind_speed_data = hourly_data["wind_speed_10m"]
        wind_direction_data = hourly_data["wind_direction_10m"]
        ziped = zip(
            time_data,
            temp_data,
            humidity_data,
            precipitation_data,
            wind_speed_data,
            wind_direction_data,
        )

        results = []
        for time, temp, humidity, precipitation, wind_speed, wind_direction in ziped:
            weather_data = WeatherData(
                temperature=Temperature(
                    value=float(temp),
                    unit=TemperatureUnit(hourly_units["temperature_2m"]),
                ),
                humidity=float(humidity),
                precipitation=precipitation > 49,
                wind_speed=Speed(
                    value=float(wind_speed),
                    unit=SpeedUnit(hourly_units["wind_speed_10m"]),
                ),
                wind_direction=WindDirection.from_degrees(wind_direction),
            )
            results.append((datetime.fromisoformat(time), weather_data))

        return results


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
