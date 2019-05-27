# interpolate.py Bicubic interpolator for AMG8833 thermal IR sensor

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

# Algorithm derivation https://www.paulinternet.nl/?page=bicubic

from array import array
import math

# Sensor is 8*8.
_PIXEL_ARRAY_WIDTH = const(8)
_PIXEL_ARRAY_HEIGHT = const(8)
# Extrapolate 1 pixel at each edge so that the 1st derivative can be estimated.
_WIDTH = const(10)
_HEIGHT = const(10)

# Cubic interpolation of a 4 element one dimensional array of samples p.
# Interpolation is between samples p[1] and p[2]: samples p[0] and p[3] provide
# a first derivative estimate at points p[1] and p[2].
# 0 <= x < 1.0 is the offset between p[1] and p[2]
@micropython.viper
def interp_arr(p, x):
    return p[1] + 0.5 * x*(p[2] - p[0] + x*(2.0*p[0] - 5.0*p[1] + 4.0*p[2] - p[3] + x*(3.0*(p[1] - p[2]) + p[3] - p[0])))

# Return index into data array from row, col
_idx = lambda r, c : r * _WIDTH + c

@micropython.native
def bicubic(line, offs, y, x, rd = array('f', (0 for _ in range(4)))):
    rd[0] = interp_arr(line[offs:], x)  # Get value of location x of row 0
    offs += _WIDTH  # Increment one row
    rd[1] = interp_arr(line[offs:], x)
    offs += _WIDTH
    rd[2] = interp_arr(line[offs:], x)
    offs += _WIDTH
    rd[3] = interp_arr(line[offs:], x)
    return interp_arr(rd, y)  # interpolate the column of data

class Interpolator:
    def __init__(self, sensor):
        self._sensor = sensor
        self._data = array('f', (0 for _ in range(_HEIGHT * _WIDTH)))
        self._mvd = memoryview(self._data)

    def refresh(self, _=None):
        s = self._sensor
        s.refresh()
        # Populate sensor data
        for row in range(_PIXEL_ARRAY_HEIGHT):
            for col in range(_PIXEL_ARRAY_WIDTH):
                self[row + 1, col + 1] = s[row, col]
        # Extrapolate edges
        # Populate corners
        self[0, 0] = 2 * self[1, 1] - self[2, 2]
        self[0, _WIDTH -1] = 2 * self[1, _WIDTH -2] - self[2, _WIDTH -3]
        self[_HEIGHT -1, 0] =  2 * self[_HEIGHT -2, 1] - self[_HEIGHT -3, 2]
        self[_HEIGHT -1, _WIDTH -1] = 2 * self[_HEIGHT -2, _WIDTH -2] - self[_HEIGHT -3, _WIDTH -3]
        # Populate edges
        col = _WIDTH -1
        for row in range(1, _HEIGHT -1):
            self[row, 0] = 2 * self[row, 1] - self[row, 2]
            self[row, col] = 2 * self[row, col -1] - self[row, col -2]
        row = _HEIGHT -1
        for col in range(1, _WIDTH -1):
            self[0, col] = 2 * self[1, col] - self[2, col]
            self[row, col] = 2 * self[row -1, col] - self[row -2, col]

    def __getitem__(self, index):
        return self._data[_idx(*index)]

    def __setitem__(self, index, v):
        self._data[_idx(*index)] = v

    # Access interpolated data by row, col: bounding box 0.0,0.0 -> 1.0,1.0
    def __call__(self, r, c):
        if r < 0.0 or r > 1.0 or c < 0.0 or c > 1.0:
            r = max(min(r, 1.0), 0.0)
            c = max(min(c, 1.0), 0.0)
        y, row = math.modf(r * 6.99)
        x, col = math.modf(c * 6.99)
        return bicubic(self._mvd, int(row * _WIDTH + col), y, x)

