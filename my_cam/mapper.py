# mapper.py Color mapper for thermal IR cameras

# Released under the MIT licence.
# Copyright (c) Peter Hinch 2019

# Mapper class. Converts a temperature value to r, g, b colors. Colors are in
# range 0..255. Temperature range may be specified.
class Mapper:

    def __init__(self, tmin, tmax, ncolors=30):
        self._ncolors = ncolors
        N = ncolors
        self._b = bytearray(max(int(255*(1 - 2*x/N)), 0) for x in range(N + 1))
        self._g = bytearray(int(255*2*x/N) if x < N/2 else int(255*2*(1 - x/N)) for x in range(N + 1))
        self._r = bytearray(max(int(255*(2*x/N - 1)), 0) for x in range(N + 1))
        self.set_range(tmin, tmax)

    def set_range(self, tmin, tmax):
        if tmax <= tmin:
            raise ValueError('Invalid temperature range.')
        self._tmin = tmin
        self._tmax = tmax
        self._factor = self._ncolors/(tmax - tmin)

    def __call__(self, t):  # Celcius to color value
        # Constrain
        t = max(min(t, self._tmax), self._tmin)
        # Ensure +ve, inclusive range 0..tmax-tmin
        t -= self._tmin
        t = round(t * self._factor)  # 0..ncolors
        return self._r[t], self._g[t], self._b[t]
