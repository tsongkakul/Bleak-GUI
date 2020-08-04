# -*- coding: utf-8 -*-
"""
Notifications
-------------
Example showing how to add notifications to a characteristic and handle the responses.
Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>
"""

import asyncio
from bleak import BleakClient
from bleak import discover
import CustomPeripheral as CPLib

name = "CP001"  # <--- Change to your device's shortened Advertising Name here
CP = CPLib.CustomPeripheral(name)

# initialize plot here
# initialize variables here
i = 0

def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    # process data into buffers
    CP.parse_data(sender, data)





async def enable_notif(CP, client):
    # await client.start_notify(CP.CHAR1, notification_handler)
    # await client.start_notify(CP.CHAR2, notification_handler)
    # await client.start_notify(CP.CHAR3, notification_handler)
    # await client.start_notify(CP.CHAR4, notification_handler)
    await client.start_notify(CP.CHAR5, notification_handler)


async def disable_notif(CP, client):
    await client.stop_notify(CP.CHAR1)
    await client.stop_notify(CP.CHAR2)
    await client.stop_notify(CP.CHAR3)
    await client.stop_notify(CP.CHAR4)
    await client.stop_notify(CP.CHAR5)


async def run(address, loop, debug=False):
    devices = await discover()
    device_found = CP.get_address(devices)
    if device_found:
        async with BleakClient(CP.ADDR, loop=loop) as client:
            x = await client.is_connected()
            print("Connected: {0}".format(x))

            # await client.write_gatt_char(SYSCFG_UUID, bytes.fromhex(cfg_string))

            # await client.start_notify(HET2.CHAR1, notification_handler)
            # await client.start_notify(HET2.CHAR2, notification_handler)
            # await client.start_notify(HET2.CHAR3, notification_handler)
            # await client.start_notify(HET2.CHAR4, notification_handler)
            # await client.start_notify(HET2.CHAR5, notification_handler)

            await enable_notif(CP, client)
            await asyncio.sleep(1000.0, loop=loop)
            await disable_notif(CP,client)
    else:
        print("ERROR: No device found.")

if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(CP, loop, False))
