
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, MANUFACTURER_ID

_LOGGER = logging.getLogger(__name__)


class ACInfinityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    # --------------------------------------------------
    # Bluetooth discovery (automatic)
    # --------------------------------------------------

    async def async_step_bluetooth(self, discovery_info):
        address = discovery_info.address
        name = discovery_info.name or "AC Infinity"

        manufacturer = (
            discovery_info.advertisement.manufacturer_data or {}
        )

        if MANUFACTURER_ID not in manufacturer:
            return self.async_abort(reason="not_ac_infinity")

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        _LOGGER.debug("Discovered AC Infinity device %s", address)

        return self.async_create_entry(
            title=f"{name} {address}",
            data={CONF_ADDRESS: address},
        )

    # --------------------------------------------------
    # Manual fallback entry
    # --------------------------------------------------

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            address = user_input[CONF_ADDRESS]

            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"AC Infinity {address}",
                data={CONF_ADDRESS: address},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ADDRESS): str}
            ),
        )
