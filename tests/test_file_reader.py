import json
from pathlib import Path

import pytest

from weather_app.file_reader import load_cities


def test_load_cities_from_valid_json(tmp_path: Path) -> None:
    input_file = tmp_path / "cities.json"

    input_file.write_text(
        json.dumps(
            [
                {
                    "name": "Van",
                    "country": "TR",
                    "latitude": 38.5012,
                    "longitude": 43.373,
                }
            ]
        ),
        encoding="utf-8",
    )

    cities = load_cities(input_file)

    assert len(cities) == 1
    assert cities[0].name == "Van"
    assert cities[0].country == "TR"


def test_load_cities_raises_for_missing_file(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_cities(missing_file)


def test_load_cities_raises_for_invalid_json(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "cities.json"
    input_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(ValueError):
        load_cities(input_file)