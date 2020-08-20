"""
Tanner Songkakul

Helper classes for CustomPeripheral devices and GUIs

Custom Peripheral
Contains UUIDs and parsing functions for basic custom peripheral.

CPPlot
Plot only object for plotting characteristic data on separate plots

Main Window
Full GUI with UI from QT Designer
"""


from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from collections import deque


class CustomPeripheral(object):
    def __init__(self):
        self.NAME = "unknown"
        self.ADDR = "unknown"
        self.SYSCFG = "f000abcd-0451-4000-b000-000000000000"
        self.CHAR1 = "f00062d2-0451-4000-b000-000000000000"
        self.CHAR2 = "f00044dc-0451-4000-b000-000000000000"
        self.CHAR3 = "f0003c36-0451-4000-b000-000000000000"
        self.CHAR4 = "f0003a36-0451-4000-b000-000000000000"
        self.CHAR5 = "f00030d8-0451-4000-b000-000000000000"
        self.CHAR_LIST = [self.CHAR1, self.CHAR2, self.CHAR3, self.CHAR4, self.CHAR5]
        self.CHAR1_DATA =[]
        self.CHAR2_DATA =[]
        self.CHAR3_DATA =[]
        self.CHAR4_DATA =[]
        self.CHAR5_DATA =[]
        self.ALL_DATA = [self.CHAR1_DATA, self.CHAR2_DATA, self.CHAR3_DATA, self.CHAR4_DATA, self.CHAR5_DATA]
        self.datacount = 0
        self.CONNECTED = 0

    def set_name(self,name):
        self.NAME = name

    def get_address(self,device_list):
        """Search list for device name and retrieve address"""
        for device in device_list:
            if device.name == self.NAME:
                self.ADDR = device.address
                return True
        return False

    def parse_data(self, sender,data):
        """For basic custom peripheral with data in first byte only, extend/replace as needed"""
        if sender == self.CHAR1:
            self.CHAR1_DATA.append(int(data[0]))
            return 1
        if sender == self.CHAR2:
            self.CHAR2_DATA.append(int(data[0]))
            return 2
        if sender == self.CHAR3:
            self.CHAR3_DATA.append(int(data[0]))
            return 3
        if sender == self.CHAR4:
            self.CHAR4_DATA.append(int(data[0]))
            return 4
        if sender == self.CHAR5:
            self.CHAR5_DATA.append(int(data[0]))
            return 5


class CPPlot: #simple object for plotting only
    def __init__(self,app,win,win_size):
        self.win_size = win_size
        self.plot_data = [deque([0]*self.win_size) for i in range(5)]

        self.app = app
        self.win = win
        self.char1_plot = win.addPlot(row=1, col=1, colspan=5, title="Char 1")
        self.char2_plot = win.addPlot(row=2, col=1, colspan=5, title="Char 2")
        self.char3_plot = win.addPlot(row=3, col=1, colspan=5, title="Char 3")
        self.char4_plot = win.addPlot(row=4, col=1, colspan=5, title="Char 4")
        self.char5_plot = win.addPlot(row=5, col=1, colspan=5, title="Char 5")
        self.char_plots = [self.char1_plot,self.char2_plot, self.char3_plot,self.char4_plot,self.char5_plot]

    def plot_char(self, char_num, data):
        char_ind = char_num - 1
        self.plot_data[char_ind].append(data)
        self.plot_data[char_ind].popleft()
        self.char_plots[char_ind].plot(self.plot_data[char_ind], clear= True)

    def update(self):
        pg.QtGui.QApplication.processEvents()

class MainWindow(QtWidgets.QMainWindow):
    #TODO add characteristic and packet printouts
    def __init__(self, *args, **kwargs):
        self.plot_data = []
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        uic.loadUi('Basic_CP_GUI.ui', self)  # From QTDesigner
        self.connectButton.clicked.connect(self.get_device)  # Connect button
        self.actionQuit.triggered.connect(self.close) # File->Quit
        self.connect_button = 0
        self.device_name = "None"
        self.line_array = []
        for i in range(5):
            self.line_array.append(self.plotWidget.plot([], pen=(i, 5)))

    def plot(self, data):
        """Plot single line"""
        self.plot_data.append(data)
        self.plotWidget.plot(self.plot_data)

    def plot_all(self, plot_list):
        # fast update of all data
        for i, data in enumerate(plot_list):
            self.line_array[i].setData(data)

    def get_device(self):
        """Connect button press callback, retrieves device name from text box and sets flag"""
        self.connect_button = 1
        self.device_name = self.deviceEntry.text()

    def button_ack(self):
        """Clear button press flag"""
        self.connect_button = 0

    def display_status(self, msg):
        """Display messages"""
        self.statusDisp.setText(msg)

