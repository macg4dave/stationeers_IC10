# display_clock_from_sun

A 24-hour clock on two **LED Displays** (hours and minutes), worked out from the sun's position seen by a **Daylight Sensor**.

*Previously called `led_display_hms_clock`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | LED Display (hours) |
| `d1` | LED Display (minutes) |
| `d2` | *(optional)* a second Daylight Sensor **on a wall**, to test the wall guess |
| `d3` | Daylight Sensor, **flat, facing up** |

Watch the pins: the sensor is on `d3` here, not `d0` as in the solar and light scripts.
With the sensor on `d0` the chip stops with an error when it writes the hours.

## What it does

- Works out how far the sun is along its daily path from both sensor angles
  (`Horizontal` and `Vertical`):
  - sun rising (in the direction the sensor reads `RISE_DEG`): **06:00**
  - sun at its highest: **12:00**
  - sun setting: **18:00**
  - sun at its lowest: **00:00**
- Works whether the sun passes straight overhead or on a tilted path.
- Checks that `d3` really is a Daylight Sensor, and switches it on if it is off.
- Displays kept On in Mode 10 (two-character text), written only when the value changes.
  The chip remembers what it last wrote, so it does not read the displays back.
- Every pin is also checked inside the main loop: unplug a device and the chip waits
  instead of halting. The displays keep the last time while it waits.

## Wall sensor check (`d2`)

With a wall-mounted Daylight Sensor on `d2`, the clock still runs from the flat sensor,
and the housing shows **how far the wall guess is off**: the wall sensor's sun height
(the guess from `lights_on_when_dark`, `asin(sin(V) × cos(H + WALL_TURN))`) minus the
flat sensor's sun height, in whole degrees.

- `0` (or ±1): the guess and `WALL_TURN` are right at this time of day.
- A large number: try another `WALL_TURN` (`0`, `90`, `180`, `270`).
- Check at a few times of day (morning, midday, evening, night): a right guess stays
  near 0 all day.

At sunrise on 2026-11-22 your two sensors read flat H 4 / V 81 and wall H 22 / V 171:
the housing would show `-1` with `WALL_TURN 0`.

While a wall sensor is on `d2` the housing shows this number instead of the status, so
`1` and `9` can be a difference too. Clear `d2` to get the status back. A device on `d2`
that is not a Daylight Sensor is ignored.

## Settings

Edit the `define` lines at the top of `display_clock_from_sun.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `RISE_DEG` | `0` | The sensor's `Horizontal` reading when the sun rises |
| `SHIFT_MIN` | `0` | Moves the clock by whole minutes |
| `WALL_TURN` | `0` | Wall sensor on `d2` only: the guess's turn, as in `lights_on_when_dark` |

To calibrate: read the sensor's `Horizontal` at sunrise and put it in `RISE_DEG`.
Then use `SHIFT_MIN` if you want sunrise to show a time other than 06:00.

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `1` | running |
| `9` | a display is missing, or `d3` is missing or not a Daylight Sensor |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
   Build the Daylight Sensor **flat, facing up**.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `display_clock_from_sun.ic10` into the chip and run it.

## Notes

- The sensor stays on `d3` (the original wiring); `d2` is the optional wall sensor.
- This is game-sun time, not real time: 06:00 is when the sun rises, whatever the
  planet's day length.
- In-game at sunrise (2026-11-22), with the sensor flat and its top to 0, the sensor
  read `Horizontal` 4, `Vertical` 81. That is about 9° above the horizon, so this
  clock shows 06:39, and `RISE_DEG 0` fits that world.
- Device notes: `docs/usage/daylight_sensor.md`, `docs/usage/led_display.md`

## Change history

- 2026-11-22: optional wall-mounted sensor on `d2`: the housing shows how far the wall
  guess is from the flat sensor, to test `WALL_TURN` in-game. Code compressed to fit
  128 lines (same time shown).
- 2026-11-22: the time now comes from the sun's angle along its path (`Horizontal` and
  `Vertical`), not from `Horizontal` alone. In-game the old clock showed 00:08–00:12 at
  sunrise and barely moved: on a steep sun path the compass direction hardly changes
  all morning. `SENSOR_DIRECTION`, `OFFSET_DEG` and `INVERT` are replaced by `RISE_DEG`.
- 2026-11-22: remembers the last value written to each display instead of reading
  `Setting` back (one read fewer per display).
- 2026-11-22: checks `d3` is a Daylight Sensor (`PrefabHash`), switches the sensor on,
  and shows a status on the housing (1 running, 9 missing).
- 2026-11-21: remade and renamed. The digit packing is now one shared routine (shorter, same output).

## Status

Functional (author's label from before the remake). The new time maths is simulated,
not yet run in-game.
