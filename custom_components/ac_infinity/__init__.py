from __future__ import annotations

import logging
from datetime import timedelta

from bleak import BleakClient
from bleak_retry_connector import establish_connection

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_INTERVAL, NOTIFY_UUID

_LOGGER = logging.getLogger(__name__)


class ACInfinityCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, mac, name):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

        self.mac = mac
        self.name = name
        self.client = None
        self._notifying = False

        self.data = {
            "temperature": None,
            "humidity": None,
            "ports": {i: False for i in range(1, 9)},
        }

    async def _ensure_connected(self):
        if self.client and self.client.is_connected:
            return

        self.client = await establish_connection(
            BleakClient,
            self.mac,
            self.name,
        )

        if not self._notifying:
            await self.client.start_notify(NOTIFY_UUID, self._handle_notify)
            self._notifying = True

    async def _async_update_data(self):
        try:
            await self._ensure_connected()
            return self.data
        except Exception as err:
            raise UpdateFailed(err) from err

    def _handle_notify(self, sender, data: bytearray):
        try:
            if not data or data[0] != 0xA5:
                return

            temp = data[6]
            humidity = data[7]

            if 0 < temp < 150:
                self.data["temperature"] = temp

            if 0 <= humidity <= 100:
                self.data["humidity"] = humidity

            bitmask = data[10]

            for i in range(8):
                self.data["ports"][i + 1] = bool(bitmask & (1 << i))

            self.async_set_updated_data(self.data)

        except Exception as err:
            _LOGGER.error("Parse error: %s", err)
