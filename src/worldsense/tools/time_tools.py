from __future__ import annotations

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from worldsense.models.preferences import UserPreferences
from worldsense.services.formatter import Formatter
from worldsense.services.geocoding_service import GeocodingService
from worldsense.services.time_service import TimeService


async def get_current_time(
    geocoder: GeocodingService,
    time_service: TimeService,
    preferences: UserPreferences,
    location: str,
) -> dict[str, str]:
    resolved = await geocoder.resolve_location(location)
    local_time = time_service.now_at(resolved)
    return {
        "location": resolved.name,
        "timezone": resolved.timezone,
        "local_time": Formatter.datetime(local_time, preferences),
        "day": local_time.strftime("%A"),
    }


async def convert_timezone(
    geocoder: GeocodingService,
    time_service: TimeService,
    preferences: UserPreferences,
    from_location: str,
    to_location: str,
    value: str,
) -> dict[str, str]:
    source, destination = await asyncio.gather(
        geocoder.resolve_location(from_location),
        geocoder.resolve_location(to_location),
    )
    converted = time_service.convert_timezone(source.timezone, destination.timezone, value)
    return {
        "from_location": source.name,
        "to_location": destination.name,
        "from_timezone": source.timezone,
        "to_timezone": destination.timezone,
        "converted_time": Formatter.datetime(converted, preferences),
    }


async def world_clock(
    geocoder: GeocodingService,
    time_service: TimeService,
    preferences: UserPreferences,
    locations: list[str],
) -> dict[str, list[dict[str, str]]]:
    if not locations:
        raise ValueError("locations must contain at least one location.")
    resolved = await asyncio.gather(*(geocoder.resolve_location(location) for location in locations))
    entries: list[dict[str, str]] = []
    for loc in resolved:
        current = time_service.now_at(loc)
        entries.append(
            {
                "location": loc.name,
                "timezone": loc.timezone,
                "local_time": Formatter.datetime(current, preferences),
                "day": current.strftime("%A"),
            }
        )
    return {"world_clock": entries}


async def get_timezone(geocoder: GeocodingService, location: str) -> dict[str, str]:
    resolved = await geocoder.resolve_location(location)
    now = datetime.now(ZoneInfo(resolved.timezone))
    return {
        "location": resolved.name,
        "timezone": resolved.timezone,
        "timezone_abbreviation": now.tzname() or "",
        "utc_offset": now.strftime("%z"),
    }
