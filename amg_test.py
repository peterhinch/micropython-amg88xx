# amg_test.py Basic test of AMG8833 sensor

import machine
import utime
from amg88xx import AMG88XX


i2c = machine.I2C(1)
sensor = AMG88XX(i2c)
while True:
    sensor.refresh()
    for row in range(8):
        print()
        for col in range(8):
            print('{:4d}'.format(sensor[row, col]), end='')
    utime.sleep(0.2)
