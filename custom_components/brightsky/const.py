from __future__ import annotations

DOMAIN = "brightsky"
DEFAULT_NAME = "Bright Sky"
DEFAULT_API_BASE_URL = "https://api.brightsky.dev"
DEFAULT_UPDATE_INTERVAL_SECONDS = 1800
MIN_UPDATE_INTERVAL_SECONDS = 900
DEFAULT_FORECAST_DAYS = 7
DEFAULT_HOURLY_SENSOR_INDICES = [0, 1, 2, 3, 6, 12, 24]
DEFAULT_DAILY_SENSOR_INDICES = [0, 1, 2, 3, 4]

CONF_CREATE_SENSORS = "create_sensors"
CONF_CREATE_WEATHER = "create_weather"
CONF_FORECAST_DAYS = "forecast_days"
CONF_HOURLY_SENSOR_INDICES = "hourly_sensor_indices"
CONF_DAILY_SENSOR_INDICES = "daily_sensor_indices"
CONF_MAX_DISTANCE = "max_distance"
CONF_MONITORED_CONDITIONS = "monitored_conditions"
CONF_TIMEZONE = "timezone"
CONF_UPDATE_INTERVAL = "update_interval"

PLATFORMS = ["weather", "sensor"]

DEFAULT_MONITORED_CONDITIONS = [
    "outdoor_temperature",
    "precipitation_60",
    "precipitation_probability",
    "precipitation_probability_6h",
    "solar_60",
    "solar_irradiance_60",
    "sunshine_60",
    "station_name",
]
