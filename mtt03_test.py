import mtt03
import time

torque = mtt03.MTT03('COM5')

while True:
    print(torque.read())
    time.sleep(1)