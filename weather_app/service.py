from dataclasses import dataclass

from weather_app.api_client import OpenMeteoClient, WeatherAPIError
from weather_app.cache import WeatherCache
from weather_app.models import City, WeatherData


@dataclass
class WeatherSummary:
    processed_cities: int
    average_temperature: float
    hottest: WeatherData
    coldest: WeatherData


class WeatherService:
    def __init__(
        self,
        api_client: OpenMeteoClient,
        cache: WeatherCache,
    ) -> None:
        self.api_client = api_client
        self.cache = cache

    def get_weather_for_cities(
        self,
        cities: list[City],
        units: str,
    ) -> tuple[list[WeatherData], list[str]]:
        results: list[WeatherData] = []
        errors: list[str] = []

        for city in cities:
            cached_weather = self.cache.get(city, units)

            if cached_weather is not None:
                results.append(cached_weather)
                continue

            try:
                live_weather = self.api_client.fetch_weather(city, units)
                self.cache.set(live_weather, units)
                results.append(live_weather)
            except WeatherAPIError as error:
                errors.append(str(error))

        return results, errors

    @staticmethod
    def create_summary(
        weather_results: list[WeatherData],
    ) -> WeatherSummary:
        if not weather_results:
            raise ValueError("No successful weather results are available.")

        average_temperature = sum(
            item.temperature for item in weather_results
        ) / len(weather_results)

        hottest = max(
            weather_results,
            key=lambda item: item.temperature,
        )

        coldest = min(
            weather_results,
            key=lambda item: item.temperature,
        )

        return WeatherSummary(
            processed_cities=len(weather_results),
            average_temperature=average_temperature,
            hottest=hottest,
            coldest=coldest,
        )