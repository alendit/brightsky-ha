from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BrightSkyCoordinator


class BrightSkyEntity(CoordinatorEntity[BrightSkyCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: BrightSkyCoordinator) -> None:
        super().__init__(coordinator)
        self._entry = coordinator.entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Bright Sky",
            configuration_url="https://brightsky.dev/",
        )

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None
