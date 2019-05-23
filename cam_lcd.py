# cam_lcd.py Thermal camera based on Adafruit AMG8833 (Product ID 3538) sensor
# and official LCD160CR LCD display.

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

import lcd160cr
import machine
import utime
from mapper import Mapper  # Maps temperature to rgb color
from amg88xx import AMG88XX

# Temperature range to cover
TMAX = 30
TMIN = 15

# Instantiate color mapper
mapper = Mapper(TMIN, TMAX)

# Instantiate display
lcd = lcd160cr.LCD160CR('Y')
lcd.set_pen(0, 0)
lcd.erase()

# Instantiate temperature sensor
i2c = machine.I2C(1)
sensor = AMG88XX(i2c)
sensor.ma_mode(True)  # Moving average mode

# Draw color scale at right of display
col = 80
val = TMIN
dt = (TMAX - TMIN) / 32
for row in range(63, -1, -2):
    color = lcd.rgb(*mapper(val))
    lcd.set_pen(color, color)
    lcd.rect(col, row, 15, 2)
    val += dt

# Coordinate mapping from sensor to screen
invert = True  # For my breadboard layout
reflect = True
transpose = True
print('Temperature {:5.1f}°C'.format(sensor.temperature()))

# Run the camera
white = lcd.rgb(255, 255, 255)
black = lcd.rgb(0, 0, 0)
lcd.set_font(3)
lcd.set_text_color(white, black)
while True:
    sensor.refresh()  # Acquire data
    max_t = -1000
    min_t = 1000
    sum_t = 0
    for row in range(8):
        for col in range(8):
            r = 7 - row if invert else row
            c = 7 - col if reflect else col
            if transpose:
                r, c = c, r
            val = sensor[r, c]
            max_t = max(max_t, val)
            min_t = min(min_t, val)
            sum_t += val
            color = lcd.rgb(*mapper(val))
            lcd.set_pen(color, color)
            lcd.rect(col * 8, row * 8, 8, 8)
    lcd.set_pos(0, 70)
    lcd.write('Temperatures')
    lcd.set_pos(0, 85)
    lcd.write('Max:{:4d}C'.format(max_t))
    lcd.set_pos(0, 100)
    lcd.write('Min:{:4d}C'.format(min_t))
    lcd.set_pos(0, 115)
    lcd.write('Avg:{:4d}C'.format(round(sum_t / 64)))
    utime.sleep(0.2)
