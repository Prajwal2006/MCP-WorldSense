from __future__ import annotations

import asyncio
import logging

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from worldsense.config.settings import settings
from worldsense.errors import LocationNotFoundError
from worldsense.models.location import LocationInfo
from worldsense.services.cache import TTLCache

logger = logging.getLogger(__name__)


class GeocodingService:
    def __init__(self) -> None:
        self._geocoder = Nominatim(user_agent=settings.geocoding_user_agent, timeout=settings.geocoding_timeout_seconds)
        self._tz_finder = TimezoneFinder()
        self._cache = TTLCache[LocationInfo](settings.cache_ttl_seconds)
        self._aliases = {
            "nyc": "New York City",
            "blr": "Bangalore",
            "la": "Los Angeles",
            "sf": "San Francisco",
        }

    async def resolve_location(self, location: str) -> LocationInfo:
        query = location.strip()
        if not query:
            raise LocationNotFoundError("Location cannot be empty.")

        normalized = self._aliases.get(query.lower(), query)
        cached = await self._cache.get(normalized.lower())
        if cached is not None:
            return cached

        result = await asyncio.to_thread(self._geocoder.geocode, normalized, addressdetails=True, language="en")
        if result is None:
            raise LocationNotFoundError(f"Could not find location '{location}'.")

        timezone = self._tz_finder.timezone_at(lat=result.latitude, lng=result.longitude)
        if timezone is None:
            timezone = self._tz_finder.closest_timezone_at(lat=result.latitude, lng=result.longitude)
        if timezone is None:
            raise LocationNotFoundError(f"Could not determine timezone for '{location}'.")

        location_info = LocationInfo(
            query=location,
            name=result.address.split(",")[0],
            latitude=result.latitude,
            longitude=result.longitude,
            timezone=timezone,
        )
        await self._cache.set(normalized.lower(), location_info)
        logger.info("resolved_location", extra={"query": location, "timezone": timezone})
        return location_info
