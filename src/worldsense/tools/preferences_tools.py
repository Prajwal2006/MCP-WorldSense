from __future__ import annotations

from worldsense.models.preferences import SetPreferencesRequest
from worldsense.storage.preferences_store import PreferencesStore


def apply_preference_command(command: str, request: SetPreferencesRequest) -> SetPreferencesRequest:
    lowered = command.lower()
    if "fahrenheit" in lowered:
        request.temperature_unit = "F"
    if "celsius" in lowered:
        request.temperature_unit = "C"
    if "24" in lowered and "time" in lowered:
        request.time_format = "24h"
    if "12" in lowered and "time" in lowered:
        request.time_format = "12h"
    if "mph" in lowered:
        request.wind_speed_unit = "mph"
    if "m/s" in lowered:
        request.wind_speed_unit = "ms"
    if "km/h" in lowered or "kph" in lowered:
        request.wind_speed_unit = "kmh"
    if "inhg" in lowered:
        request.pressure_unit = "inHg"
    if "hpa" in lowered:
        request.pressure_unit = "hPa"
    if "inches" in lowered or "inch" in lowered:
        request.precipitation_unit = "in"
    if "millimeter" in lowered or "mm" in lowered:
        request.precipitation_unit = "mm"
    return request


async def get_preferences(store: PreferencesStore) -> dict[str, str]:
    return (await store.get_preferences()).model_dump()


async def set_preferences(store: PreferencesStore, request: SetPreferencesRequest) -> dict[str, str]:
    if request.command:
        request = apply_preference_command(request.command, request)
    updated = await store.set_preferences(request)
    return updated.model_dump()


async def reset_preferences(store: PreferencesStore) -> dict[str, str]:
    return (await store.reset_preferences()).model_dump()
