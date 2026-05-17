from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPrecipitationDepth

from custom_components.brightsky.const import DEFAULT_MONITORED_CONDITIONS
from custom_components.brightsky.sensor import (
    CURRENT_SENSOR_DESCRIPTIONS,
    FORECAST_SENSOR_FIELDS,
    SOLAR_IRRADIANCE_UNIT,
    SOLAR_UNIT,
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


def test_current_sensors_have_runtime_name_fallbacks() -> None:
    assert (
        CURRENT_SENSOR_DESCRIPTIONS["precipitation_60"].name
        == "Precipitation 60 min"
    )
    assert CURRENT_SENSOR_DESCRIPTIONS["station_name"].name == "Station name"


def test_forecast_sensor_names_include_index_context() -> None:
    assert forecast_sensor_name("hourly", 0, "solar") == "Current hour solar"
    assert (
        forecast_sensor_name("hourly", 0, "solar_irradiance")
        == "Current hour solar irradiance"
    )
    assert (
        forecast_sensor_name("hourly", 1, "solar_irradiance")
        == "Next hour solar irradiance"
    )
    assert forecast_sensor_name("hourly", 3, "solar") == "Hourly +3h solar"
    assert (
        forecast_sensor_name("hourly", 3, "solar_irradiance")
        == "Hourly +3h solar irradiance"
    )
    assert forecast_sensor_name("daily", 0, "sunshine") == "Today sunshine"
    assert forecast_sensor_name("daily", 2, "sunshine") == "Day +2 sunshine"


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


def test_hourly_solar_irradiance_forecast_field_is_available() -> None:
    unit, device_class = FORECAST_SENSOR_FIELDS["solar_irradiance"]

    assert unit == SOLAR_IRRADIANCE_UNIT
    assert device_class is None
