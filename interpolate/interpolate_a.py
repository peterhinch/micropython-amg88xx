# interpolate_a.py Bicubic interpolator for AMG8833 thermal IR sensor
# version for STM using Arm Thumb2 Assembler

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

@micropython.viper
def interp_arr_x(p, x):
    return p[1] + 0.5 * x*(p[2] - p[0] + x*(2.0*p[0] - 5.0*p[1] + 4.0*p[2] - p[3] + x*(3.0*(p[1] - p[2]) + p[3] - p[0])))

# Cubic interpolation of a 4 element one dimensional array of samples p.
# Interpolation is between samples p[1] and p[2]: samples p[0] and p[3] provide
# a first derivative estimate at points p[1] and p[2].
# 0 <= x < 1.0 is the offset between p[1] and p[2]
# p[1] + 0.5 * x*(p[2] - p[0] + x*(2.0*p[0] - 5.0*p[1] + 4.0*p[2] - p[3] + x*(3.0*(p[1] - p[2]) + p[3] - p[0])))

# r0: Array of 4 samples
# r1: Array of _coefficients. r1[0] = x, r1[1:] = 0.5, 2.0, 3.0, 4.0, 5.0
# r2: r2[0] will hold result
@micropython.asm_thumb
def interp_arr(r0, r1, r2):
    vldr(s0, [r1, 4])  # s0 = 0.5
    vldr(s1, [r1, 8])  # s1 = 2.0
    vldr(s2, [r1, 12])  # s2 = 3.0
    vldr(s3, [r1, 16])  # s3 = 4.0
    vldr(s4, [r1, 20])  # s4 = 5.0
    vldr(s5, [r0, 0])  # s5 = p[0]
    vldr(s6, [r0, 4])  # s6 = p[1]
    vldr(s7, [r0, 8])  # s7 = p[2]
    vldr(s8, [r0, 12])  # s8 = p[3]
    vldr(s9, [r1, 0])  # s9 = x
    vsub(s10, s6, s7)  # s10 = p[1] -p[2]
    vmul(s10, s10, s2) # s10 = 3.0*(p[1] - p[2])
    vadd(s10, s10, s8) # s10 += p[3]
    vsub(s10, s10, s5)  # s10 -= p[0]
    vmul(s10, s10, s9)  # s10 *= x
    vsub(s10, s10, s8)  # s10 -= p[3]
    vmul(s11, s3, s7)  # s11 = 4.0*p[2]
    vadd(s10, s10, s11)  # s10 += 4.0*p[2]
    vmul(s11, s4, s6)  # s11 = 5.0*p[1]
    vsub(s10, s10, s11)  # s10 -= 5.0*p[1]
    vmul(s11, s1, s5)  # s11 = 2.0*p[0]
    vadd(s10, s10, s11)  # s10 += 2.0*p[0]
    vmul(s10, s10, s9)  # s10 *= x
    vsub(s10, s10, s5)  # s10 -= p[0]
    vadd(s10, s10, s7)  # s10 += p[2]
    vmul(s10, s10, s9)  # s10 *= x
    vmul(s10, s10, s0)  # s10 *= 0.5
    vadd(s10, s10, s6)  # s10 += p[1]
    vstr(s10, [r2, 0])

# Return index into data array from row, col
_idx = lambda r, c : r * _WIDTH + c

class Interpolator:
    def __init__(self, sensor):
        self._sensor = sensor
        self._data = array('f', (0 for _ in range(_HEIGHT * _WIDTH)))
        self._coeffs = array('f', (0.0, 0.5, 2.0, 3.0, 4.0, 5.0))
        self._mvd = memoryview(self._data)
        self._rd = array('f', (0 for _ in range(4)))
        self._mvrd = memoryview(self._rd)

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

    @micropython.native
    def bicubic(self, offs, y, x):
        c = self._coeffs
        rd = self._mvrd
        line = self._mvd  # line[offs] points to sample set
        c[0] = x
        interp_arr(line[offs:], c, rd)  # Get value of location x of row 0
        offs += _WIDTH  # Increment one row
        interp_arr(line[offs:], c, rd[1:])
        offs += _WIDTH
        interp_arr(line[offs:], c, rd[2:])
        offs += _WIDTH
        interp_arr(line[offs:], c, rd[3:])
        c[0] = y
        interp_arr(rd, c, c)  # interpolate the column of data
        return c[0]

    # Access interpolated data by row, col: bounding box 0.0,0.0 -> 1.0,1.0
    def __call__(self, r, c):
        if r < 0.0 or r > 1.0 or c < 0.0 or c > 1.0:
            r = max(min(r, 1.0), 0.0)
            c = max(min(c, 1.0), 0.0)
        y, row = math.modf(r * 6.99)
        x, col = math.modf(c * 6.99)
        return self.bicubic(int(row * _WIDTH + col), y, x)

#import pyb
#def test():
    #a = array('f', (x for x in range(4)))
    #coeffs = array('f', (0.0, 0.5, 2.0, 3.0, 4.0, 5.0))
    #res = array('f', (0.0,))
    #for _ in range(10):
        #for i in range(4):
            #a[i] = pyb.rng()/2**29
        #x = pyb.rng()/2**30
        #print('Py', interp_arr_x(a, x))
        #coeffs[0] = x
        #res[0] = 0
        #interp_arr(a, coeffs, res)
        #print('Asm', res[0])
