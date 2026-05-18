from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TemperatureUnit = Literal["C", "F"]
WindSpeedUnit = Literal["kmh", "mph", "ms"]
TimeFormat = Literal["12h", "24h"]
PressureUnit = Literal["hPa", "inHg"]
PrecipitationUnit = Literal["mm", "in"]


class UserPreferences(BaseModel):
    temperature_unit: TemperatureUnit = "C"
    wind_speed_unit: WindSpeedUnit = "kmh"
    time_format: TimeFormat = "24h"
    pressure_unit: PressureUnit = "hPa"
    precipitation_unit: PrecipitationUnit = "mm"


class SetPreferencesRequest(BaseModel):
    temperature_unit: TemperatureUnit | None = None
    wind_speed_unit: WindSpeedUnit | None = None
    time_format: TimeFormat | None = None
    pressure_unit: PressureUnit | None = None
    precipitation_unit: PrecipitationUnit | None = None
    command: str | None = Field(default=None, description="Natural language preference command")
