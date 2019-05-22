# micropython-amg88xx
Driver for Grid-EYE 8x8 pixel thermal infra red array sensor (Adafruit 3538).

The driver, test programs and this doc are provisional and may be subject to
change.

The driver is a port of the
[Adafruit CircuitPython driver](https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx)
modified for MicroPython. Dependencies on Adafruit libraries removed, coding
adapted to conform to MicroPython conventions.

Original author(s): Dean Miller, Scott Shawcroft.  
Adapted by Peter Hinch.

# 1. Files

 * `amg88xx.py` The device driver.
 * `amg_test.py` Simple text based test program.
 * `cam.py` Thermal camera demo using
 [Adafruit 0.96 OLED display](https://www.adafruit.com/product/684).

# 2. Wiring

If used with a Pyboard

| pyboard | amg8833 |
|:-------:|:-------:|
| 3V3     | VIN     |
| GND     | GND     |
| SCL X9  | SCL     |
| SDA X10 | SDA     |

# 3. AMG88XX class

This maintains an internal `bytearray` object holding a single frame of raw
data from the sensor. It is populated by the `refresh` method. The contents may
be retrieved as integer temperatures in °C by means of array access syntax.

Constructor:  
This takes the following arguments:
 * `i2c` An `I2C` instance created using the `machine` module.
 * `address=0x69` The default device address. If you solder the jumper on the
 back of the board labeled `Addr`, the address will change to 0x68.

Methods:
 * `refresh` Takes an optional arg which is ignored. This method causes the
 internal array to be updated with data from the sensor. On a Pyboard 1.x this
 method blocks for 2.9ms. This method does not allocate RAM and may be called
 by an interrupt service routine. The dummy arg facilitiates use as a timer
 callback (see commented out code in `cam.py`).
 * `__getitem__` Args `row`, `col`. Enables access to the data retrieved by
 `refresh`. Return value is a signed integer representing the temperature of
 that pixel in °C.

Data Access:  
After issuing the `refresh` method, a set of pixel data may be read by means of
array access.

```python
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
```

# 4. Camera demo

This works, but I may do further work to improve the image quality. It assumes
a Pyboard linked to an
[Adafruit 0.96 OLED display](https://www.adafruit.com/product/684). Wiring is
as follows:

| pyboard | OLED |
|:-------:|:----:|
| 3V3     | VCC  |
| GND     | GND  |
| X8 MOSI | SDA  |
| X6 SCL  | SCL  |
| X3      | RES  |
| X2      | CS   |
| X1      | DC   |

The sensor is wired as detailed above.

Orientation of the display may be adjusted to match the physical layout of the
devices by setting the following program booleans:
 * `invert` Swap top and bottom.
 * `reflect` Swap left and right.
 * `transpose` Exchange row and column.

The limits of temperature display may be adjusted by assigning integer values
to these program values:
 * `TMAX` Temperatures >= `TMAX` appear red.
 * `TMIN` Temperatures <= `TMIN` appear blue.
