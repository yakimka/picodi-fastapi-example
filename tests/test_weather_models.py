import pytest

from picodi_app.weather import (
    Coordinates,
    Speed,
    SpeedUnit,
    Temperature,
    TemperatureUnit,
    WindDirection,
)


@pytest.mark.parametrize(
    "temp,expected",
    [
        (Temperature(32.0, TemperatureUnit.celsius), 32.0),
        (Temperature(32.33333, TemperatureUnit.celsius), 32.33333),
        (Temperature(32.0, TemperatureUnit.fahrenheit), 0.0),
        (Temperature(32.33333, TemperatureUnit.fahrenheit), 0.19),
        (Temperature(0.0, TemperatureUnit.celsius), 0.0),
        (Temperature(0.0, TemperatureUnit.fahrenheit), -17.78),
        (Temperature(128.0, TemperatureUnit.fahrenheit), 53.33),
    ],
)
def test_convert_temperature_to_celsius(temp, expected):
    result = temp.in_celsius()

    assert result == expected


@pytest.mark.parametrize(
    "speed,expected",
    [
        (Speed(32.0, SpeedUnit.m_s), 32.0),
        (Speed(120.3333, SpeedUnit.m_s), 120.3333),
        (Speed(32.0, SpeedUnit.km_h), 8.89),
        (Speed(120.3333, SpeedUnit.km_h), 33.43),
        (Speed(0.0, SpeedUnit.m_s), 0.0),
        (Speed(0.0, SpeedUnit.km_h), 0.0),
    ],
)
def test_convert_kmh_to_ms(speed, expected):
    result = speed.in_meters_per_second()

    assert result == expected


@pytest.mark.parametrize(
    "degree,expected",
    [
        (0, WindDirection.N),
        (45, WindDirection.NE),
        (90, WindDirection.E),
        (135, WindDirection.SE),
        (180, WindDirection.S),
        (225, WindDirection.SW),
        (270, WindDirection.W),
        (315, WindDirection.NW),
    ],
)
def test_convert_degree_to_wind_direction(degree, expected):
    result = WindDirection.from_degrees(degree)

    assert result == expected


def test_coordinates_serialization_deserialization():
    coordinates = Coordinates(52.52, 13.405)
    serialized = coordinates.to_string()
    deserialized = Coordinates.from_string(serialized)

    assert coordinates == deserialized
