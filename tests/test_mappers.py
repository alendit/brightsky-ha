from datetime import UTC, datetime

from custom_components.brightsky.mappers import (
    aggregate_daily_forecast,
    map_brightsky_condition,
    map_hourly_forecast,
)


def test_maps_brightsky_icons_to_home_assistant_conditions() -> None:
    assert map_brightsky_condition({"icon": "clear-day", "condition": "dry"}) == "sunny"
    assert (
        map_brightsky_condition({"icon": "clear-night", "condition": "dry"})
        == "clear-night"
    )
    assert map_brightsky_condition({"icon": "partly-cloudy-day"}) == "partlycloudy"
    assert map_brightsky_condition({"condition": "thunderstorm"}) == "lightning-rainy"
    assert map_brightsky_condition({"condition": "sleet"}) == "snowy-rainy"


def test_maps_hourly_forecast_with_standard_and_precipitation_fields() -> None:
    record = {
        "timestamp": "2026-05-17T10:00:00+00:00",
        "icon": "rain",
        "temperature": 13.2,
        "dew_point": 7.1,
        "pressure_msl": 1013.3,
        "relative_humidity": 81,
        "cloud_cover": 88,
        "precipitation": 0.3,
        "precipitation_probability": 42,
        "wind_direction": 190,
        "wind_speed": 14.8,
        "wind_gust_speed": 31.5,
    }

    assert map_hourly_forecast(record) == {
        "datetime": "2026-05-17T10:00:00+00:00",
        "condition": "rainy",
        "native_temperature": 13.2,
        "native_dew_point": 7.1,
        "native_pressure": 1013.3,
        "humidity": 81,
        "cloud_coverage": 88,
        "native_precipitation": 0.3,
        "precipitation_probability": 42,
        "wind_bearing": 190,
        "native_wind_speed": 14.8,
        "native_wind_gust_speed": 31.5,
    }


def test_aggregates_daily_forecast_by_local_day() -> None:
    records = [
        {
            "timestamp": "2026-05-17T00:00:00+02:00",
            "icon": "clear-night",
            "temperature": 7.0,
            "precipitation": 0.0,
            "precipitation_probability": 5,
            "pressure_msl": 1010.0,
            "wind_speed": 5.0,
            "precipitation_probability_6h": 20,
            "solar": 0.1,
            "sunshine": 5,
            "visibility": 18000,
        },
        {
            "timestamp": "2026-05-17T12:00:00+02:00",
            "icon": "rain",
            "temperature": 15.0,
            "precipitation": 0.4,
            "precipitation_probability": 60,
            "pressure_msl": 1014.0,
            "wind_speed": 12.0,
            "wind_gust_speed": 22.0,
            "precipitation_probability_6h": 80,
            "solar": 0.4,
            "sunshine": 20,
            "visibility": 32000,
        },
        {
            "timestamp": "2026-05-18T00:00:00+02:00",
            "icon": "cloudy",
            "temperature": 9.0,
            "precipitation": 0.1,
            "precipitation_probability": 20,
        },
    ]

    daily = aggregate_daily_forecast(records)

    assert daily[0] == {
        "datetime": datetime(2026, 5, 17, tzinfo=UTC).isoformat(),
        "condition": "rainy",
        "native_temperature": 15.0,
        "native_templow": 7.0,
        "native_precipitation": 0.4,
        "precipitation_probability": 60,
        "precipitation_probability_6h": 80.0,
        "solar": 0.5,
        "sunshine": 25.0,
        "visibility": 32000.0,
        "native_pressure": 1012.0,
        "native_wind_speed": 12.0,
        "native_wind_gust_speed": 22.0,
    }
    assert daily[1]["datetime"] == datetime(
        2026, 5, 18, tzinfo=UTC
    ).isoformat()
    assert daily[1]["native_precipitation"] == 0.1
