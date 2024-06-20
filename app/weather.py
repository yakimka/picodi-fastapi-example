import abc
from dataclasses import dataclass
from enum import Enum


class CantGetDataError(Exception):
    pass


class TemperatureUnit(Enum):
    celsius = "°C"
    fahrenheit = "°F"


@dataclass
class Temperature:
    value: float
    unit: TemperatureUnit


class SpeedUnit(Enum):
    km_h = "km/h"
    m_s = "m/s"


@dataclass
class Speed:
    value: float
    unit: SpeedUnit


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
    def from_degrees(cls, degrees: float) -> "WindDirection":
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


class IWeatherClient(abc.ABC):
    @abc.abstractmethod
    async def get_weather(self, coords: Coordinates) -> WeatherData:
        pass


@dataclass
class City:
    name: str
    coordinates: Coordinates
    description: str


class IGeocoderClient(abc.ABC):
    @abc.abstractmethod
    async def get_coordinates_by_city(self, city: str) -> list[City]:
        pass
