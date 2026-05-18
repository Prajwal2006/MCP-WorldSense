from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Settings:
    geocoding_user_agent: str = "mcp-worldsense"
    geocoding_timeout_seconds: float = 8.0
    weather_base_url: str = "https://api.open-meteo.com"
    weather_timeout_seconds: float = 12.0
    request_retries: int = 3
    retry_backoff_seconds: float = 0.5
    cache_ttl_seconds: int = 300
    weather_max_concurrency: int = 4
    sqlite_path: Path = Path(os.getenv("WORLDSENSE_DB_PATH", "worldsense.db"))


settings = Settings()
