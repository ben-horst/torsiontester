import serial

class MTT03():
    def __init__(self, com_port):
        self.__com_port = com_port

        self.initialize()

    def initialize(self):
        self._ser = serial.Serial(
            port = self.__com_port,
            baudrate = 9600,
            timeout=1
        )

    def read(self):
        self._ser.write(b'?\r')
        response = self._ser.readline().decode().strip()
        #might want to remove units from string
        return response