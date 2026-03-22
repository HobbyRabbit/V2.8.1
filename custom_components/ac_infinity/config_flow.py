import logging

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ACInfinityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle AC Infinity config flow."""

    VERSION = 1

    async def async_step_bluetooth(self, discovery_info):
        """Handle Bluetooth discovery."""

        address = discovery_info.address

        _LOGGER.debug("Discovered AC Infinity device: %s", address)

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"AC Infinity {address}",
            data={"mac": address},
        )
