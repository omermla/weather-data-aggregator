from pathlib import Path

from weather_app.cache import WeatherCache
from weather_app.models import City, WeatherData
from weather_app.service import WeatherService


class FakeAPIClient:
    def fetch_weather(
        self,
        city: City,
        units: str,
    ) -> WeatherData:
        return WeatherData(
            city=city,
            temperature=25.0,
            condition="Clear Sky",
            source="API FETCH",
        )


def test_service_fetches_and_summarizes_weather(
    tmp_path: Path,
) -> None:
    cache = WeatherCache(
        database_path=tmp_path / "test_cache.db"
    )

    service = WeatherService(
        api_client=FakeAPIClient(),
        cache=cache,
    )

    cities = [
        City("Van", "TR", 38.5012, 43.373),
        City("London", "UK", 51.5074, -0.1278),
    ]

    results, errors = service.get_weather_for_cities(
        cities,
        "metric",
    )

    summary = service.create_summary(results)

    assert len(results) == 2
    assert errors == []
    assert summary.processed_cities == 2
    assert summary.average_temperature == 25.0