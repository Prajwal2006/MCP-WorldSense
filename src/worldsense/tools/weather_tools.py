from __future__ import annotations

from worldsense.models.preferences import UserPreferences
from worldsense.services.formatter import Formatter
from worldsense.services.geocoding_service import GeocodingService
from worldsense.services.weather_service import WeatherService


async def get_current_weather(
    geocoder: GeocodingService,
    weather_service: WeatherService,
    preferences: UserPreferences,
    location: str,
) -> dict[str, object]:
    resolved = await geocoder.resolve_location(location)
    weather = await weather_service.get_current_weather(resolved.latitude, resolved.longitude, resolved.timezone)
    temperature, temperature_unit = Formatter.temperature(weather["temperature"], preferences)
    feels_like, feels_like_unit = Formatter.temperature(weather["feels_like"], preferences)
    wind_speed, wind_speed_unit = Formatter.wind_speed(weather["wind_speed"], preferences)
    precipitation, precipitation_unit = Formatter.precipitation(weather["precipitation"], preferences)
    pressure, pressure_unit = Formatter.pressure(weather["pressure"], preferences)

    return {
        "location": resolved.name,
        "temperature": temperature,
        "temperature_unit": temperature_unit,
        "feels_like": feels_like,
        "feels_like_unit": feels_like_unit,
        "humidity": weather["humidity"],
        "wind_speed": wind_speed,
        "wind_speed_unit": wind_speed_unit,
        "precipitation": precipitation,
        "precipitation_unit": precipitation_unit,
        "cloud_cover": weather["cloud_cover"],
        "pressure": pressure,
        "pressure_unit": pressure_unit,
        "weather_description": weather["weather_description"],
        "sunrise": weather["sunrise"],
        "sunset": weather["sunset"],
    }


async def get_hourly_forecast(
    geocoder: GeocodingService,
    weather_service: WeatherService,
    preferences: UserPreferences,
    location: str,
    hours: int,
) -> dict[str, object]:
    if hours < 1 or hours > 168:
        raise ValueError("hours must be between 1 and 168.")
    resolved = await geocoder.resolve_location(location)
    entries = await weather_service.get_hourly_forecast(resolved.latitude, resolved.longitude, resolved.timezone, hours)
    formatted: list[dict[str, object]] = []
    for entry in entries:
        temperature, temp_unit = Formatter.temperature(entry["temperature"], preferences)
        feels_like, feels_unit = Formatter.temperature(entry["feels_like"], preferences)
        wind_speed, wind_unit = Formatter.wind_speed(entry["wind_speed"], preferences)
        formatted.append(
            {
                "time": entry["time"],
                "temperature": temperature,
                "temperature_unit": temp_unit,
                "feels_like": feels_like,
                "feels_like_unit": feels_unit,
                "humidity": entry["humidity"],
                "wind_speed": wind_speed,
                "wind_speed_unit": wind_unit,
                "precipitation": entry["precipitation"],
                "weather_description": entry["weather_description"],
            }
        )
    return {"location": resolved.name, "hourly_forecast": formatted}


async def get_daily_forecast(
    geocoder: GeocodingService,
    weather_service: WeatherService,
    preferences: UserPreferences,
    location: str,
    days: int,
) -> dict[str, object]:
    if days < 1 or days > 16:
        raise ValueError("days must be between 1 and 16.")
    resolved = await geocoder.resolve_location(location)
    entries = await weather_service.get_daily_forecast(resolved.latitude, resolved.longitude, resolved.timezone, days)
    formatted: list[dict[str, object]] = []
    for entry in entries:
        max_temperature, max_temp_unit = Formatter.temperature(entry["max_temperature"], preferences)
        min_temperature, min_temp_unit = Formatter.temperature(entry["min_temperature"], preferences)
        wind_speed, wind_speed_unit = Formatter.wind_speed(entry["wind_speed"], preferences)
        precipitation, precipitation_unit = Formatter.precipitation(entry["precipitation"], preferences)
        formatted.append(
            {
                "date": entry["date"],
                "weather_description": entry["weather_description"],
                "max_temperature": max_temperature,
                "max_temperature_unit": max_temp_unit,
                "min_temperature": min_temperature,
                "min_temperature_unit": min_temp_unit,
                "wind_speed": wind_speed,
                "wind_speed_unit": wind_speed_unit,
                "precipitation": precipitation,
                "precipitation_unit": precipitation_unit,
                "sunrise": entry["sunrise"],
                "sunset": entry["sunset"],
                "moon_phase": entry["moon_phase"],
            }
        )
    return {"location": resolved.name, "daily_forecast": formatted}


async def get_weather_alerts(
    geocoder: GeocodingService,
    weather_service: WeatherService,
    location: str,
) -> dict[str, object]:
    resolved = await geocoder.resolve_location(location)
    alerts = await weather_service.get_weather_alerts(resolved.latitude, resolved.longitude, resolved.timezone)
    return {
        "location": resolved.name,
        **alerts,
    }
