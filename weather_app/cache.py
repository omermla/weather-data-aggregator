import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from weather_app.models import City, WeatherData


class WeatherCache:
    def __init__(
        self,
        database_path: Path,
        ttl_minutes: int = 15,
    ) -> None:
        self.database_path = database_path
        self.ttl = timedelta(minutes=ttl_minutes)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_cache (
                    cache_key TEXT PRIMARY KEY,
                    city_name TEXT NOT NULL,
                    country TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    units TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    condition TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _build_cache_key(city: City, units: str) -> str:
        return (
            f"{city.name.lower()}|"
            f"{city.country.lower()}|"
            f"{city.latitude}|"
            f"{city.longitude}|"
            f"{units}"
        )

    def get(self, city: City, units: str) -> WeatherData | None:
        cache_key = self._build_cache_key(city, units)

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT temperature, condition, created_at
                FROM weather_cache
                WHERE cache_key = ?
                """,
                (cache_key,),
            ).fetchone()

        if row is None:
            return None

        try:
            created_at = datetime.fromisoformat(row["created_at"])
        except ValueError:
            self.delete(cache_key)
            return None

        now = datetime.now(timezone.utc)

        if now - created_at > self.ttl:
            self.delete(cache_key)
            return None

        return WeatherData(
            city=city,
            temperature=float(row["temperature"]),
            condition=str(row["condition"]),
            source="CACHE HIT",
        )

    def set(
        self,
        weather_data: WeatherData,
        units: str,
    ) -> None:
        city = weather_data.city
        cache_key = self._build_cache_key(city, units)
        created_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO weather_cache (
                    cache_key,
                    city_name,
                    country,
                    latitude,
                    longitude,
                    units,
                    temperature,
                    condition,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    city.name,
                    city.country,
                    city.latitude,
                    city.longitude,
                    units,
                    weather_data.temperature,
                    weather_data.condition,
                    created_at,
                ),
            )

    def delete(self, cache_key: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM weather_cache WHERE cache_key = ?",
                (cache_key,),
            )