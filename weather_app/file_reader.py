import json
from pathlib import Path

from weather_app.models import City


def load_cities(file_path: Path) -> list[City]:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if file_path.suffix.lower() != ".json":
        raise ValueError("Only JSON input files are currently supported.")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON file: {error}") from error

    if not isinstance(raw_data, list):
        raise ValueError("The JSON file must contain a list of cities.")

    cities: list[City] = []

    for index, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"City entry {index} must be a JSON object.")

        required_fields = {"name", "country", "latitude", "longitude"}
        missing_fields = required_fields - item.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"City entry {index} is missing required fields: {missing}"
            )

        try:
            city = City(
                name=str(item["name"]).strip(),
                country=str(item["country"]).strip(),
                latitude=float(item["latitude"]),
                longitude=float(item["longitude"]),
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"City entry {index} contains invalid values."
            ) from error

        if not city.name or not city.country:
            raise ValueError(
                f"City entry {index} must have a name and country."
            )

        if not -90 <= city.latitude <= 90:
            raise ValueError(
                f"Invalid latitude for {city.name}: {city.latitude}"
            )

        if not -180 <= city.longitude <= 180:
            raise ValueError(
                f"Invalid longitude for {city.name}: {city.longitude}"
            )

        cities.append(city)

    if not cities:
        raise ValueError("The input file does not contain any cities.")

    return cities