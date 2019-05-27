# AMG8833 Interpolating Camera

The 8x8 resolution of the AMG8833 produces a "blocky" display. The illusion of
higher resolution may be achieved using bicubic interpolation. This is
computationally intensive. On a Pyboard 1.1 the frame rate for 32x32 pixels
using Python code is ~1Hz. This can be increased to ~2.5Hz using assembler.

##### [Main README](../README.md)

# 1. Files

 * `cam_interp.py` 32x32 pixel demo using the Adafruit 0.96 inch OLED.
 * `interpolate.py` Portable interpolator using optimised Python code.
 * `interpolate_a.py` Version using Arm Thumb2 Assembler.

Both versions of the interpolator provide implementations of the `Interpolator`
class.

# 2. Interpolator class

Constructor:  
This takes a single arg, an `AMG88XX` instance.

Methods:__
 * `refresh` No args. Causes the `AMG88XX` instance and the interpolator to
 update with physical data.
 * `__call__` args `r, c`. The interpolator's coordinate space covers the range
 0.0 <= r <= 1.0, 0.0 <= c <= 1.0. Function call syntax causes the interpolator
 to return the temperature value for that row, col location.

# Usage

Converting a working 8x8 camera application to use interpolation is simple. The
aim is to replace the 8x8 array of pixels with a larger array of smaller
pixels: the `cam_interp.py` demo uses 32x32 squares of size 2x2.

After instantiating the sensor, create an `Interpolator`:
```python
i2c = machine.I2C(1)
sensor = AMG88XX(i2c)
sensor.ma_mode(True)  # Moving average mode
interpolator = Interpolator(sensor)
```
Replace
```python
    sensor.refresh()  # Acquire data
```
with
```python
   interpolator.refresh()
```
The iterator now needs to iterate through the number of virtual rows and cols
and display smaller squares. Instead of accessing the sensor, the value is
retrieved with
```python
val = interpolator(r/max_row, c/max_col)  # Values range 0.0..1.0
```

# Algorithm

The theory of cubic and bicubic interpolation is straightforward.
[This ref](https://www.paulinternet.nl/?page=bicubic) provides a good
explanation, with Java and C++ implementations.
