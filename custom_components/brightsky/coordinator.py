from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import BrightSkyApiError, BrightSkyClient
from .const import (
    CONF_FORECAST_DAYS,
    CONF_MAX_DISTANCE,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DOMAIN,
)
from .mappers import aggregate_daily_forecast, map_hourly_forecast
from .models import BrightSkyData

_LOGGER = logging.getLogger(__name__)


class BrightSkyCoordinator(DataUpdateCoordinator[BrightSkyData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = BrightSkyClient(async_get_clientsession(hass))
        update_interval = int(
            entry.options.get(
                CONF_UPDATE_INTERVAL,
                entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_SECONDS),
            )
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> BrightSkyData:
        latitude = float(self.entry.data["latitude"])
        longitude = float(self.entry.data["longitude"])
        timezone = str(
            self.entry.options.get(
                CONF_TIMEZONE,
                self.entry.data.get(CONF_TIMEZONE, self.hass.config.time_zone),
            )
        )
        max_distance = self.entry.options.get(
            CONF_MAX_DISTANCE, self.entry.data.get(CONF_MAX_DISTANCE)
        )
        forecast_days = int(
            self.entry.options.get(
                CONF_FORECAST_DAYS,
                self.entry.data.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS),
            )
        )

        now = dt_util.now().replace(minute=0, second=0, microsecond=0)
        end = now + timedelta(days=forecast_days)

        try:
            current_payload = await self.client.fetch_current_weather(
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                max_distance=max_distance,
            )
            weather_payload = await self.client.fetch_weather(
                latitude=latitude,
                longitude=longitude,
                start=now.isoformat(),
                end=end.isoformat(),
                timezone=timezone,
                max_distance=max_distance,
            )
        except BrightSkyApiError as err:
            raise UpdateFailed(str(err)) from err

        hourly_records = weather_payload.get("weather") or []
        if not isinstance(hourly_records, list):
            raise UpdateFailed("Bright Sky weather payload did not include a list")

        current = current_payload.get("weather") or {}
        if not isinstance(current, dict):
            raise UpdateFailed(
                "Bright Sky current weather payload did not include an object"
            )

        current_sources = current_payload.get("sources") or []
        forecast_sources = weather_payload.get("sources") or []
        return BrightSkyData(
            current=current,
            current_sources=(
                current_sources if isinstance(current_sources, list) else []
            ),
            hourly_records=hourly_records,
            forecast_sources=(
                forecast_sources if isinstance(forecast_sources, list) else []
            ),
            hourly_forecast=[map_hourly_forecast(record) for record in hourly_records],
            daily_forecast=aggregate_daily_forecast(hourly_records),
        )
