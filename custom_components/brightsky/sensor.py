from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfSpeed,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_CREATE_SENSORS,
    CONF_DAILY_SENSOR_INDICES,
    CONF_HOURLY_SENSOR_INDICES,
    CONF_MONITORED_CONDITIONS,
    DEFAULT_DAILY_SENSOR_INDICES,
    DEFAULT_HOURLY_SENSOR_INDICES,
    DEFAULT_MONITORED_CONDITIONS,
)
from .coordinator import BrightSkyCoordinator
from .entity import BrightSkyEntity

SOLAR_UNIT = "kWh/m²"


@dataclass(frozen=True, kw_only=True)
class BrightSkySensorDescription(SensorEntityDescription):
    value_fn: Callable[[BrightSkyCoordinator], Any]
    attr_fn: Callable[[BrightSkyCoordinator], dict[str, Any]] | None = None


def _current(key: str) -> Callable[[BrightSkyCoordinator], Any]:
    return lambda coordinator: coordinator.data.current.get(key)


def _primary_source(key: str) -> Callable[[BrightSkyCoordinator], Any]:
    return lambda coordinator: (
        coordinator.data.primary_source or {}
    ).get(key)


FORECAST_FIELD_NAMES = {
    "precipitation": "precipitation",
    "precipitation_probability": "precipitation probability",
    "precipitation_probability_6h": "6h precipitation probability",
    "solar": "solar",
    "sunshine": "sunshine",
    "visibility": "visibility",
    "source_id": "source ID",
}


def forecast_sensor_name(forecast_type: str, index: int, field: str) -> str:
    field_name = FORECAST_FIELD_NAMES[field]
    if forecast_type == "hourly":
        if index == 0:
            return f"Current hour {field_name}"
        if index == 1:
            return f"Next hour {field_name}"
        return f"Hourly +{index}h {field_name}"
    if index == 0:
        return f"Today {field_name}"
    if index == 1:
        return f"Tomorrow {field_name}"
    return f"Day +{index} {field_name}"


CURRENT_SENSOR_DESCRIPTIONS: dict[str, BrightSkySensorDescription] = {
    "precipitation_10": BrightSkySensorDescription(
        key="precipitation_10",
        name="Precipitation 10 min",
        translation_key="precipitation_10",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("precipitation_10"),
    ),
    "precipitation_30": BrightSkySensorDescription(
        key="precipitation_30",
        name="Precipitation 30 min",
        translation_key="precipitation_30",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("precipitation_30"),
    ),
    "precipitation_60": BrightSkySensorDescription(
        key="precipitation_60",
        name="Precipitation 60 min",
        translation_key="precipitation_60",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("precipitation_60"),
    ),
    "solar_10": BrightSkySensorDescription(
        key="solar_10",
        name="Solar 10 min",
        translation_key="solar_10",
        native_unit_of_measurement=SOLAR_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("solar_10"),
    ),
    "solar_30": BrightSkySensorDescription(
        key="solar_30",
        name="Solar 30 min",
        translation_key="solar_30",
        native_unit_of_measurement=SOLAR_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("solar_30"),
    ),
    "solar_60": BrightSkySensorDescription(
        key="solar_60",
        name="Solar 60 min",
        translation_key="solar_60",
        native_unit_of_measurement=SOLAR_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("solar_60"),
    ),
    "sunshine_30": BrightSkySensorDescription(
        key="sunshine_30",
        name="Sunshine 30 min",
        translation_key="sunshine_30",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("sunshine_30"),
    ),
    "sunshine_60": BrightSkySensorDescription(
        key="sunshine_60",
        name="Sunshine 60 min",
        translation_key="sunshine_60",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("sunshine_60"),
    ),
    "wind_speed_60": BrightSkySensorDescription(
        key="wind_speed_60",
        name="Wind speed 60 min",
        translation_key="wind_speed_60",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("wind_speed_60"),
    ),
    "wind_direction_60": BrightSkySensorDescription(
        key="wind_direction_60",
        name="Wind direction 60 min",
        translation_key="wind_direction_60",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("wind_direction_60"),
    ),
    "wind_gust_speed_60": BrightSkySensorDescription(
        key="wind_gust_speed_60",
        name="Wind gust speed 60 min",
        translation_key="wind_gust_speed_60",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_current("wind_gust_speed_60"),
    ),
    "station_name": BrightSkySensorDescription(
        key="station_name",
        name="Station name",
        translation_key="station_name",
        value_fn=_primary_source("station_name"),
    ),
}

FORECAST_SENSOR_FIELDS: dict[str, tuple[str | None, SensorDeviceClass | None]] = {
    "precipitation": (
        UnitOfPrecipitationDepth.MILLIMETERS,
        SensorDeviceClass.PRECIPITATION,
    ),
    "precipitation_probability": (PERCENTAGE, None),
    "precipitation_probability_6h": (PERCENTAGE, None),
    "solar": (SOLAR_UNIT, None),
    "sunshine": (UnitOfTime.MINUTES, None),
    "visibility": (UnitOfLength.METERS, SensorDeviceClass.DISTANCE),
    "source_id": (None, None),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    if not entry.options.get(
        CONF_CREATE_SENSORS, entry.data.get(CONF_CREATE_SENSORS, True)
    ):
        return

    coordinator: BrightSkyCoordinator = entry.runtime_data
    monitored = entry.options.get(
        CONF_MONITORED_CONDITIONS,
        entry.data.get(CONF_MONITORED_CONDITIONS, DEFAULT_MONITORED_CONDITIONS),
    )
    hourly_indices = entry.options.get(
        CONF_HOURLY_SENSOR_INDICES,
        entry.data.get(CONF_HOURLY_SENSOR_INDICES, DEFAULT_HOURLY_SENSOR_INDICES),
    )
    daily_indices = entry.options.get(
        CONF_DAILY_SENSOR_INDICES,
        entry.data.get(CONF_DAILY_SENSOR_INDICES, DEFAULT_DAILY_SENSOR_INDICES),
    )

    entities: list[SensorEntity] = [
        BrightSkyCurrentSensor(coordinator, CURRENT_SENSOR_DESCRIPTIONS[key])
        for key in monitored
        if key in CURRENT_SENSOR_DESCRIPTIONS
    ]
    for index in hourly_indices:
        entities.extend(
            BrightSkyForecastSensor(coordinator, "hourly", int(index), key)
            for key in FORECAST_SENSOR_FIELDS
        )
    for index in daily_indices:
        entities.extend(
            BrightSkyForecastSensor(coordinator, "daily", int(index), key)
            for key in FORECAST_SENSOR_FIELDS
            if key != "source_id"
        )
    async_add_entities(entities)


class BrightSkyCurrentSensor(BrightSkyEntity, SensorEntity):
    entity_description: BrightSkySensorDescription

    def __init__(
        self,
        coordinator: BrightSkyCoordinator,
        description: BrightSkySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator)


class BrightSkyForecastSensor(BrightSkyEntity, SensorEntity):
    def __init__(
        self,
        coordinator: BrightSkyCoordinator,
        forecast_type: str,
        index: int,
        field: str,
    ) -> None:
        super().__init__(coordinator)
        unit, device_class = FORECAST_SENSOR_FIELDS[field]
        self.forecast_type = forecast_type
        self.index = index
        self.field = field
        self.entity_description = SensorEntityDescription(
            key=f"{forecast_type}_{index}_{field}",
            name=forecast_sensor_name(forecast_type, index, field),
            translation_key=f"{forecast_type}_{field}",
            native_unit_of_measurement=unit,
            device_class=device_class,
            state_class=SensorStateClass.MEASUREMENT if unit else None,
        )
        self._attr_unique_id = f"{self._entry.entry_id}_{forecast_type}_{index}_{field}"

    @property
    def native_value(self) -> Any:
        record = self._record()
        if record is None:
            return None
        return record.get(self.field)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        record = self._record()
        if record is None:
            return None
        return {
            "forecast_type": self.forecast_type,
            "forecast_index": self.index,
            "datetime": record.get("timestamp") or record.get("datetime"),
            "condition": record.get("condition"),
            "fallback_source_ids": record.get("fallback_source_ids", {}),
        }

    def _record(self) -> dict[str, Any] | None:
        records = (
            self.coordinator.data.hourly_records
            if self.forecast_type == "hourly"
            else self.coordinator.data.daily_forecast
        )
        if self.index >= len(records):
            return None
        return records[self.index]
