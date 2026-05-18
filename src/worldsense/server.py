from __future__ import annotations

import atexit
import logging
from typing import Any

from fastmcp import FastMCP

from worldsense.config.settings import settings
from worldsense.logging_utils import configure_logging
from worldsense.models.preferences import SetPreferencesRequest
from worldsense.services.geocoding_service import GeocodingService
from worldsense.services.time_service import TimeService
from worldsense.services.weather_service import WeatherService
from worldsense.storage.preferences_store import PreferencesStore
from worldsense.tools import preferences_tools, time_tools, weather_tools

configure_logging()
logger = logging.getLogger(__name__)

mcp = FastMCP(name="MCP: WorldSense")

_geocoder = GeocodingService()
_time_service = TimeService()
_weather_service = WeatherService()
_preferences_store = PreferencesStore(settings.sqlite_path)


@atexit.register
def _cleanup() -> None:
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_weather_service.close())
        else:
            loop.run_until_complete(_weather_service.close())
    except RuntimeError:
        pass


def _error_payload(exc: Exception) -> dict[str, str]:
    logger.exception("tool_error", extra={"error": str(exc)})
    return {"error": exc.__class__.__name__, "message": str(exc)}


@mcp.tool()
async def get_current_time(location: str) -> dict[str, Any]:
    try:
        prefs = await _preferences_store.get_preferences()
        return await time_tools.get_current_time(_geocoder, _time_service, prefs, location)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def convert_timezone(from_location: str, to_location: str, datetime: str) -> dict[str, Any]:
    try:
        prefs = await _preferences_store.get_preferences()
        return await time_tools.convert_timezone(_geocoder, _time_service, prefs, from_location, to_location, datetime)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def world_clock(locations: list[str]) -> dict[str, Any]:
    try:
        prefs = await _preferences_store.get_preferences()
        return await time_tools.world_clock(_geocoder, _time_service, prefs, locations)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def get_timezone(location: str) -> dict[str, Any]:
    try:
        return await time_tools.get_timezone(_geocoder, location)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def get_current_weather(location: str) -> dict[str, Any]:
    try:
        prefs = await _preferences_store.get_preferences()
        return await weather_tools.get_current_weather(_geocoder, _weather_service, prefs, location)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def get_hourly_forecast(location: str, hours: int = 24) -> dict[str, Any]:
    try:
        prefs = await _preferences_store.get_preferences()
        return await weather_tools.get_hourly_forecast(_geocoder, _weather_service, prefs, location, hours)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def get_daily_forecast(location: str, days: int = 5) -> dict[str, Any]:
    try:
        prefs = await _preferences_store.get_preferences()
        return await weather_tools.get_daily_forecast(_geocoder, _weather_service, prefs, location, days)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def get_weather_alerts(location: str) -> dict[str, Any]:
    try:
        return await weather_tools.get_weather_alerts(_geocoder, _weather_service, location)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def get_preferences() -> dict[str, Any]:
    try:
        return await preferences_tools.get_preferences(_preferences_store)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def set_preferences(
    temperature_unit: str | None = None,
    wind_speed_unit: str | None = None,
    time_format: str | None = None,
    pressure_unit: str | None = None,
    precipitation_unit: str | None = None,
    command: str | None = None,
) -> dict[str, Any]:
    try:
        request = SetPreferencesRequest(
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            time_format=time_format,
            pressure_unit=pressure_unit,
            precipitation_unit=precipitation_unit,
            command=command,
        )
        return await preferences_tools.set_preferences(_preferences_store, request)
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
async def reset_preferences() -> dict[str, Any]:
    try:
        return await preferences_tools.reset_preferences(_preferences_store)
    except Exception as exc:
        return _error_payload(exc)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
