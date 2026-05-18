# MCP: WorldSense

MCP: WorldSense is a production-ready, async-first Python MCP server that provides global time, timezone, and weather intelligence for OpenClaw and future AI agents.

## Features

- Current time lookup from natural-language locations
- Timezone metadata and timezone conversion between locations
- Multi-location world clock
- Current weather + hourly and daily forecasts via Open-Meteo
- Weather alert summaries + moon phase in daily forecast
- Persistent SQLite user preferences for units/formatting
- Async I/O, retries, caching, structured error responses, and structured logging

## Project Layout

```text
src/worldsense/
  config/
  models/
  services/
  storage/
  tools/
  server.py
```

## Requirements

- Python 3.11+
- Internet access for Nominatim and Open-Meteo APIs

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Run Server

```bash
worldsense-server
```

Or:

```bash
python -m worldsense.server
```

## MCP Integration

Expose the executable in your MCP host configuration:

```json
{
  "name": "MCP: WorldSense",
  "command": "worldsense-server"
}
```

## Available MCP Tools

### Time
- `get_current_time(location)`
- `convert_timezone(from_location, to_location, datetime)`
- `world_clock(locations)`
- `get_timezone(location)`

### Weather
- `get_current_weather(location)`
- `get_hourly_forecast(location, hours=24)`
- `get_daily_forecast(location, days=5)`
- `get_weather_alerts(location)`

### Preferences
- `get_preferences()`
- `set_preferences(temperature_unit, wind_speed_unit, time_format, pressure_unit, precipitation_unit, command)`
- `reset_preferences()`

Natural language preference updates are supported through `set_preferences(command="Use Fahrenheit from now on")`.

## Example Calls

- `get_current_time("Tokyo")`
- `convert_timezone("Bangalore", "NYC", "2026-05-18 21:44:22")`
- `world_clock(["Paris France", "Tokyo", "NYC"])`
- `get_current_weather("London")`
- `get_hourly_forecast("Singapore", 12)`
- `set_preferences(command="Use 24 hour time and mph")`

## Raspberry Pi Deployment

1. Copy project to `/opt/mcp-worldsense`
2. Create venv and install dependencies
3. Copy service file:

```bash
sudo cp deploy/worldsense.service /etc/systemd/system/worldsense.service
sudo systemctl daemon-reload
sudo systemctl enable worldsense
sudo systemctl start worldsense
sudo systemctl status worldsense
```

## Configuration

Copy `.env.example` to `.env` and customize values as needed.

## Testing

```bash
pytest -q
```
