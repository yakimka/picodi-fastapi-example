from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class CantGetDataError(Exception):
    pass


class TemperatureUnit(Enum):
    celsius = "°C"
    fahrenheit = "°F"


@dataclass
class Temperature:
    value: float
    unit: TemperatureUnit

    def in_celsius(self) -> float:
        if self.unit == TemperatureUnit.celsius:
            return self.value
        if self.unit == TemperatureUnit.fahrenheit:
            return round(((self.value - 32) * 5 / 9), 2)
        raise ValueError(f"Unknown temperature unit: {self.unit}")


class SpeedUnit(Enum):
    km_h = "km/h"
    m_s = "m/s"


@dataclass
class Speed:
    value: float
    unit: SpeedUnit

    def in_meters_per_second(self) -> float:
        if self.unit == SpeedUnit.m_s:
            return self.value
        if self.unit == SpeedUnit.km_h:
            return round(((5 / 18) * self.value), 2)
        raise ValueError(f"Unknown speed unit: {self.unit}")


class WindDirection(Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"

    @classmethod
    def from_degrees(cls, degrees: float) -> WindDirection:
        directions = list(cls)
        directions_length = len(directions)
        index = round(degrees / (360 // directions_length)) % directions_length
        return directions[index]


@dataclass
class WeatherData:
    temperature: Temperature
    humidity: float
    precipitation: bool
    wind_speed: Speed
    wind_direction: WindDirection


@dataclass
class Coordinates:
    latitude: float
    longitude: float

    @classmethod
    def from_string(cls, coords: str) -> Coordinates:
        lat, lon = coords.split(",")
        return cls(latitude=float(lat), longitude=float(lon))

    def to_string(self) -> str:
        return f"{self.latitude},{self.longitude}"


class IWeatherClient(abc.ABC):
    @abc.abstractmethod
    async def get_current_weather(self, coords: Coordinates) -> WeatherData: ...

    @abc.abstractmethod
    async def get_forecast(
        self, coords: Coordinates, days: int
    ) -> list[tuple[datetime, WeatherData]]: ...


@dataclass
class City:
    name: str
    coordinates: Coordinates
    description: str


class IGeocoderClient(abc.ABC):
    @abc.abstractmethod
    async def get_coordinates_by_city(self, city: str) -> list[City]: ...
