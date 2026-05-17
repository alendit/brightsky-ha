# Bright Sky for Home Assistant

HACS-ready weather integration for the public Bright Sky API, with standard
Home Assistant forecasts plus extra DWD-backed precipitation, solar, sunshine,
wind, and station sensors.

Bright Sky uses open weather data from Germany's DWD through
[brightsky.dev](https://brightsky.dev/). The public API does not require an API
key.

## Quick Start

1. In HACS, add this repository as a custom integration repository.
2. Install **Bright Sky**.
3. Restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Search for **Bright Sky** and enter a name, latitude, longitude, and timezone.

After setup, Home Assistant creates a weather entity and, by default, a small
set of useful extra sensors. You can change the selected sensors later from the
integration options.

## Features

- Standard Home Assistant weather entity for current conditions.
- Hourly forecasts from Bright Sky `/weather` records.
- Daily forecasts derived from hourly records for Home Assistant weather cards.
- Current extra sensors for precipitation windows, solar irradiation, sunshine
  duration, wind details, and source station metadata.
- Configurable forecast-index sensors for precipitation, precipitation
  probability, solar, sunshine, visibility, and source data.
- UI config flow and options flow.
- No API key and no external Python Bright Sky wrapper.

## Details

### Entities

The integration creates one weather entity per configured location. It maps
Bright Sky fields into Home Assistant's standard weather shape:

- condition
- temperature and dew point
- pressure
- humidity
- cloud coverage
- visibility
- wind speed, gust speed, and bearing
- precipitation and precipitation probability in forecasts

Optional sensors expose Bright Sky values that do not fit the weather entity
well, including:

- `precipitation_10`, `precipitation_30`, `precipitation_60`
- `solar_10`, `solar_30`, `solar_60`
- `sunshine_30`, `sunshine_60`
- `wind_speed_60`, `wind_direction_60`, `wind_gust_speed_60`
- station name and forecast source fields

### Forecast Sensors

Forecast sensors are created from zero-based forecast indices. For example,
hourly indices `0,1,2,3,6,12,24` expose selected upcoming hourly records without
creating an entity for every hour in the full forecast horizon.

The options flow can change:

- monitored current sensors
- hourly forecast indices
- daily forecast indices
- forecast horizon
- update interval
- maximum station distance

### Defaults

- Update interval: `1800` seconds.
- Minimum update interval: `900` seconds.
- Forecast horizon: `7` days.
- Units: Bright Sky `dwd` units, matching Home Assistant native Celsius, hPa,
  km/h, mm, percent, and degree units.
- API base URL: `https://api.brightsky.dev`.

### Coverage Notes

Bright Sky is backed by DWD data. Observations focus on Germany, while forecasts
have broader coverage with lower station density outside Germany.

## Development

This project uses `uv`, `pytest`, `ruff`, and `mypy`.

```bash
uv run pytest
uv run ruff check .
uv run mypy
```

The implementation keeps API access in `api.py`, polling in `coordinator.py`,
pure forecast mapping in `mappers.py`, and Home Assistant entity glue in
`weather.py` and `sensor.py`.
