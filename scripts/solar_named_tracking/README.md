# solar_named_tracking

**Purpose:**
Tracks normal and heavy Solar Panels on the same data network using one Daylight Sensor
and exact panel-name groups. Group names represent each panel group's **data-port world
direction**. During the day, the script compensates for that mount direction. At night,
it uses a shared base park angle plus per-group offsets so mixed panel orientations can
be tuned.

## Devices

- **Required:** 1 Daylight Sensor, 1 or more Solar Panels and/or Heavy Solar Panels on
    the same data network
- **Optional:** None

## Device registers

- `d0` = Daylight Sensor

## Exact panel names supported

Rename each Solar Panel or Heavy Solar Panel to one of these exact values based on the
direction its **data port faces in the world**:

- `0`
- `90`
- `180`
- `270`

All panels sharing the same exact name will move together as one group.

These map to the game's four practical data-port directions:

- `0` = north
- `90` = east
- `180` = south
- `270` = west

> **Important:** IC10 cannot read arbitrary device name text from the network.
> This script works by targeting known exact `HASH("name")` values with `sbn`.
> This repo assumes the game's supported Solar Panel facing directions are the
> four cardinal directions only. Do not use diagonal name groups here.

## How the naming works

- Solar Panel `Horizontal` is a **local panel angle**, not a world compass heading.
- The game's Solar Panel docs define the panel data-port side as local `270°`.
- This script treats the group name as the panel's **world** data-port direction and
    compensates for it during daytime tracking.
- Night parking is tuned separately using one shared base angle plus one fixed offset
    per group.

Formulas used:

- **Daytime:** `panel horizontal = sun horizontal + 270 - data-port direction`
- **Night:** `panel horizontal = NIGHT_PARK_BASE_HORIZONTAL + NIGHT_PARK_OFFSET_group`

Default night offsets keep the `270` group as the reference park heading and rotate the
other groups in `90°` steps from that base.

If one group parks correctly and the others are still rotated wrong, adjust only the
`NIGHT_PARK_OFFSET_*` constants in `90°` steps until all groups line up.

## Usage

1. Place and power a Daylight Sensor and connect it to the same data network as the IC.
2. Mount the Daylight Sensor **flat / facing up** as the default setup.
3. Rename each Solar Panel to the exact world direction its **data port** faces.
4. Put the Daylight Sensor on `d0`.
5. Paste `solar_named_tracking.ic10` into the IC.
6. If tracking is rotated, adjust `SENSOR_DIR_Q` in 90° steps.
7. If needed, fine-tune `H_BIAS` and `V_BIAS`.

## Tuning

- `SENSOR_DIR_Q`: sensor connector direction in quarter-turns (`0..3`).
- `H_BIAS`: extra horizontal trim in degrees.
- `H_INV`: set to `1` if horizontal motion runs backward.
- `V_BIAS`: extra vertical trim in degrees.
- `PANEL_PORT_H`: local Solar Panel angle of the data-port side (default `270`).
- `PARK_BASE_H`: reference local horizontal park angle.
- `PARK_OFF_0`, `PARK_OFF_90`, `PARK_OFF_180`, `PARK_OFF_270`:
    fixed night offsets added to the base for each name group.
- `NIGHT_TRIG_V`: below this computed panel elevation, the script parks for night.
- `PARK_V`: night park elevation (default `15`).

## Debug / status

The IC Housing `db Setting` shows:

- `1` = daytime tracking
- `2` = night parking
- `901` = `d0` is not a Daylight Sensor

## Notes

- This script assumes the Daylight Sensor's `Vertical` behaves like a zenith angle,
  so the panel target elevation is computed as `90 - sensor Vertical`.
- The Solar Panel `Horizontal` value is interpreted in the panel's local frame; the
    script compensates using the named data-port direction for each group.
- Night parking is intentionally exposed as base + offsets because different panel
    build conventions can need different quarter-turn corrections.
- Solar Panel and Heavy Solar Panel writes are batch-targeted by prefab hash and exact
    name hash.
- See `docs/usage/daylight_sensor.md` and `docs/usage/solar_panels.md`.

## Status

Functional
