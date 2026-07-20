from dataclasses import dataclass


@dataclass
class City:
    name: str
    country: str
    latitude: float
    longitude: float


@dataclass
class WeatherData:
    city: City
    temperature: float
    condition: str
    source: str