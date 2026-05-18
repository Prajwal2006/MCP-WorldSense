from pathlib import Path

import pytest

from worldsense.models.preferences import SetPreferencesRequest
from worldsense.storage.preferences_store import PreferencesStore


@pytest.mark.asyncio
async def test_preferences_round_trip(tmp_path: Path) -> None:
    store = PreferencesStore(tmp_path / "prefs.db")

    defaults = await store.get_preferences()
    assert defaults.temperature_unit == "C"

    updated = await store.set_preferences(SetPreferencesRequest(temperature_unit="F", time_format="12h"))
    assert updated.temperature_unit == "F"
    assert updated.time_format == "12h"

    reset = await store.reset_preferences()
    assert reset.temperature_unit == "C"
    assert reset.time_format == "24h"
