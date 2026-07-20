from typing import Any

import requests

from weather_app.models import City, WeatherData


class WeatherAPIError(Exception):
    """Raised when weather data cannot be fetched from the external API."""


class OpenMeteoClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def fetch_weather(self, city: City, units: str) -> WeatherData:
        temperature_unit = "fahrenheit" if units == "imperial" else "celsius"

        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "current": "temperature_2m,weather_code",
            "temperature_unit": temperature_unit,
            "timezone": "auto",
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as error:
            raise WeatherAPIError(
                f"Request timed out for {city.name}."
            ) from error
        except requests.ConnectionError as error:
            raise WeatherAPIError(
                f"Network connection failed for {city.name}."
            ) from error
        except requests.HTTPError as error:
            status_code = error.response.status_code if error.response else "unknown"
            raise WeatherAPIError(
                f"HTTP error {status_code} while fetching {city.name}."
            ) from error
        except requests.RequestException as error:
            raise WeatherAPIError(
                f"Weather request failed for {city.name}: {error}"
            ) from error

        try:
            payload: dict[str, Any] = response.json()
            current = payload["current"]

            temperature = float(current["temperature_2m"])
            weather_code = int(current["weather_code"])
        except (ValueError, TypeError, KeyError) as error:
            raise WeatherAPIError(
                f"Malformed API response for {city.name}."
            ) from error

        return WeatherData(
            city=city,
            temperature=temperature,
            condition=weather_code_to_description(weather_code),
            source="API FETCH",
        )


def weather_code_to_description(code: int) -> str:
    descriptions = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        56: "Light Freezing Drizzle",
        57: "Dense Freezing Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Slight Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Slight Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Slight Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Slight Hail",
        99: "Thunderstorm with Heavy Hail",
    }

    return descriptions.get(code, "Unknown Weather")