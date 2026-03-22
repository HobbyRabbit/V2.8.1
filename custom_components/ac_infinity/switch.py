from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PORTS


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        PortSwitch(coordinator, port)
        for port in PORTS
    ]

    async_add_entities(entities)


class PortSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, port):
        super().__init__(coordinator)
        self.port = port
        self._attr_name = f"{coordinator.name} Port {port}"
        self._attr_unique_id = f"{coordinator.mac}_port_{port}"

    @property
    def is_on(self):
        return self.coordinator.data["ports"].get(self.port, False)

    async def async_turn_on(self):
        # control added later (matches V2.5 separation)
        pass

    async def async_turn_off(self):
        pass
