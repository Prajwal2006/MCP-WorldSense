from datetime import datetime

from worldsense.models.preferences import UserPreferences
from worldsense.services.formatter import Formatter


def test_formatter_conversions_respect_preferences() -> None:
    prefs = UserPreferences(temperature_unit="F", wind_speed_unit="mph", precipitation_unit="in", pressure_unit="inHg")
    assert Formatter.temperature(20, prefs) == (68.0, "°F")
    assert Formatter.wind_speed(36, prefs) == (22.37, "mph")
    assert Formatter.precipitation(25.4, prefs) == (1.0, "in")
    assert Formatter.pressure(1013.25, prefs) == (29.92, "inHg")


def test_formatter_time_format() -> None:
    dt = datetime(2026, 5, 18, 21, 44, 22)
    assert Formatter.datetime(dt, UserPreferences(time_format="24h")) == "2026-05-18 21:44:22"
    assert Formatter.datetime(dt, UserPreferences(time_format="12h")) == "2026-05-18 09:44:22 PM"
