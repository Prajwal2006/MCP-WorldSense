import pytest

from worldsense.services.weather_service import WeatherService


@pytest.mark.asyncio
async def test_weather_service_parses_current_weather(monkeypatch: pytest.MonkeyPatch) -> None:
    service = WeatherService()

    async def fake_request(path: str, params: dict[str, object]) -> dict[str, object]:
        return {
            "current": {
                "time": "2026-05-18T10:00",
                "temperature_2m": 30,
                "apparent_temperature": 33,
                "relative_humidity_2m": 60,
                "wind_speed_10m": 12,
                "precipitation": 1.2,
                "cloud_cover": 70,
                "weather_code": 63,
                "pressure_msl": 1008,
            },
            "daily": {"sunrise": ["2026-05-18T05:30"], "sunset": ["2026-05-18T18:45"]},
        }

    monkeypatch.setattr(service, "_request", fake_request)

    result = await service.get_current_weather(1.0, 2.0, "Asia/Kolkata")
    assert result["weather_description"] == "Moderate rain"
    assert result["sunrise"] == "2026-05-18T05:30"

    await service.close()
