from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPrecipitationDepth

from custom_components.brightsky.sensor import CURRENT_SENSOR_DESCRIPTIONS


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
