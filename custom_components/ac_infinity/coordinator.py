"""AC Infinity BLE Coordinator V6.5 (Stable)."""

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

UPDATE_INTERVAL = timedelta(seconds=10)

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"


class ACInfinityCoordinator(DataUpdateCoordinator):
    """AC Infinity BLE data coordinator."""

    def __init__(self, hass, mac: str, name: str):
        """Initialize."""
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

        # Data model (clean + consistent)
        self.data = {
            "temperature": None,
            "humidity": None,
            "ports": {i: False for i in range(1, 9)},
        }

    async def _ensure_connected(self):
        """Ensure BLE connection (HA safe)."""
        try:
            if self.client and self.client.is_connected:
                return

            _LOGGER.debug("Connecting to %s", self.mac)

            self.client = await establish_connection(
                BleakClient,
                self.mac,
                self.name,
            )

            # Start notify only once
            if not self._notifying:
                await self.client.start_notify(
                    NOTIFY_UUID,
                    self._handle_notification,
                )
                self._notifying = True

            _LOGGER.debug("Connected + notifications started")

        except Exception as err:
            # 🔧 Fix for 'str has no attribute details'
            if isinstance(err, str):
                raise UpdateFailed(f"BLE connect failed: {err}")
            raise UpdateFailed("BLE connect failed") from err

    async def _async_update_data(self):
        """Fetch latest data."""
        try:
            await self._ensure_connected()
            return self.data
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err

    def _handle_notification(self, sender: int, data: bytearray):
        """Parse BLE packets."""
        try:
            if len(data) < 16:
                return

            # Packet signature check
            if data[0:5] != b"JGQUA":
                return

            # ---------------------------
            # Temperature (F)
            # ---------------------------
            temp_raw = (data[9] << 8) | data[10]
            temperature = round(temp_raw / 36, 1)

            # ---------------------------
            # Humidity (%)
            # ---------------------------
            humidity_raw = data[11]
            humidity = int(humidity_raw / 3)

            # Update only if valid
            if 0 < temperature < 150:
                self.data["temperature"] = temperature

            if 0 <= humidity <= 100:
                self.data["humidity"] = humidity

            # ---------------------------
            # Port updates
            # ---------------------------
            port = data[13]
            state = data[15]

            if 1 <= port <= 8:
                self.data["ports"][port] = bool(state)

            _LOGGER.debug(
                "Packet | Temp=%sF Hum=%s%% Port=%s State=%s Raw=%s",
                self.data["temperature"],
                self.data["humidity"],
                port,
                state,
                data.hex(),
            )

        except Exception as err:
            _LOGGER.error("Packet parse error: %s", err)
