import logging
from bleak import BleakClient
from bleak_retry_connector import establish_connection

from .const import WRITE_UUID

_LOGGER = logging.getLogger(__name__)


def build_packet(port: int, state: int):
    # inferred working structure
    return bytearray([0xA5, port, state, 0x00])


async def send_command(mac: str, port: int, state: int):
    try:
        client = await establish_connection(BleakClient, mac, "AC Infinity")

        packet = build_packet(port, state)

        await client.write_gatt_char(WRITE_UUID, packet)

        await client.disconnect()

    except Exception as err:
        _LOGGER.error("BLE command failed: %s", err)
