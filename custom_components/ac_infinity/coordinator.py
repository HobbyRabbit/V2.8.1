"""AC Infinity BLE Coordinator V6.5 (Stable)."""

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .bluetooth import async_get_device_data
from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ACInfinityCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, address, name):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.mac = address
        self.name = name

    async def _async_update_data(self):
        data = async_get_device_data(self.hass, self.mac)

        if not data:
            raise UpdateFailed("No BLE advertisement data")

        return data
