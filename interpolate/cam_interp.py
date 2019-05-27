# cam_interp.py Thermal camera based on Adafruit AMG8833 (Product ID 3538) sensor and
# Adafruit 0.96 inch OLED display (Product ID 684)

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

import framebuf
import machine
from ssd1331 import SSD1331  # Driver for 0.96 inch OLED
from mapper import Mapper  # Maps temperature to rgb color
from amg88xx import AMG88XX
# from interpolate import Interpolator  # Portable version
from interpolate_a import Interpolator  # STM assembler version

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
interpolator = Interpolator(sensor)

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
    interpolator.refresh()  # Acquire data from sensor via interpolator.
    for row in range(32):
        for col in range(32):
            r = 31 - row if invert else row
            c = 31 - col if reflect else col
            if transpose:
                r, c = c, r
            # For interpolator 0.0 <= row <= 1.0, 0.0 <= col <= 1.0
            val = interpolator(r/31, c/31)
            ssd.fill_rect(col * 2, row * 2, 2, 2, ssd.rgb(*mapper(val)))
    ssd.show()
