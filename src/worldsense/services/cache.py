from __future__ import annotations

import asyncio
import time
from collections.abc import Hashable
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._store: dict[Hashable, tuple[float, T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: Hashable) -> T | None:
        async with self._lock:
            value = self._store.get(key)
            if value is None:
                return None
            expires_at, data = value
            if expires_at < time.time():
                self._store.pop(key, None)
                return None
            return data

    async def set(self, key: Hashable, value: T) -> None:
        async with self._lock:
            self._store[key] = (time.time() + self._ttl_seconds, value)
