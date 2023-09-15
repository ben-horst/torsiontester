import serial
import time

class BusServo():
    """initializes a servo on the specified com port and device ID"""
    def __init__(self, com_port, device_id):
        self.__com_port = com_port
        self.__device_id = device_id
        
        self.initialize()

    def initialize(self):
        self._ser = serial.Serial(
            port = self.__com_port,
            baudrate = 115200,
            timeout=None
        )

    def writeCommand(self, cmd, par1 = None, par2 = None):
        buf = bytearray(b'\x55\x55')
        len = 3
        par_buf = bytearray(b'')

        #assemble parameters
        if par1 is not None:
            len += 2  
            par_buf.extend([(0xff & par1), (0xff & (par1 >> 8))]) 
        if par2 is not None:
            len += 2
            par_buf.extend([(0xff & par2), (0xff & (par2 >> 8))])
        buf.extend([(0xff & self.__device_id), (0xff & len), (0xff & cmd)])
        buf.extend(par_buf)

        #calculate checksum
        sum = 0x00
        for b in buf:
            sum += b        #sum all bytes
        sum = sum - 0x55 - 0x55  #remove the two 0x55 bytes
        sum = ~sum  #invert
        buf.append(0xff & sum)

        #send message
        self._ser.write(buf)

    def commandPosition(self, angle, time):
        """goes to set angle (0-240 deg) smoothly in set time (ms)"""
        pos = int(1000 * angle / 240)
        self.writeCommand(29, par1 = 0, par2 =  0)  #go back into servo mode
        self.writeCommand(1, par1 = pos, par2 = time)

    def commandSpeed(self, speed):
        """starts rotating at speed -1000 to 1000"""
        self.writeCommand(29, par1 = 1, par2 = speed)

    def readPosition(self):
        """request servo position and return value"""
        pos = None
        self.writeCommand(28)
        #time.sleep(0.005)
        expected_bytes = 8
        recv_data = self._ser.read(expected_bytes)
        if recv_data[0] == 0x55 and recv_data[1] == 0x55 and recv_data[4] == 0x1C :
            pos = int.from_bytes(recv_data[5:7], byteorder = 'little', signed = True)
            return pos

    