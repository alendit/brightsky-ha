from types import SimpleNamespace
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    EntityCategory,
    UnitOfPrecipitationDepth,
    UnitOfTemperature,
)

from custom_components.brightsky.const import DEFAULT_MONITORED_CONDITIONS
from custom_components.brightsky.models import BrightSkyData
from custom_components.brightsky.sensor import (
    CURRENT_SENSOR_DESCRIPTIONS,
    FORECAST_SENSOR_FIELDS,
    SOLAR_IRRADIANCE_UNIT,
    SOLAR_UNIT,
    expand_monitored_conditions,
    forecast_sensor_name,
    solar_irradiance_from_energy,
)


def test_precipitation_sensor_uses_home_assistant_precipitation_metadata() -> None:
    description = CURRENT_SENSOR_DESCRIPTIONS["precipitation_60"]

    assert description.device_class is SensorDeviceClass.PRECIPITATION
    assert (
        description.native_unit_of_measurement
        is UnitOfPrecipitationDepth.MILLIMETERS
    )
    assert description.state_class is SensorStateClass.MEASUREMENT


def test_station_name_sensor_is_non_numeric() -> None:
    description = CURRENT_SENSOR_DESCRIPTIONS["station_name"]

    assert description.device_class is None
    assert description.native_unit_of_measurement is None
    assert description.state_class is None
    assert description.entity_category is EntityCategory.DIAGNOSTIC


def test_current_sensors_have_runtime_name_fallbacks() -> None:
    assert (
        CURRENT_SENSOR_DESCRIPTIONS["precipitation_60"].name
        == "Precipitation 60 min"
    )
    assert (
        CURRENT_SENSOR_DESCRIPTIONS["solar_60"].name
        == "Solar irradiation 60 min"
    )
    assert CURRENT_SENSOR_DESCRIPTIONS["station_name"].name == "Station name"


def test_forecast_sensor_names_group_by_weather_variable_first() -> None:
    assert (
        forecast_sensor_name("hourly", 0, "precipitation")
        == "Precipitation (current hour)"
    )
    assert (
        forecast_sensor_name("hourly", 0, "solar")
        == "Solar irradiation (current hour)"
    )
    assert (
        forecast_sensor_name("hourly", 0, "solar_irradiance")
        == "Solar irradiance (current hour)"
    )
    assert (
        forecast_sensor_name("hourly", 1, "solar_irradiance")
        == "Solar irradiance (next hour)"
    )
    assert (
        forecast_sensor_name("hourly", 3, "solar")
        == "Solar irradiation (+3h)"
    )
    assert (
        forecast_sensor_name("hourly", 3, "solar_irradiance")
        == "Solar irradiance (+3h)"
    )
    assert forecast_sensor_name("hourly", 3, "sunshine") == "Sunshine (+3h)"
    assert forecast_sensor_name("daily", 0, "sunshine") == "Sunshine (today)"
    assert forecast_sensor_name("daily", 2, "sunshine") == "Sunshine (day +2)"
    assert (
        forecast_sensor_name("daily", 2, "precipitation_probability")
        == "Precipitation probability (day +2)"
    )


def test_solar_irradiance_conversion_uses_interval_minutes() -> None:
    assert solar_irradiance_from_energy(0.081, 10) == 486.0
    assert solar_irradiance_from_energy(0.207, 30) == 414.0
    assert solar_irradiance_from_energy(0.48, 60) == 480.0
    assert solar_irradiance_from_energy(0.563, 60) == 563.0
    assert solar_irradiance_from_energy(None, 60) is None


def test_solar_irradiance_sensor_metadata_is_model_ready() -> None:
    raw = CURRENT_SENSOR_DESCRIPTIONS["solar_60"]
    derived = CURRENT_SENSOR_DESCRIPTIONS["solar_irradiance_60"]

    assert raw.native_unit_of_measurement == SOLAR_UNIT
    assert derived.native_unit_of_measurement == SOLAR_IRRADIANCE_UNIT
    assert derived.state_class is SensorStateClass.MEASUREMENT
    assert "solar_irradiance_60" in DEFAULT_MONITORED_CONDITIONS


def test_outdoor_temperature_sensor_uses_current_weather_temperature() -> None:
    description = CURRENT_SENSOR_DESCRIPTIONS["outdoor_temperature"]
    coordinator: Any = SimpleNamespace(
        data=BrightSkyData(
            current={"temperature": 17.4},
            current_sources=[],
            hourly_records=[],
            forecast_sources=[],
        )
    )

    assert description.name == "Outdoor temperature"
    assert description.device_class is SensorDeviceClass.TEMPERATURE
    assert description.native_unit_of_measurement is UnitOfTemperature.CELSIUS
    assert description.state_class is SensorStateClass.MEASUREMENT
    assert description.value_fn(coordinator) == 17.4
    assert "outdoor_temperature" in DEFAULT_MONITORED_CONDITIONS


def test_current_solar_irradiance_60_falls_back_to_current_hour_forecast() -> None:
    description = CURRENT_SENSOR_DESCRIPTIONS["solar_irradiance_60"]
    coordinator: Any = SimpleNamespace(
        data=BrightSkyData(
            current={"solar_60": None},
            current_sources=[],
            hourly_records=[{"solar": 0.508}],
            forecast_sources=[],
        )
    )

    assert description.value_fn(coordinator) == 508.0


def test_current_solar_irradiance_60_prefers_current_weather_value() -> None:
    description = CURRENT_SENSOR_DESCRIPTIONS["solar_irradiance_60"]
    coordinator: Any = SimpleNamespace(
        data=BrightSkyData(
            current={"solar_60": 0.42},
            current_sources=[],
            hourly_records=[{"solar": 0.508}],
            forecast_sources=[],
        )
    )

    assert description.value_fn(coordinator) == 420.0


def test_existing_solar_monitoring_expands_to_matching_irradiance_sensor() -> None:
    assert expand_monitored_conditions(["solar_60"]) == [
        "solar_60",
        "solar_irradiance_60",
    ]
    assert expand_monitored_conditions(["solar_60", "solar_irradiance_60"]) == [
        "solar_60",
        "solar_irradiance_60",
    ]


def test_hourly_solar_irradiance_forecast_field_is_available() -> None:
    description = FORECAST_SENSOR_FIELDS["solar_irradiance"]

    assert description.unit == SOLAR_IRRADIANCE_UNIT
    assert description.device_class is None


def test_source_id_forecast_field_is_diagnostic_metadata() -> None:
    description = FORECAST_SENSOR_FIELDS["source_id"]

    assert description.unit is None
    assert description.device_class is None
    assert description.entity_category is EntityCategory.DIAGNOSTIC
