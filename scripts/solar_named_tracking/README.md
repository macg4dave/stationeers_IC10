# solar_named_tracking

**Purpose:**
Tracks all Solar Panels on the same data network using one Daylight Sensor and exact
panel-name groups. During the day, each group's name is used as a horizontal offset.
At night, each group parks back to its own starting angle.

## Devices

- **Required:** 1 Daylight Sensor, 1 or more Solar Panels on the same data network
- **Optional:** None

## Device registers

- `d0` = Daylight Sensor

## Exact panel names supported

Rename each Solar Panel to one of these exact values:

- `0`
- `90`
- `180`
- `270`

All panels sharing the same exact name will move together as one group.

These map to the game's four practical facing directions:

- `0` = north
- `90` = east
- `180` = south
- `270` = west

> **Important:** IC10 cannot read arbitrary device name text from the network.
> This script works by targeting known exact `HASH("name")` values with `sbn`.
> This repo assumes the game's supported Solar Panel facing directions are the
> four cardinal directions only. Do not use diagonal name groups here.

## How the naming works

- **Daytime:** group angle = `sun horizontal + name`
- **Night:** group angle = `name`

Examples:

- A panel named `0` tracks with no extra horizontal offset and parks at `0`.
- A panel named `90` tracks with a +90° horizontal offset and parks at `90`.

This is useful when different panel groups need different cardinal horizontal
offsets or when you want a predictable night parking direction per group.

## Usage

1. Place and power a Daylight Sensor and connect it to the same data network as the IC.
2. Mount the Daylight Sensor **flat / facing up** as the default setup.
3. Rename each Solar Panel to one of the supported exact names above.
4. Put the Daylight Sensor on `d0`.
5. Paste `solar_named_tracking.ic10` into the IC.
6. If tracking is rotated, adjust `SENSOR_PORT_DIRECTION` in 90° steps.
7. If needed, fine-tune `HORIZONTAL_BIAS_DEG` and `VERTICAL_BIAS_DEG`.

## Tuning

- `SENSOR_PORT_DIRECTION`: sensor connector direction in quarter-turns (`0..3`).
- `HORIZONTAL_BIAS_DEG`: extra horizontal trim in degrees.
- `HORIZONTAL_INVERT`: set to `1` if horizontal motion runs backward.
- `VERTICAL_BIAS_DEG`: extra vertical trim in degrees.
- `NIGHT_THRESHOLD_DEG`: below this computed panel elevation, the script parks for night.
- `NIGHT_PARK_VERTICAL`: night park elevation (default `15`).

## Debug / status

The IC Housing `db Setting` shows:

- `1` = daytime tracking
- `2` = night parking
- `901` = `d0` is not a Daylight Sensor

## Notes

- This script assumes the Daylight Sensor's `Vertical` behaves like a zenith angle,
  so the panel target elevation is computed as `90 - sensor Vertical`.
- Solar Panel writes are batch-targeted by prefab hash and exact name hash.
- See `docs/usage/daylight_sensor.md` and `docs/usage/solar_panels.md`.

## Status

Functional
