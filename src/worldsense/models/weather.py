from __future__ import annotations

from pydantic import BaseModel


class TimezoneMetadata(BaseModel):
    location: str
    timezone: str
    abbreviation: str
    utc_offset: str
