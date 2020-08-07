"""
Tanner Songkakul

CustomPeripheralGUI.py

Uses bleak and PyQT to connect to a CC2642 Launchpad running Custom Peripheral
and plot data on each characteristics.

Requires bleak, pyqt, qasync and included customperipheral library
"""

from PyQt5 import QtWidgets
import sys
import asyncio
from qasync import QEventLoop
import customperipheral as cplib
from bleak import BleakClient
from bleak import discover

# GLOBALS
#TODO: find a better way to use this with the notification handler without using as global
cp = cplib.CustomPeripheral()

def notification_handler(sender, data):
    """Handle incoming packets."""
    cp.datacount = cp.datacount + 1
    char = cp.parse_data(sender, data)


async def plot_handler(cp, win):
    """Asynchronously update the plot each second """
    while 1: # TODO: remove loop here to allow disconnect/reconnect
        win.plot_all(cp.ALL_DATA)
        await asyncio.sleep(1)


async def button_wait(win):
    """Polling for button press"""
    while not win.connect_button:  # wait for button press flag to be set in GUI
        await asyncio.sleep(.01)
    win.button_ack() # clear button press flag


async def find_device(win, cp):
    """Search for device after button press"""
    await button_wait(win)  # Wait for button press
    win.display_status("Scanning...")
    devices = await discover()  # Discover devices on BLE
    cp.set_name(win.device_name) # Get device name from text input window in GUI
    device_found = cp.get_address(devices) #  Check if device in list
    return device_found


async def enable_notif(cp, client):
    """Start notifications on all characteristics"""
    for char in cp.CHAR_LIST:
        await client.start_notify(char, notification_handler)
    #print("Notifications enabled")


async def disable_notif(cp, client):
    """Stop notifications on all characteristics"""
    for char in cp.CHAR_LIST:
        await client.stop_notify(char, notification_handler)


async def run(win, cp, loop):
    """Main asyncio loop"""
    while 1: # TODO replace this loop to allow for disconnect/reconnect
        # while not cp.CONNECTED:
        dev_found = await find_device(win, cp) # Find device address
        if dev_found:
            win.display_status("Device {} found! Connecting...".format(cp.NAME))
            async with BleakClient(cp.ADDR, loop=loop) as client:
                x = await client.is_connected() # Attempt device connection TODO add error messages
                win.display_status("Connected!")
                await enable_notif(cp, client)
                await plot_handler(cp, win)
                await disable_notif(cp, client)
        else:
            win.display_status("ERROR: Device not found.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  # NEW must set the event loop

    win = cplib.MainWindow()
    win.show()

    with loop:  ## context manager calls .close() when loop completes, and releases all resources
        loop.run_until_complete(run(win, cp, loop))


if __name__ == '__main__':
    main()
