from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        ACInfinityTempSensor(coordinator),
        ACInfinityHumiditySensor(coordinator),
    ]

    async_add_entities(entities)


class BaseSensor(SensorEntity):
    def __init__(self, coordinator, key, name):
        self.coordinator = coordinator
        self._key = key
        self._attr_name = f"{coordinator.name} {name}"
        self._attr_unique_id = f"{coordinator.mac}_{key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class ACInfinityTempSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "temperature", "Temperature")
        self._attr_native_unit_of_measurement = "°F"


class ACInfinityHumiditySensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "humidity", "Humidity")
        self._attr_native_unit_of_measurement = "%"
