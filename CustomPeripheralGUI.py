from PyQt5 import QtWidgets
import sys
import asyncio
from qasync import QEventLoop
import customperipheral as cplib
from bleak import BleakClient
from bleak import discover

# GLOBALS
cp = cplib.CustomPeripheral()

def notification_handler(sender, data):
    # process data into buffers
    cp.datacount = cp.datacount + 1
    char = cp.parse_data(sender, data)


async def plot_handler(cp, win):
    while 1:
        win.plot_all(cp.ALL_DATA)
        await asyncio.sleep(0.5)


async def button_wait(win):
    while not win.connect_button:  # wait for button press
        await asyncio.sleep(.01)
    win.button_ack()


async def find_device(win, cp):
    await button_wait(win)
    win.display_status("Scanning...")
    devices = await discover()
    cp.set_name(win.device_name)
    device_found = cp.get_address(devices)
    return device_found


async def enable_notif(cp, client):
    for char in cp.CHAR_LIST:
        await client.start_notify(char, notification_handler)
    print("Notifications enabled")


async def disable_notif(cp, client):
    for char in cp.CHAR_LIST:
        await client.stop_notify(char, notification_handler)


async def run(win, cp, loop):
    while 1:
        # while not cp.CONNECTED:
        dev_found = await find_device(win, cp)
        if dev_found:
            win.display_status("Device {} found! Connecting...".format(cp.NAME))
            async with BleakClient(cp.ADDR, loop=loop) as client:
                x = await client.is_connected()
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
