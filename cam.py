# cam.py Thermal camera based on Adafruit AMG8833 (Product ID 3538) sensor and
# Adafruit 0.96 inch OLED display (Product ID 684)

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

import framebuf
import machine
import utime
import gc
from amg88xx import AMG88XX
# For timer callback demo:
# import pyb

# Temperature range to cover
TMAX = 30
TMIN = 15

# Display driver
# See https://github.com/peterhinch/micropython-nano-gui/tree/master/drivers/ssd1331
# for explanation of the bytes objects used to initialise the hardware.
class SSD1331(framebuf.FrameBuffer):
    _colors = bytearray(30)  # Populated by set_range
    _factor = 1
    _tmax = 100
    _tmin = 0
    # Convert r, g, b in range 0-255 to an 8 bit colour value
    #  acceptable to hardware: rrrgggbb
    @staticmethod
    def rgb(r, g, b):
        return (r & 0xe0) | ((g >> 3) & 0x1c) | (b >> 6)

    # Initialise color list, max and min temps and multiplier
    @staticmethod
    def set_range(tmin, tmax):
        SSD1331._tmax = tmax
        SSD1331._tmin = tmin
        ncolors = len(SSD1331._colors)
        for x in range(ncolors):
            r = 0 if x < 20 else (x - 20) * 25
            b = 0 if x > 10 else (10 - x) * 25
            if x > 5 and x < 15:
                g = (x - 5) * 25
            elif x >= 15 and x < 25:
                g = (25 - x) * 25
            else:
                g = 0
            SSD1331._colors[x] = SSD1331.rgb(r, g, b)
        SSD1331._factor = (ncolors - 1) / (tmax - tmin)

    @staticmethod
    def to_color(t):  # Celcius to color value
        # Constrain
        t = max(min(t, SSD1331._tmax), SSD1331._tmin)
        # Ensure +ve, range 0 .. tmax-tmin
        t -= SSD1331._tmin
        return SSD1331._colors[round(t * SSD1331._factor)]

    def __init__(self, spi, pincs, pindc, pinrs, height=64, width=96):
        self.spi = spi
        self.rate = 6660000  # Data sheet: 150ns min clock period
        self.pincs = pincs
        self.pindc = pindc  # 1 = data 0 = cmd
        self.height = height  # Required by Writer class
        self.width = width
        # Save color mode for use by writer_gui (blit)
        self.mode = framebuf.GS8  # Use 8bit greyscale for 8 bit color.
        gc.collect()
        self.buffer = bytearray(self.height * self.width)
        super().__init__(self.buffer, self.width, self.height, self.mode)
        pinrs(0)  # Pulse the reset line
        utime.sleep_ms(1)
        pinrs(1)
        utime.sleep_ms(1)
        self._write(b'\xae\xa0\x32\xa1\x00\xa2\x00\xa4\xa8\x3f\xad\x8e\xb0'\
        b'\x0b\xb1\x31\xb3\xf0\x8a\x64\x8b\x78\x8c\x64\xbb\x3a\xbe\x3e\x87'\
        b'\x06\x81\x91\x82\x50\x83\x7d\xaf', 0)
        gc.collect()
        self.show()

    def _write(self, buf, dc):
        self.spi.init(baudrate=self.rate, polarity=1, phase=1)
        self.pincs(1)
        self.pindc(dc)
        self.pincs(0)
        self.spi.write(buf)
        self.pincs(1)

    def show(self, _cmd=b'\x15\x00\x5f\x75\x00\x3f'):  # Pre-allocate
        self._write(_cmd, 0)
        self._write(self.buffer, 1)

SSD1331.set_range(TMIN, TMAX)  # Map temps 
pdc = machine.Pin('X1', machine.Pin.OUT_PP, value=0)
pcs = machine.Pin('X2', machine.Pin.OUT_PP, value=1)
prst = machine.Pin('X3', machine.Pin.OUT_PP, value=1)
spi = machine.SPI(1)
ssd = SSD1331(spi, pcs, pdc, prst)
ssd.fill(0)
ssd.show()

i2c = machine.I2C(1)
sensor = AMG88XX(i2c)

# Demo use in timer callback
# tim = pyb.Timer(1)
# tim.init(freq=10)
# tim.callback(sensor.refresh)

# Draw color scale at right of display
col = 80
val = TMIN
dt = (TMAX - TMIN) / 32
for row in range(63, -1, -2):
    ssd.fill_rect(col, row, 15, 2, ssd.to_color(int(val)))
    val += dt

# Coordinate mapping from sensor to screen
invert = True  # For my breadboard layout
reflect = True
transpose = True
print('Temperature {:5.1f}°C'.format(sensor.temperature()))
while True:
    sensor.refresh()  # Acquire data
    for row in range(8):
        for col in range(8):
            r = 7 - row if invert else row
            c = 7 - col if reflect else col
            if transpose:
                r, c = c, r
            val = sensor[r, c]
            ssd.fill_rect(col * 8, row * 8, 8, 8, ssd.to_color(val))
    ssd.show()
    utime.sleep(0.2)
