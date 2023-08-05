__author__ = 'Maarten'


class BusBase():
    def __init__(self, port, debug=True):
        self.port = port
        self.pwd = b"notasecret"
        self.debug = debug

    def _printDebug(self, msg):
        if self.debug:
            print(msg)


class Packet():
    def __init__(self, action=PacketType.EMPTY, data={}):
        self.action = action
        self.data = data


class PacketType():
    EMPTY, TEST, SETMOTOR, PROCESSPICTURE, STARTSCAN, CALIBRATE, DONEPICTURE, DONESCAN = range(8)
