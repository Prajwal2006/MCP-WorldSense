import pytest

from worldsense.models.location import LocationInfo
from worldsense.models.preferences import UserPreferences
from worldsense.services.time_service import TimeService
from worldsense.tools import time_tools


class StubGeocoder:
    async def resolve_location(self, location: str) -> LocationInfo:
        if location.lower() == "tokyo":
            return LocationInfo(query=location, name="Tokyo", latitude=35.67, longitude=139.65, timezone="Asia/Tokyo")
        return LocationInfo(query=location, name="London", latitude=51.50, longitude=-0.12, timezone="Europe/London")


@pytest.mark.asyncio
async def test_convert_timezone() -> None:
    result = await time_tools.convert_timezone(
        StubGeocoder(),
        TimeService(),
        UserPreferences(time_format="24h"),
        "London",
        "Tokyo",
        "2026-05-18 12:00:00",
    )
    assert result["to_timezone"] == "Asia/Tokyo"
    assert result["from_timezone"] == "Europe/London"
