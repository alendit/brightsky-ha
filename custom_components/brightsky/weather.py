from __future__ import annotations

from typing import Any, cast

from homeassistant.components.weather import Forecast, WeatherEntity
from homeassistant.components.weather.const import WeatherEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CREATE_WEATHER
from .entity import BrightSkyEntity
from .mappers import map_brightsky_condition


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    if not entry.options.get(
        CONF_CREATE_WEATHER, entry.data.get(CONF_CREATE_WEATHER, True)
    ):
        return
    async_add_entities([BrightSkyWeatherEntity(entry.runtime_data)])


class BrightSkyWeatherEntity(BrightSkyEntity, WeatherEntity):
    _attr_name = None
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.METERS
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(self, coordinator: Any) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._entry.entry_id}_weather"

    @property
    def condition(self) -> str | None:
        return map_brightsky_condition(self.coordinator.data.current)

    @property
    def native_temperature(self) -> float | None:
        return self.coordinator.data.current.get("temperature")

    @property
    def native_dew_point(self) -> float | None:
        return self.coordinator.data.current.get("dew_point")

    @property
    def native_pressure(self) -> float | None:
        return self.coordinator.data.current.get("pressure_msl")

    @property
    def humidity(self) -> float | None:
        return self.coordinator.data.current.get("relative_humidity")

    @property
    def cloud_coverage(self) -> float | None:
        return self.coordinator.data.current.get("cloud_cover")

    @property
    def native_visibility(self) -> float | None:
        return self.coordinator.data.current.get("visibility")

    @property
    def wind_bearing(self) -> float | str | None:
        return (
            self.coordinator.data.current.get("wind_direction_60")
            or self.coordinator.data.current.get("wind_direction")
            or self.coordinator.data.current.get("wind_direction_30")
            or self.coordinator.data.current.get("wind_direction_10")
        )

    @property
    def native_wind_speed(self) -> float | None:
        return (
            self.coordinator.data.current.get("wind_speed_60")
            or self.coordinator.data.current.get("wind_speed")
            or self.coordinator.data.current.get("wind_speed_30")
            or self.coordinator.data.current.get("wind_speed_10")
        )

    @property
    def native_wind_gust_speed(self) -> float | None:
        return (
            self.coordinator.data.current.get("wind_gust_speed_60")
            or self.coordinator.data.current.get("wind_gust_speed")
            or self.coordinator.data.current.get("wind_gust_speed_30")
            or self.coordinator.data.current.get("wind_gust_speed_10")
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        source = data.primary_source or {}
        return {
            "source_id": data.current.get("source_id"),
            "station_name": source.get("station_name"),
            "dwd_station_id": source.get("dwd_station_id"),
            "wmo_station_id": source.get("wmo_station_id"),
            "fallback_source_ids": data.current.get("fallback_source_ids", {}),
        }

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        return cast(list[Forecast], self.coordinator.data.hourly_forecast)

    async def async_forecast_daily(self) -> list[Forecast] | None:
        return cast(list[Forecast], self.coordinator.data.daily_forecast)
