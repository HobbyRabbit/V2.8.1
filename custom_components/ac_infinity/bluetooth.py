from homeassistant.components import bluetooth
from .const import MANUFACTURER_ID


def parse_manufacturer(data: bytes):
    if len(data) < 6:
        return None

    temp_f = data[0]
    humidity = data[1]

    ports = data[2]

    return {
        "temperature": temp_f,
        "humidity": humidity,
        "ports": ports
    }


def async_get_device_data(hass, address):
    service_info = bluetooth.async_last_service_info(hass, address)

    if not service_info:
        return None

    mfg_data = service_info.manufacturer_data.get(MANUFACTURER_ID)

    if not mfg_data:
        return None

    return parse_manufacturer(mfg_data)
