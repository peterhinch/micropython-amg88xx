# mapper.py Color mapper for thermal IR cameras

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

# Mapper class. Converts a temperature value to r, g, b colors. Colors are in
# range 0..255. Temperature range may be specified.
class Mapper:

    def __init__(self, tmin, tmax, ncolors=30):
        self._ncolors = ncolors
        N = ncolors
        self._b = bytearray(max(int(255 *(1 - 2 * x / N)), 0) for x in range(N))
        self._g = bytearray(int(255 * 2*x/N) if x < N/2 else int(255*2*(1 - x/N)) for x in range(N))
        self._r = bytearray(max(int(255 *(2 * x / N -1)), 0) for x in range(N))
        self.set_range(tmin, tmax)

    def set_range(self, tmin, tmax):
        if tmax <= tmin:
            raise ValueError('Invalid temperature range.')
        self._tmin = tmin
        self._tmax = tmax
        self._factor = (self._ncolors - 1) / (tmax - tmin)

    def __call__(self, t):  # Celcius to color value
        t = int(t)
        # Constrain
        t = max(min(t, self._tmax), self._tmin)
        # Ensure +ve, range 0 .. tmax-tmin
        t -= self._tmin
        t = round(t * self._factor)
        return self._r[t], self._g[t], self._b[t]
