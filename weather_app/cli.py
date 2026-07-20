import argparse
from pathlib import Path

from weather_app.api_client import OpenMeteoClient
from weather_app.cache import WeatherCache
from weather_app.file_reader import load_cities
from weather_app.service import WeatherService, WeatherSummary


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch weather data for cities and generate "
            "an aggregated weather report."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the input JSON file.",
    )

    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Temperature units: metric or imperial.",
    )

    return parser


def run_cli() -> int:
    parser = create_parser()
    arguments = parser.parse_args()

    try:
        cities = load_cities(arguments.input)
    except (FileNotFoundError, ValueError) as error:
        print(f"Input error: {error}")
        return 1

    cache = WeatherCache(
        database_path=Path("weather_cache.db"),
        ttl_minutes=15,
    )

    api_client = OpenMeteoClient(timeout=10)

    service = WeatherService(
        api_client=api_client,
        cache=cache,
    )

    print("\nFetching weather data...\n")

    results, errors = service.get_weather_for_cities(
        cities=cities,
        units=arguments.units,
    )

    unit_symbol = "°C" if arguments.units == "metric" else "°F"

    for weather in results:
        print(
            f"[{weather.source}] "
            f"{weather.city.name}: "
            f"{weather.temperature:.1f}{unit_symbol} "
            f"({weather.condition})"
        )

    if errors:
        print("\nWarnings:")

        for error in errors:
            print(f"- {error}")

    if not results:
        print("\nNo weather data could be retrieved.")
        return 1

    summary = service.create_summary(results)
    print_summary(summary, unit_symbol)

    return 0


def print_summary(
    summary: WeatherSummary,
    unit_symbol: str,
) -> None:
    print("\n============== SUMMARY REPORT ==============")
    print(f"Processed Cities : {summary.processed_cities}")
    print(
        f"Average Temp     : "
        f"{summary.average_temperature:.2f}{unit_symbol}"
    )
    print(
        f"Hottest City     : "
        f"{summary.hottest.city.name} "
        f"({summary.hottest.temperature:.1f}{unit_symbol})"
    )
    print(
        f"Coldest City     : "
        f"{summary.coldest.city.name} "
        f"({summary.coldest.temperature:.1f}{unit_symbol})"
    )
    print("============================================")