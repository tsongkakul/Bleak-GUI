# -*- coding: utf-8 -*-
"""
Tanner Songkakul

CustomPeripheralPlot.py

Uses bleak and pyqtgraph to connect to a CC2642 Launchpad running Custom Peripheral
and plot data on each characteristics.

Requires bleak, pyqtgraph and included customperipheral library
"""

import asyncio
from bleak import BleakClient
from bleak import discover
import customperipheral as CPLib
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg

# User Settings
name = "CP001"  # <--- Change to your device's shortened Advertising Name here
window_length = 100  # Length of rolling windows.

# Globals
# Set up Custom Peripheral object
CP = CPLib.CustomPeripheral()
CP.set_name(name)

# Set up plot widget
app = QtGui.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Custom Peripheral")
CP_plot = CPLib.CPPlot(app, win, window_length)

def notification_handler(sender, data):
    """Simple notification handler which parses received data and plots it"""
    # BUG: drops packets on characteristics when server sends on all 5 channels simultaneously
    char = CP.parse_data(sender, data)
    CP_plot.plot_char(char, int(data[0]))


async def enable_notif(CP, client):
    """Start notifications on all characteristics"""
    await client.start_notify(CP.CHAR1, notification_handler)
    await client.start_notify(CP.CHAR2, notification_handler)
    await client.start_notify(CP.CHAR3, notification_handler)
    await client.start_notify(CP.CHAR4, notification_handler)
    await client.start_notify(CP.CHAR5, notification_handler)
    await plot_handler()


async def plot_handler():
    """Asynchronously update the plot each second """
    while 1:
        CP_plot.update()
        await asyncio.sleep(1)


async def disable_notif(CP, client):
    """Stop notifications on all characteristics"""
    await client.stop_notify(CP.CHAR1)
    await client.stop_notify(CP.CHAR2)
    await client.stop_notify(CP.CHAR3)
    await client.stop_notify(CP.CHAR4)
    await client.stop_notify(CP.CHAR5)


async def run(address, loop, debug=False):
    """Main asyncio loop"""
    devices = await discover() # discover BLE devices
    device_found = CP.get_address(devices) # search device names to get the
    if device_found:
        async with BleakClient(CP.ADDR, loop=loop) as client:
            x = await client.is_connected()  # connect to device
            print("Connected: {0}".format(x))
            # await client.write_gatt_char(CP.SYSCFG, bytes.fromhex(cfg_string)) # uncomment to write data to device
            await enable_notif(CP, client) # enable notifications
            await asyncio.sleep(1000.0, loop=loop) # TODO make sure this doesn't cause a timeout
            await disable_notif(CP, client) # disable notifications
    else:
        print("ERROR: Device not found.")


if __name__ == "__main__":
    import os
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(CP, loop, False))
