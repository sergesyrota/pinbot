import serial
import math


class Arduino(object):
    serial = None

    def __init__(self, port, baud=115200):
        self.serial = serial.Serial(port, baud)

    def pressA(self, milliseconds):
        self.serial.write('A' + chr(int(math.ceil(milliseconds/10))))

    def pressB(self, milliseconds):
        self.serial.write('B' + chr(int(math.ceil(milliseconds/10))))

    def close(self):
        if (self.serial):
            self.serial.close()

    def __del__(self):
        self.close()
