# -*- coding: utf-8 -*-
"""

"""

import asyncio
from bleak import BleakClient
from bleak import discover
import CustomPeripheral as CPLib
from pyqtgraph.Qt import QtGui

import pyqtgraph as pg

# User Settings
name = "CP001"  # <--- Change to your device's shortened Advertising Name here
window_length = 100  # Length of rolling windows.

# Globals
CP = CPLib.CustomPeripheral()
CP.set_name(name)
app = QtGui.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Custom Peripheral")
CP_plot = CPLib.CPPlot(app, win, window_length)

def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    # process data into buffers
    CP.datacount = CP.datacount + 1
    char = CP.parse_data(sender, data)
    CP_plot.plot_char(char, int(data[0]))


async def enable_notif(CP, client):
    await client.start_notify(CP.CHAR1, notification_handler)
    await client.start_notify(CP.CHAR2, notification_handler)
    await client.start_notify(CP.CHAR3, notification_handler)
    await client.start_notify(CP.CHAR4, notification_handler)
    await client.start_notify(CP.CHAR5, notification_handler)
    await plot_handler()


async def plot_handler():
    while 1:
        CP_plot.update()
        await asyncio.sleep(1)


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
            await enable_notif(CP, client)
            await asyncio.sleep(1000.0, loop=loop)
            await disable_notif(CP, client)
    else:
        print("ERROR: No device found.")


if __name__ == "__main__":
    import os

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(CP, loop, False))
