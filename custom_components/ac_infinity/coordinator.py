"""AC Infinity Coordinator V7.2 (V2.5 aligned)."""

from __future__ import annotations

import logging
from datetime import timedelta

from bleak import BleakClient
from bleak_retry_connector import establish_connection

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=5)

SERVICE_UUID = "70d51000-2c7f-4e75-ae8a-d758951ce4e0"
WRITE_UUID   = "70d51001-2c7f-4e75-ae8a-d758951ce4e0"
NOTIFY_UUID  = "70d51002-2c7f-4e75-ae8a-d758951ce4e0"


class ACInfinityCoordinator(DataUpdateCoordinator):
    """AC Infinity coordinator (V2.5 aligned)."""

    def __init__(self, hass, mac: str, name: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=UPDATE_INTERVAL,
        )

        self.mac = mac
        self.name = name

        self.client: BleakClient | None = None
        self._notifying = False

        # 🔥 EXACT structure expected by sensor/switch platforms
        self.data = {
            "temperature": None,
            "humidity": None,
            "ports": {i: False for i in range(1, 9)},
        }

    async def _ensure_connected(self):
        """Ensure BLE connection."""
        if self.client and self.client.is_connected:
            return

        _LOGGER.debug("Connecting to %s", self.mac)

        self.client = await establish_connection(
            BleakClient,
            self.mac,
            self.name,
        )

        if not self._notifying:
            await self.client.start_notify(
                NOTIFY_UUID,
                self._handle_notify,
            )
            self._notifying = True

            _LOGGER.debug("Notifications started")

    async def _async_update_data(self):
        """Update data from BLE."""
        try:
            await self._ensure_connected()

            # 🔥 IMPORTANT: return existing data, do NOT overwrite
            return self.data

        except Exception as err:
            raise UpdateFailed(f"BLE update failed: {err}") from err

    def _handle_notify(self, sender, data: bytearray):
        """Handle incoming BLE packets."""
        try:
            if not data or data[0] != 0xA5:
                return

            # ---------------------------
            # ENVIRONMENT DATA
            # ---------------------------
            temp = data[6]
            humidity = data[7]

            # sanity filter
            if 0 < temp < 150:
                self.data["temperature"] = temp

            if 0 <= humidity <= 100:
                self.data["humidity"] = humidity

            # ---------------------------
            # PORT BITMASK (V2.5 behavior)
            # ---------------------------
            port_bits = data[10]

            for i in range(8):
                self.data["ports"][i + 1] = bool(port_bits & (1 << i))

            _LOGGER.debug(
                "Decoded | T=%s H=%s Ports=%s Raw=%s",
                self.data["temperature"],
                self.data["humidity"],
                self.data["ports"],
                data.hex(),
            )

            # 🔥 CRITICAL: push update to HA
            self.async_set_updated_data(self.data)

        except Exception as err:
            _LOGGER.error("Parse error: %s", err)
