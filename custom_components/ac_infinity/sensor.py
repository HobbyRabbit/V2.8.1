from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        TempSensor(coordinator),
        HumiditySensor(coordinator),
    ])


class BaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{coordinator.name} {name}"
        self._attr_unique_id = f"{coordinator.mac}_{key}"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)


class TempSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "temperature", "Temperature", "°F")


class HumiditySensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "humidity", "Humidity", "%")
