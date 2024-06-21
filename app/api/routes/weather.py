from typing import Annotated

from fastapi import APIRouter, Depends, Query
from picodi import Provide, inject
from pydantic import BaseModel, Field

from app.deps import get_geocoder_client, get_weather_client
from app.weather import City
from app.weather import Coordinates as DomainCoordinates
from app.weather import IGeocoderClient, IWeatherClient, WeatherData

router = APIRouter()


class Coordinates(BaseModel):
    latitude: float = Field(..., description="Latitude", examples=[50.45466])
    longitude: float = Field(..., description="Longitude", examples=[30.5238])

    def to_domain(self) -> DomainCoordinates:
        return DomainCoordinates(
            latitude=self.latitude,
            longitude=self.longitude,
        )


class CityResp(BaseModel):
    name: str = Field(..., description="City name", examples=["Kyiv", "London"])
    coordinates: Coordinates = Field(..., description="City coordinates")
    description: str = Field(
        ..., description="City description", examples=["Ukraine; Kyiv City"]
    )

    @classmethod
    def from_domain(cls, city: City) -> "CityResp":
        return cls(
            name=city.name,
            coordinates=Coordinates(
                latitude=city.coordinates.latitude,
                longitude=city.coordinates.longitude,
            ),
            description=city.description,
        )


class WeatherResp(BaseModel):
    temperature: int = Field(..., description="Temperature in Celsius", examples=[25])
    humidity: int = Field(..., description="Humidity in %", examples=[75])
    precipitation: bool = Field(..., description="Precipitation", examples=[True])
    wind_speed: int = Field(..., description="Wind speed in m/s", examples=[12])
    wind_direction: str = Field(..., description="Wind direction", examples=["N", "NE"])

    @classmethod
    def from_domain(cls, weather: WeatherData) -> "WeatherResp":
        return cls(
            temperature=round(weather.temperature.in_celsius()),
            humidity=round(weather.humidity),
            precipitation=weather.precipitation,
            wind_speed=round(weather.wind_speed.in_meters_per_second()),
            wind_direction=weather.wind_direction.value,
        )


@router.get("/current")
@inject
async def get_current_weather(
    latitude: Annotated[float, Query(..., example=50.45466)],
    longitude: Annotated[float, Query(..., example=30.5238)],
    weather_client: IWeatherClient = Depends(Provide(get_weather_client)),
) -> WeatherResp:
    weather = await weather_client.get_current_weather(
        DomainCoordinates(latitude=latitude, longitude=longitude)
    )
    return WeatherResp.from_domain(weather)


class ForecastResp(BaseModel):
    time: list[str] = Field(
        ..., description="Time", examples=[["2021-08-01T12:00:00Z"]]
    )
    weather_data: list[WeatherResp] = Field(..., description="Weather data")


@router.get("/forecast")
@inject
async def get_forecast(
    latitude: Annotated[float, Query(..., example=50.45466)],
    longitude: Annotated[float, Query(..., example=30.5238)],
    days: Annotated[int, Query(..., example=3)] = 1,
    weather_client: IWeatherClient = Depends(Provide(get_weather_client)),
) -> ForecastResp:
    forecast = await weather_client.get_forecast(
        DomainCoordinates(latitude=latitude, longitude=longitude), days=days
    )
    time_data = []
    weather_data = []
    for time, weather in forecast:
        time_data.append(time.isoformat())
        weather_data.append(WeatherResp.from_domain(weather))

    return ForecastResp(time=time_data, weather_data=weather_data)


@router.get("/geocode")
@inject
async def geocode(
    city: Annotated[str, Query(..., example="Kyiv")],
    geocoder_client: IGeocoderClient = Depends(Provide(get_geocoder_client)),
) -> list[CityResp]:
    results = await geocoder_client.get_coordinates_by_city(city)
    return [CityResp.from_domain(city) for city in results]
