"""AC Infinity coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from bleak import BleakClient

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=10)

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"


class ACInfinityCoordinator(DataUpdateCoordinator):
    """Coordinator for AC Infinity controller."""

    def __init__(self, hass, mac):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

        self.mac = mac
        self.client = BleakClient(mac)

        self.data = {
            "temperature": None,
            "humidity": None,
            "ports": {i: False for i in range(1, 9)},
        }

    async def _async_update_data(self):
        """Fetch BLE data."""

        try:
            if not self.client.is_connected:
                await self.client.connect()

            await self.client.start_notify(
                NOTIFY_UUID,
                self._handle_notification,
            )

        except Exception as err:
            raise UpdateFailed(f"BLE error: {err}") from err

        return self.data

    def _handle_notification(self, sender, data):
        """Parse BLE packet."""

        try:
            if len(data) < 20:
                return

            # HEADER CHECK
            if data[0:5] != b"JGQUA":
                return

            # ---- temperature decode (V2.5 method)
            temp_raw = (data[9] << 8) | data[10]
            temperature = round(temp_raw / 36, 1)

            # ---- humidity decode (V2.5 method)
            humidity_raw = data[11]
            humidity = int(humidity_raw / 3)

            self.data["temperature"] = temperature
            self.data["humidity"] = humidity

            # ---- port state (V2.4 structure)
            port = data[13]
            state = data[15]

            if 1 <= port <= 8:
                self.data["ports"][port] = bool(state)

            _LOGGER.debug(
                "Packet decoded: temp=%s humidity=%s port=%s state=%s",
                temperature,
                humidity,
                port,
                state,
            )

        except Exception as err:
            _LOGGER.error("Packet parse error: %s", err)
