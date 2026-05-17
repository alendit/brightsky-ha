from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPrecipitationDepth

from custom_components.brightsky.sensor import (
    CURRENT_SENSOR_DESCRIPTIONS,
    forecast_sensor_name,
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
    assert forecast_sensor_name("hourly", 3, "solar") == "Hourly +3h solar"
    assert forecast_sensor_name("daily", 0, "sunshine") == "Today sunshine"
    assert forecast_sensor_name("daily", 2, "sunshine") == "Day +2 sunshine"
