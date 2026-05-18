from __future__ import annotations

from datetime import datetime

from worldsense.models.preferences import UserPreferences


class Formatter:
    @staticmethod
    def temperature(value_celsius: float, prefs: UserPreferences) -> tuple[float, str]:
        if prefs.temperature_unit == "F":
            return round((value_celsius * 9 / 5) + 32, 2), "°F"
        return round(value_celsius, 2), "°C"

    @staticmethod
    def wind_speed(value_kmh: float, prefs: UserPreferences) -> tuple[float, str]:
        if prefs.wind_speed_unit == "mph":
            return round(value_kmh * 0.621371, 2), "mph"
        if prefs.wind_speed_unit == "ms":
            return round(value_kmh / 3.6, 2), "m/s"
        return round(value_kmh, 2), "km/h"

    @staticmethod
    def precipitation(value_mm: float, prefs: UserPreferences) -> tuple[float, str]:
        if prefs.precipitation_unit == "in":
            return round(value_mm / 25.4, 2), "in"
        return round(value_mm, 2), "mm"

    @staticmethod
    def pressure(value_hpa: float, prefs: UserPreferences) -> tuple[float, str]:
        if prefs.pressure_unit == "inHg":
            return round(value_hpa * 0.0295299830714, 2), "inHg"
        return round(value_hpa, 2), "hPa"

    @staticmethod
    def datetime(dt: datetime, prefs: UserPreferences) -> str:
        if prefs.time_format == "12h":
            return dt.strftime("%Y-%m-%d %I:%M:%S %p")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
