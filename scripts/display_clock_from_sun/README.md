# display_clock_from_sun

A 24-hour clock on two **LED Displays** (hours and minutes), worked out from the sun's position seen by a **Daylight Sensor**.

*Previously called `led_display_hms_clock`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | LED Display (hours) |
| `d1` | LED Display (minutes) |
| `d3` | Daylight Sensor |

## What it does

- Sun `Horizontal` angle 0–360° → 00:00–23:59 (4 minutes per degree).
- Displays kept On in Mode 10 (two-character text), written only when the value changes.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `display_clock_from_sun.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `SENSOR_DIRECTION` | `0` | Which way the sensor faces (0–3, adds 90° each) |
| `OFFSET_DEG` | `0` | Shifts the angle |
| `INVERT` | `0` | 1 = angle runs backwards |
| `SHIFT_MIN` | `0` | Moves the clock by whole minutes |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `display_clock_from_sun.ic10` into the chip and run it.

## Notes

- `d2` is unused (the original wiring used `d3` for the sensor, so it is kept).
- This is game-sun time, not real time; tune `OFFSET_DEG`/`SHIFT_MIN` until noon looks right on your planet.
- Device notes: `docs/usage/daylight_sensor.md`, `docs/usage/led_display.md`

## Change history

- 2026-11-21: remade and renamed. The digit packing is now one shared routine (shorter, same output).

## Status

Functional (author's label from before the remake; re-test in-game).
