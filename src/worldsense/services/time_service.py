from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from worldsense.models.location import LocationInfo


class TimeService:
    @staticmethod
    def now_at(location: LocationInfo) -> datetime:
        return datetime.now(tz=ZoneInfo(location.timezone))

    @staticmethod
    def convert_timezone(from_timezone: str, to_timezone: str, dt_input: str) -> datetime:
        parsed = TimeService._parse_datetime(dt_input)
        source_dt = parsed.replace(tzinfo=ZoneInfo(from_timezone))
        return source_dt.astimezone(ZoneInfo(to_timezone))

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return datetime.fromisoformat(value)
