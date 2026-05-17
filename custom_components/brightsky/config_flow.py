from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BrightSkyApiError, BrightSkyClient
from .const import (
    CONF_CREATE_SENSORS,
    CONF_CREATE_WEATHER,
    CONF_DAILY_SENSOR_INDICES,
    CONF_FORECAST_DAYS,
    CONF_HOURLY_SENSOR_INDICES,
    CONF_MAX_DISTANCE,
    CONF_MONITORED_CONDITIONS,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_DAILY_SENSOR_INDICES,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_HOURLY_SENSOR_INDICES,
    DEFAULT_MONITORED_CONDITIONS,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DOMAIN,
    MIN_UPDATE_INTERVAL_SECONDS,
)
from .sensor import CURRENT_SENSOR_DESCRIPTIONS


def _parse_indices(value: Any) -> list[int]:
    if isinstance(value, list):
        return [int(item) for item in value]
    if value is None or value == "":
        return []
    return [int(part.strip()) for part in str(value).split(",") if part.strip()]


def _indices_to_text(value: Any) -> str:
    return ",".join(str(item) for item in _parse_indices(value))


def _base_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Required(
                CONF_LATITUDE, default=defaults.get(CONF_LATITUDE)
            ): cv.latitude,
            vol.Required(
                CONF_LONGITUDE, default=defaults.get(CONF_LONGITUDE)
            ): cv.longitude,
            vol.Optional(
                CONF_TIMEZONE,
                default=defaults.get(CONF_TIMEZONE, "Europe/Berlin"),
            ): str,
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=defaults.get(
                    CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_SECONDS
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL_SECONDS)),
            vol.Optional(
                CONF_MAX_DISTANCE, default=defaults.get(CONF_MAX_DISTANCE)
            ): vol.Any(None, vol.All(vol.Coerce(int), vol.Range(min=0, max=500000))),
            vol.Optional(
                CONF_FORECAST_DAYS,
                default=defaults.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            vol.Optional(
                CONF_CREATE_WEATHER,
                default=defaults.get(CONF_CREATE_WEATHER, True),
            ): bool,
            vol.Optional(
                CONF_CREATE_SENSORS,
                default=defaults.get(CONF_CREATE_SENSORS, True),
            ): bool,
        }
    )


def _options_schema(defaults: dict[str, Any]) -> vol.Schema:
    return _base_schema(defaults).extend(
        {
            vol.Optional(
                CONF_MONITORED_CONDITIONS,
                default=defaults.get(
                    CONF_MONITORED_CONDITIONS, DEFAULT_MONITORED_CONDITIONS
                ),
            ): cv.multi_select(
                {
                    key: key.replace("_", " ").title()
                    for key in CURRENT_SENSOR_DESCRIPTIONS
                }
            ),
            vol.Optional(
                CONF_HOURLY_SENSOR_INDICES,
                default=_indices_to_text(
                    defaults.get(
                        CONF_HOURLY_SENSOR_INDICES, DEFAULT_HOURLY_SENSOR_INDICES
                    )
                ),
            ): str,
            vol.Optional(
                CONF_DAILY_SENSOR_INDICES,
                default=_indices_to_text(
                    defaults.get(
                        CONF_DAILY_SENSOR_INDICES, DEFAULT_DAILY_SENSOR_INDICES
                    )
                ),
            ): str,
        }
    )


async def _validate_input(hass: Any, data: dict[str, Any]) -> None:
    client = BrightSkyClient(async_get_clientsession(hass))
    await client.fetch_current_weather(
        latitude=float(data[CONF_LATITUDE]),
        longitude=float(data[CONF_LONGITUDE]),
        timezone=str(data[CONF_TIMEZONE]),
        max_distance=data.get(CONF_MAX_DISTANCE),
    )


class BrightSkyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return BrightSkyOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        defaults = {
            CONF_NAME: DEFAULT_NAME,
            CONF_LATITUDE: self.hass.config.latitude,
            CONF_LONGITUDE: self.hass.config.longitude,
            CONF_TIMEZONE: self.hass.config.time_zone,
        }

        if user_input is not None:
            unique_id = (
                f"{float(user_input[CONF_LATITUDE]):.5f},"
                f"{float(user_input[CONF_LONGITUDE]):.5f}"
            )
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            try:
                await _validate_input(self.hass, user_input)
            except BrightSkyApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=str(user_input[CONF_NAME]),
                    data={
                        **user_input,
                        CONF_MONITORED_CONDITIONS: DEFAULT_MONITORED_CONDITIONS,
                        CONF_HOURLY_SENSOR_INDICES: DEFAULT_HOURLY_SENSOR_INDICES,
                        CONF_DAILY_SENSOR_INDICES: DEFAULT_DAILY_SENSOR_INDICES,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(defaults),
            errors=errors,
        )


class BrightSkyOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        defaults = {**self._config_entry.data, **self._config_entry.options}

        if user_input is not None:
            try:
                await _validate_input(self.hass, user_input)
                user_input[CONF_HOURLY_SENSOR_INDICES] = _parse_indices(
                    user_input.get(CONF_HOURLY_SENSOR_INDICES)
                )
                user_input[CONF_DAILY_SENSOR_INDICES] = _parse_indices(
                    user_input.get(CONF_DAILY_SENSOR_INDICES)
                )
            except BrightSkyApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(defaults),
            errors=errors,
        )
