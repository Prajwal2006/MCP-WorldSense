from __future__ import annotations

from pydantic import BaseModel, Field


class LocationInfo(BaseModel):
    query: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    latitude: float
    longitude: float
    timezone: str = Field(..., min_length=1)
