"""
Tanner Songkakul

CustomPeripheralGUI.py

Uses bleak and PyQT to connect to a CC2642 Launchpad running Custom Peripheral
and plot data on each characteristics.

Requires bleak, pyqt, qasync and included customperipheral library
"""
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import sys
import asyncio
import asyncqt

import bleak
from bleak import BleakClient
from bleak import discover
from customperipheral import CustomPeripheral

cp = CustomPeripheral()


def notification_handler(sender, data):
    """Handle incoming packets."""
    print("Data received")
    print(sender)
    char = cp.parse_data(sender, data)


class MainWindow(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        # Initialize objects and variables
        self.scan_list = []
        # Load the UI Page and QTimer
        uic.loadUi('Basic_CP_GUI.ui', self)  # From QTDesigner
        self.line_array = []
        for i in range(5):
            self.line_array.append(self.plotWidget.plot([], pen=(i, 5)))
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_plot)
        # Attach button callbacks
        self.scanButton.clicked.connect(self.scan_callback)
        self.scanBox.activated.connect(self.select_device)
        self.connectButton.clicked.connect(self.connect_callback)
        self.actionQuit.triggered.connect(self.close) # File->Quit

    async def device_scan(self):
        self.display_status("Scanning...")
        # print('Scanning for devices')
        if not cp.CONNECTED:
            self.scanBox.clear()
            self.scan_list = []
            devices = await discover(30)
            # print('scan returns...')
            for i, device in enumerate(devices):
                if device.name != "Unknown":
                    self.scanBox.addItem(device.name)
                    self.scan_list.append(device)
                # print(f"{i}: {device.name}")
            if self.scan_list:
                cp.NAME = self.scan_list[0].name # required for case when CP is first in list
                cp.ADDR = self.scan_list[0].address
                self.display_status("Scan complete!")
            else:
                self.display_status("No devices found!")

    def scan_callback(self):
        scan_task = self.device_scan()
        asyncio.ensure_future(scan_task, loop=loop)

    async def connect_task(self):
        self.display_status("Connecting to {}".format(cp.NAME))
        async with BleakClient(cp.ADDR, loop = loop ) as client:
            try:
                x = await client.is_connected()  # Attempt device connection TODO add error messages
                await self.enable_notif(client)
            except AttributeError:
                win.display_status("Unable to connect!")
            except bleak.exc.BleakDotNetTaskError:
                win.display_status("Could not get GATT characteristics")
            except:
                win.display_status("Error")

    async def enable_notif(self, client):
        """Start notifications on all characteristics"""
        for char in cp.CHAR_LIST:
            await client.start_notify(char, notification_handler)
            print("Notification enabled")
            win.display_status("Connected!")
            self.timer.start()
            await asyncio.sleep(5000)

    def connect_callback(self):
        connect_task = self.connect_task()
        asyncio.ensure_future(connect_task, loop=loop)

    def select_device(self):
        if not cp.CONNECTED:
            cp.NAME = self.scan_list[self.scanBox.currentIndex()].name
            cp.ADDR = self.scan_list[self.scanBox.currentIndex()].address
            print(cp.NAME)
            print(cp.ADDR)

    def display_status(self, msg):
        """Display messages"""
        self.statusDisp.setText(msg)

    def update_plot(self):
        # fast update of all data
        print("Update plot.")
        self.line_array[0].setData(cp.CHAR1_DATA)
        self.line_array[1].setData(cp.CHAR2_DATA)
        self.line_array[2].setData(cp.CHAR3_DATA)
        self.line_array[3].setData(cp.CHAR4_DATA)
        self.line_array[4].setData(cp.CHAR5_DATA)


app = QApplication(sys.argv)
loop = asyncqt.QEventLoop(app)
asyncio.set_event_loop(loop)  # NEW must set the event loop
win = MainWindow()
win.show()
with loop:
    sys.exit(loop.run_forever())
