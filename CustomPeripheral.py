import struct
from bleak import BleakClient
from bleak import discover


class CustomPeripheral:
    def __init__(self, name):
        self.NAME = name
        self.ADDR = "unknown"
        self.SYSCFG = "f000abcd-0451-4000-b000-000000000000"
        self.CHAR1 = "f00062d2-0451-4000-b000-000000000000"
        self.CHAR2 = "f00044dc-0451-4000-b000-000000000000"
        self.CHAR3 = "f0003c36-0451-4000-b000-000000000000"
        self.CHAR4 = "f0003a36-0451-4000-b000-000000000000"
        self.CHAR5 = "f00030d8-0451-4000-b000-000000000000"
        self.CHAR1_DATA =[]
        self.CHAR2_DATA =[]
        self.CHAR3_DATA =[]
        self.CHAR4_DATA =[]
        self.CHAR5_DATA =[]


    def get_address(self,device_list):
        for device in device_list:
            if device.name == self.NAME:
                self.ADDR = device.address
                return True
        return False

    def parse_data(self, sender,data):
        if sender == self.CHAR1:
            self.CHAR1_DATA.append(data)
        if sender == self.CHAR2:
            self.CHAR2_DATA.append(data)
        if sender == self.CHAR3:
            self.CHAR3_DATA.append(data)
        if sender == self.CHAR4:
            self.CHAR4_DATA.append(data)
        if sender == self.CHAR5:
            self.CHAR5_DATA.append(data)


