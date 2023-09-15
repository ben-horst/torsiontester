import servo_control
import time

servo = servo_control.BusServo('COM6', 1)

#servo.commandSpeed(00)
servo.commandPosition(20, 5)

# while True:
#     print(servo.readPosition())
    