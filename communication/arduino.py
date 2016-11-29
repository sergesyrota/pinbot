import serial


class Arduino(object):
    serial = None

    def __init__(self, port, baud=115200):
        self.serial = serial.Serial(port, baud)

    def longPressA(self):
        serial.write('A')

    def shortPressA(self):
        serial.write('a')

    def longPressB(self):
        serial.write('B')

    def shortPressB(self):
        serial.write('b')

    def close(self):
        if (serial):
            serial.close()

    def __del__(self):
        self.close()
