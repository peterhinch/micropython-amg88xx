# cam.py Thermal camera based on Adafruit AMG8833 (Product ID 3538) sensor and
# Adafruit 0.96 inch OLED display (Product ID 684)

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

import framebuf
import machine
import utime
# 8-bit color driver for 0.96 inch OLED
from ssd1331 import SSD1331
# Optional 16-bit color driver
# from ssd1331_16bit import SSD1331
from mapper import Mapper  # Maps temperature to rgb color
from amg88xx import AMG88XX

# For timer callback demo:
# import pyb

# Temperature range to cover
TMAX = 30
TMIN = 15

# Instantiate color mapper
mapper = Mapper(TMIN, TMAX)

# Instantiate display
pdc = machine.Pin('X1', machine.Pin.OUT_PP, value=0)
pcs = machine.Pin('X2', machine.Pin.OUT_PP, value=1)
prst = machine.Pin('X3', machine.Pin.OUT_PP, value=1)
spi = machine.SPI(1)
ssd = SSD1331(spi, pcs, pdc, prst)
ssd.fill(0)
ssd.show()

# Instantiate temperature sensor
i2c = machine.I2C(1)
sensor = AMG88XX(i2c)
sensor.ma_mode(True)  # Moving average mode

# Demo use in timer callback. No point in running faster than 10Hz as this is
# the update rate of the chip.
# tim = pyb.Timer(1)
# tim.init(freq=10)
# tim.callback(sensor.refresh)

# Draw color scale at right of display
col = 80
val = TMIN
dt = (TMAX - TMIN) / 32
for row in range(63, -1, -2):
    ssd.fill_rect(col, row, 15, 2, ssd.rgb(*mapper(int(val))))
    val += dt

# Coordinate mapping from sensor to screen
invert = True  # For my breadboard layout
reflect = True
transpose = True
print('Temperature {:5.1f}°C'.format(sensor.temperature()))

# Run the camera
while True:
    sensor.refresh()  # Acquire data
    for row in range(8):
        for col in range(8):
            r = 7 - row if invert else row
            c = 7 - col if reflect else col
            if transpose:
                r, c = c, r
            val = sensor[r, c]
            ssd.fill_rect(col * 8, row * 8, 8, 8, ssd.rgb(*mapper(val)))
    ssd.show()
    utime.sleep(0.2)
