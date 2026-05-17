from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from statistics import mean
from typing import Any

from .models import ForecastRecord, WeatherRecord

HA_CONDITION_BY_ICON = {
    "clear-day": "sunny",
    "clear-night": "clear-night",
    "partly-cloudy-day": "partlycloudy",
    "partly-cloudy-night": "partlycloudy",
    "cloudy": "cloudy",
    "fog": "fog",
    "wind": "windy",
    "rain": "rainy",
    "sleet": "snowy-rainy",
    "snow": "snowy",
    "hail": "hail",
    "thunderstorm": "lightning-rainy",
}

HA_CONDITION_BY_CONDITION = {
    "dry": "sunny",
    "fog": "fog",
    "rain": "rainy",
    "sleet": "snowy-rainy",
    "snow": "snowy",
    "hail": "hail",
    "thunderstorm": "lightning-rainy",
}


def map_brightsky_condition(record: WeatherRecord) -> str | None:
    icon = record.get("icon")
    if isinstance(icon, str) and icon in HA_CONDITION_BY_ICON:
        return HA_CONDITION_BY_ICON[icon]
    condition = record.get("condition")
    if isinstance(condition, str):
        return HA_CONDITION_BY_CONDITION.get(condition)
    return None


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _without_none(data: ForecastRecord) -> ForecastRecord:
    return {key: value for key, value in data.items() if value is not None}


def map_hourly_forecast(record: WeatherRecord) -> ForecastRecord:
    return _without_none(
        {
            "datetime": record.get("timestamp"),
            "condition": map_brightsky_condition(record),
            "native_temperature": record.get("temperature"),
            "native_dew_point": record.get("dew_point"),
            "native_pressure": record.get("pressure_msl"),
            "humidity": record.get("relative_humidity"),
            "cloud_coverage": record.get("cloud_cover"),
            "native_precipitation": record.get("precipitation"),
            "precipitation_probability": record.get("precipitation_probability"),
            "wind_bearing": record.get("wind_direction"),
            "native_wind_speed": record.get("wind_speed"),
            "native_wind_gust_speed": record.get("wind_gust_speed"),
        }
    )


def _numeric_values(records: list[WeatherRecord], key: str) -> list[float]:
    values = []
    for record in records:
        value = record.get(key)
        if isinstance(value, int | float):
            values.append(float(value))
    return values


def _max_value(records: list[WeatherRecord], key: str) -> float | None:
    values = _numeric_values(records, key)
    return max(values) if values else None


def _min_value(records: list[WeatherRecord], key: str) -> float | None:
    values = _numeric_values(records, key)
    return min(values) if values else None


def _sum_value(records: list[WeatherRecord], key: str) -> float | None:
    values = _numeric_values(records, key)
    return round(sum(values), 3) if values else None


def _mean_value(records: list[WeatherRecord], key: str) -> float | None:
    values = _numeric_values(records, key)
    return round(mean(values), 1) if values else None


def _representative_condition(records: list[WeatherRecord]) -> str | None:
    priority = [
        "lightning-rainy",
        "hail",
        "snowy-rainy",
        "snowy",
        "rainy",
        "fog",
        "windy",
        "cloudy",
        "partlycloudy",
        "sunny",
        "clear-night",
    ]
    conditions = {map_brightsky_condition(record) for record in records}
    for condition in priority:
        if condition in conditions:
            return condition
    return None


def aggregate_daily_forecast(records: list[WeatherRecord]) -> list[ForecastRecord]:
    grouped: dict[Any, list[WeatherRecord]] = defaultdict(list)
    for record in records:
        timestamp = record.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        grouped[parse_timestamp(timestamp).date()].append(record)

    daily: list[ForecastRecord] = []
    for day, day_records in sorted(grouped.items()):
        midnight = datetime(day.year, day.month, day.day, tzinfo=UTC)
        daily.append(
            _without_none(
                {
                    "datetime": midnight.isoformat(),
                    "condition": _representative_condition(day_records),
                    "native_temperature": _max_value(day_records, "temperature"),
                    "native_templow": _min_value(day_records, "temperature"),
                    "native_precipitation": _sum_value(day_records, "precipitation"),
                    "precipitation_probability": _max_value(
                        day_records, "precipitation_probability"
                    ),
                    "precipitation_probability_6h": _max_value(
                        day_records, "precipitation_probability_6h"
                    ),
                    "solar": _sum_value(day_records, "solar"),
                    "sunshine": _sum_value(day_records, "sunshine"),
                    "visibility": _max_value(day_records, "visibility"),
                    "native_pressure": _mean_value(day_records, "pressure_msl"),
                    "native_wind_speed": _max_value(day_records, "wind_speed"),
                    "native_wind_gust_speed": _max_value(
                        day_records, "wind_gust_speed"
                    ),
                }
            )
        )
    return daily
