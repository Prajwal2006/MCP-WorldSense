from __future__ import annotations

import asyncio
import logging
import math
from datetime import datetime
from typing import Any

import httpx

from worldsense.config.settings import settings
from worldsense.errors import ExternalServiceError
from worldsense.services.cache import TTLCache

logger = logging.getLogger(__name__)

_WEATHER_CODE_DESCRIPTIONS: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}


class WeatherService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=settings.weather_base_url, timeout=httpx.Timeout(settings.weather_timeout_seconds))
        self._cache = TTLCache[dict[str, Any]](settings.cache_ttl_seconds)
        self._semaphore = asyncio.Semaphore(settings.weather_max_concurrency)

    async def close(self) -> None:
        await self._client.aclose()

    async def get_current_weather(self, latitude: float, longitude: float, timezone: str) -> dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "forecast_days": 1,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,precipitation,cloud_cover,weather_code,pressure_msl",
            "daily": "sunrise,sunset",
        }
        data = await self._request("/v1/forecast", params)
        current = data["current"]
        daily = data["daily"]
        return {
            "time": current["time"],
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "precipitation": current["precipitation"],
            "cloud_cover": current["cloud_cover"],
            "pressure": current["pressure_msl"],
            "weather_description": _WEATHER_CODE_DESCRIPTIONS.get(current.get("weather_code", -1), "Unknown"),
            "sunrise": daily["sunrise"][0],
            "sunset": daily["sunset"][0],
        }

    async def get_hourly_forecast(self, latitude: float, longitude: float, timezone: str, hours: int) -> list[dict[str, Any]]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "forecast_days": max(1, math.ceil(hours / 24)),
            "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,precipitation_probability,weather_code",
        }
        data = await self._request("/v1/forecast", params)
        hourly = data["hourly"]
        entries: list[dict[str, Any]] = []
        for idx, time_value in enumerate(hourly["time"][: max(1, hours)]):
            weather_code = hourly["weather_code"][idx]
            entries.append(
                {
                    "time": time_value,
                    "temperature": hourly["temperature_2m"][idx],
                    "feels_like": hourly["apparent_temperature"][idx],
                    "humidity": hourly["relative_humidity_2m"][idx],
                    "wind_speed": hourly["wind_speed_10m"][idx],
                    "precipitation": hourly["precipitation_probability"][idx],
                    "weather_description": _WEATHER_CODE_DESCRIPTIONS.get(weather_code, "Unknown"),
                }
            )
        return entries

    async def get_daily_forecast(self, latitude: float, longitude: float, timezone: str, days: int) -> list[dict[str, Any]]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "forecast_days": max(1, days),
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,wind_speed_10m_max",
        }
        data = await self._request("/v1/forecast", params)
        daily = data["daily"]
        entries: list[dict[str, Any]] = []
        for idx, date_value in enumerate(daily["time"][: max(1, days)]):
            weather_code = daily["weather_code"][idx]
            entries.append(
                {
                    "date": date_value,
                    "weather_description": _WEATHER_CODE_DESCRIPTIONS.get(weather_code, "Unknown"),
                    "max_temperature": daily["temperature_2m_max"][idx],
                    "min_temperature": daily["temperature_2m_min"][idx],
                    "precipitation": daily["precipitation_sum"][idx],
                    "wind_speed": daily["wind_speed_10m_max"][idx],
                    "sunrise": daily["sunrise"][idx],
                    "sunset": daily["sunset"][idx],
                    "moon_phase": self._moon_phase(date_value),
                }
            )
        return entries

    async def get_weather_alerts(self, latitude: float, longitude: float, timezone: str) -> dict[str, Any]:
        forecasts = await self.get_daily_forecast(latitude, longitude, timezone, days=2)
        alerts = [
            f"Potential severe weather: {entry['weather_description']} on {entry['date']}"
            for entry in forecasts
            if "thunderstorm" in entry["weather_description"].lower() or "violent" in entry["weather_description"].lower()
        ]
        return {
            "alerts": alerts,
            "summary": "No severe weather warnings." if not alerts else "Severe weather conditions may occur.",
        }

    async def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        key = f"{path}:{sorted(params.items())}"
        cached = await self._cache.get(key)
        if cached is not None:
            return cached

        last_error: Exception | None = None
        for attempt in range(1, settings.request_retries + 1):
            try:
                async with self._semaphore:
                    response = await self._client.get(path, params=params)
                response.raise_for_status()
                data = response.json()
                await self._cache.set(key, data)
                return data
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = exc
                logger.warning("weather_request_failed", extra={"attempt": attempt, "path": path})
                if attempt < settings.request_retries:
                    await asyncio.sleep(settings.retry_backoff_seconds * attempt)

        raise ExternalServiceError("Open-Meteo API request failed after retries") from last_error

    @staticmethod
    def _moon_phase(date_string: str) -> str:
        date = datetime.fromisoformat(date_string)
        phase = (date.toordinal() + 4) % 29
        if phase < 2:
            return "New Moon"
        if phase < 8:
            return "Waxing Crescent"
        if phase < 10:
            return "First Quarter"
        if phase < 15:
            return "Waxing Gibbous"
        if phase < 17:
            return "Full Moon"
        if phase < 23:
            return "Waning Gibbous"
        if phase < 25:
            return "Last Quarter"
        return "Waning Crescent"
