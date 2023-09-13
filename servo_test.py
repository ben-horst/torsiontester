import servo_control
import time

servo = servo_control.BusServo('COM6', 1)

servo.commandSpeed(100)

while True:
    #servo.commandPosition(0, 3000)
    #time.sleep(5)
    print(servo.readPosition())
    #servo.commandPosition(240, 3000)
    #time.sleep(1)
    #print(servo.readPosition())