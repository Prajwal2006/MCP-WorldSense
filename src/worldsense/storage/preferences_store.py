from __future__ import annotations

import asyncio
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from worldsense.models.preferences import SetPreferencesRequest, UserPreferences


class PreferencesStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    temperature_unit TEXT NOT NULL,
                    wind_speed_unit TEXT NOT NULL,
                    time_format TEXT NOT NULL,
                    pressure_unit TEXT NOT NULL,
                    precipitation_unit TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO preferences (
                    id, temperature_unit, wind_speed_unit, time_format, pressure_unit, precipitation_unit, updated_at
                ) VALUES (1, 'C', 'kmh', '24h', 'hPa', 'mm', ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (datetime.now(timezone.utc).isoformat(),),
            )
            conn.commit()

    async def get_preferences(self) -> UserPreferences:
        return await asyncio.to_thread(self._get_preferences_sync)

    def _get_preferences_sync(self) -> UserPreferences:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT temperature_unit, wind_speed_unit, time_format, pressure_unit, precipitation_unit FROM preferences WHERE id = 1"
            ).fetchone()
        if row is None:
            return UserPreferences()
        return UserPreferences(
            temperature_unit=row[0],
            wind_speed_unit=row[1],
            time_format=row[2],
            pressure_unit=row[3],
            precipitation_unit=row[4],
        )

    async def set_preferences(self, request: SetPreferencesRequest) -> UserPreferences:
        return await asyncio.to_thread(self._set_preferences_sync, request)

    def _set_preferences_sync(self, request: SetPreferencesRequest) -> UserPreferences:
        current = self._get_preferences_sync()
        updates = request.model_dump(exclude_none=True)
        updates.pop("command", None)
        merged = current.model_copy(update=updates)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                UPDATE preferences
                SET temperature_unit=?, wind_speed_unit=?, time_format=?, pressure_unit=?, precipitation_unit=?, updated_at=?
                WHERE id=1
                """,
                (
                    merged.temperature_unit,
                    merged.wind_speed_unit,
                    merged.time_format,
                    merged.pressure_unit,
                    merged.precipitation_unit,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        return merged

    async def reset_preferences(self) -> UserPreferences:
        default = UserPreferences()
        await self.set_preferences(SetPreferencesRequest(**default.model_dump()))
        return default
