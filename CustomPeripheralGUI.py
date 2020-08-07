from PyQt5 import QtWidgets, uic
import sys
import asyncio
from qasync import QEventLoop, QThreadExecutor
import CustomPeripheral as CPLib
from bleak import BleakClient
from bleak import discover

# GLOBALS
cp = CPLib.CustomPeripheral()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        self.plot_data = []
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        uic.loadUi('Basic_CP_GUI.ui', self)
        self.connectButton.clicked.connect(self.get_device)
        self.actionQuit.triggered.connect(self.close)
        self.connect_button = 0
        self.device_name = "None"

    def plot(self, data):
        self.plot_data.append(data)
        self.plotWidget.plot(self.plot_data)

    def plot_all(self, plot_list):
        for i, data in enumerate(plot_list):
            self.plotWidget.plot(data, pen=(i, len(plot_list)))

    def get_device(self):
        # print("Button pressed. Text box says {}".format(self.deviceEntry.text()))
        self.connect_button = 1
        self.device_name = self.deviceEntry.text()

    def button_ack(self):
        self.connect_button = 0

    def display_status(self, msg):
        self.statusDisp.setText(msg)

def notification_handler(sender, data):
    # process data into buffers
    cp.datacount = cp.datacount + 1
    char = cp.parse_data(sender, data)

async def plot_handler(cp, win):
    while 1:
        win.plot_all(cp.ALL_DATA)
        await asyncio.sleep(1)


async def enable_notif(cp, client):
    for char in cp.CHAR_LIST:
        await client.start_notify(char, notification_handler)
    print("Notifications enabled")


async def disable_notif(cp, client):
    for char in cp.CHAR_LIST:
        await client.stop_notify(char, notification_handler)

async def run(win, cp, loop):
    while 1:
    #while not cp.CONNECTED:
        dev_found = await find_device(win, cp)
        if dev_found:
            win.display_status("Device {} found!".format(cp.NAME))
            async with BleakClient(cp.ADDR, loop=loop) as client:
                x = await client.is_connected()
                win.display_status("Connected!")
                await enable_notif(cp, client)
                await plot_handler(cp, win)
                await disable_notif(cp, client)
        else:
            win.display_status("ERROR: Device not found.")

async def disable_notif(CP, client):
    await client.stop_notify(CP.CHAR1)
    await client.stop_notify(CP.CHAR2)
    await client.stop_notify(CP.CHAR3)
    await client.stop_notify(CP.CHAR4)
    await client.stop_notify(CP.CHAR5)

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


async def plot_forever(graph):
    i = 0
    while 1:
        graph.plot(i)
        i += 1
        await asyncio.sleep(.1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  # NEW must set the event loop

    win = MainWindow()
    win.show()

    with loop:  ## context manager calls .close() when loop completes, and releases all resources
        loop.run_until_complete(run(win, cp, loop))


if __name__ == '__main__':
    main()
