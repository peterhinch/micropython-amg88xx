This is a record of the files used to build my PIR camera.

Usage:
The topmost switch controls maximum temperature: push left to increase, push
right to decrease. A long press initiates auto-ranging, a short press clears
it.

The bottom switch controls minimum temperature. A long press causes a display
hold, a short press clears it.

The .fzz file defines the PCB. The fixing holes do not align perfectly with
those on the OLED display: some fettling is required.

The color scale is not ideal at the blue end of the spectrum. This is because
the rrrgggbb mapping is only capable of displaying 4 levels of blue. This gives
some unexpected color shades as blue ramps down and green ramps up.
