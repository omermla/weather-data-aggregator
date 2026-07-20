# Weather Data Aggregator

A Python command-line application that reads cities from a JSON file, fetches real-time weather data from the Open-Meteo API, caches responses locally, and displays aggregated weather statistics.

## Features

- Read city data from JSON
- Fetch weather data using Open-Meteo API
- Local SQLite caching (15-minute TTL)
- Average temperature calculation
- Hottest and coldest city detection
- Command-line interface
- Unit tests with pytest

## Requirements

- Python 3.10+
- requests
- pytest

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py --input cities.json --units metric
```

## Run Tests

```bash
pytest
```