# -*- coding: utf-8 -*-
"""
Notifications
-------------
Example showing how to add notifications to a characteristic and handle the responses.
Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>
"""

import asyncio

from bleak import BleakClient

i = 0
SYSCFG_UUID = "f000abcd-0451-4000-b000-000000000000"
CHAR1_UUID = "f00062d2-0451-4000-b000-000000000000"
CHAR2_UUID = "f00044dc-0451-4000-b000-000000000000"
CHAR3_UUID = "f0003c36-0451-4000-b000-000000000000"
CHAR4_UUID = "f0003a36-0451-4000-b000-000000000000"
CHAR5_UUID = "f00030d8-0451-4000-b000-000000000000"

# initialize plot here
# initialize variables here

def notification_handler(sender, data):
    global i
    """Simple notification handler which prints the data received."""

    # process data into buffer
    #
    print("{0}: {1}".format(sender, data))


async def run(address, loop, debug=False):
    async with BleakClient(address, loop=loop) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        #await client.write_gatt_char(SYSCFG_UUID, bytes.fromhex(cfg_string))

        await client.start_notify(CHAR1_UUID, notification_handler)
        await client.start_notify(CHAR2_UUID, notification_handler)
        await client.start_notify(CHAR3_UUID, notification_handler)
        await client.start_notify(CHAR4_UUID, notification_handler)
        await client.start_notify(CHAR5_UUID, notification_handler)
        await asyncio.sleep(1000.0, loop=loop)
        await client.stop_notify(CHAR1_UUID)
        await client.stop_notify(CHAR2_UUID)
        await client.stop_notify(CHAR3_UUID)
        await client.stop_notify(CHAR4_UUID)
        await client.stop_notify(CHAR5_UUID)

if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    address = (
        "04:EE:03:9B:7A:8E"  # <--- Change to your device's address here if you are using Windows or Linux
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, loop, False))
