# solar_panels_track_sun

Points every movable solar panel on the network at the sun, using one **Daylight Sensor**.
Panels are found by type and name, so you never wire them to pins. Name each panel
`0`, `90`, `180` or `270` after the way its data port faces.

*Replaces `solar_named_tracking`, which was removed from the repo on 2026-06-01 by
mistake (in a satellite clean-up commit). Panels named for the old script work unchanged.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Daylight Sensor |

Solar panels are not pins. They are found on the data network by type and exact name.

## Panel types

| Panel | Prefab | Hash |
| --- | --- | --- |
| Solar Panel | `StructureSolarPanel` | `-2045627372` |
| Solar Panel (Heavy) | `StructureSolarPanelReinforced` | `-934345724` |
| Solar Panel (Dual) | `StructureSolarPanelDual` | `-539224550` |
| Solar Panel (Heavy Dual) | `StructureSolarPanelDualReinforced` | `-1545574413` |
| Solar Panel 1x5 | `StructureSolarPanel1x5` **(guess)** | `939649277` |
| Solar Panel 1x5 (Heavy) | `StructureSolarPanel1x5Reinforced` **(guess)** | `1945473703` |

The first four come from the game's prefab data. The 1x5 names are guesses that follow
the game's naming. If your 1x5 panels don't move, read their real hash (see
[Setup](#setup)) and replace `P_1X5` / `P_H1X5`. A wrong guess is harmless: those lines
then match nothing.

Angled and Flat panels are not included: they are built in a fixed pose.

## Panel names

Rename each panel to the world direction its **data port** faces:

| Name | Data port faces |
| --- | --- |
| `0` | north |
| `90` | east |
| `180` | south |
| `270` | west |

**1x5 panels are built flipped** (confirmed in-game): for them the name is the opposite
way, so a 1x5 named `0` has its data port facing south (180). Name all panels by the
table above as if they were normal panels; the script adds the half turn for 1x5 types.

Names are exact: `90` works, `90 ` or `East` does not. Panels with any other name are
left alone, so you can keep fixed panels on the same network.

## What it does

- Every tick it reads the sun's `Horizontal` and `Vertical` from the sensor.
- It works out each group's panel angle:
  - horizontal = sun direction + 270 − group name;
  - vertical = 90 − sensor `Vertical` (the sun's height above the horizon), kept
    within 15–90.
- It writes to every panel type in all four groups in the same tick.
- Panels are only re-aimed when the sun has moved more than `STEP` degrees. Every
  `RESEND` ticks they are re-aimed anyway, so new or renamed panels join within
  10 seconds.
- **Night:** panels keep following the sun below the horizon at their lowest tilt (15),
  so at sunrise they already face it. No night settings are needed.
- If the sensor is switched off, the script switches it on.
- If the sensor is unplugged or the device on `d0` is not a Daylight Sensor, panels stay
  where they are and the status shows 9. The chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `solar_panels_track_sun.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `SENSOR_PORT` | `0` | Which way the sensor's data port faces (`0`/`90`/`180`/`270`). Change it if all panels point the wrong way |
| `STEP` | `0.5` | Degrees the sun must move before panels are re-aimed |
| `RESEND` | `20` | Ticks between forced re-aims (20 = 10 s) |
| `P_1X5`, `P_H1X5` | see above | 1x5 panel hashes |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `1` | day: sun above the horizon |
| `2` | night: panels waiting, facing the sun below the horizon |
| `9` | Daylight Sensor missing, or `d0` is a different device |

## Setup

1. Build the Daylight Sensor **flat, facing up**, and connect it, the panels and the IC
   Housing to one data network.
2. Rename every panel `0`, `90`, `180` or `270` (see [Panel names](#panel-names)).
3. Set `d0` to the Daylight Sensor.
4. Paste `solar_panels_track_sun.ic10` into the chip and run it.
5. Calibrate. Check at midday that the panels face the sun.
   - If **every** panel is off by the same quarter or half turn, set `SENSOR_PORT` to
     the way the sensor's data port faces.
   - If only **one panel type** is off (for example only Dual panels), its data port sits
     elsewhere on the panel. Rename those panels to the next number round (`0` → `90`
     → `180` → `270`) until they line up. No code change is needed.

To read a panel's real hash (for the 1x5), put the panel on `d0` of a spare chip and run
`l r0 d0 PrefabHash` then `s db Setting r0`. The housing shows the number.

## Notes

- Do you still need the Daylight Sensor? Yes. It is the only device that reports where
  the sun is, and IC10 has no clock. Without it a chip can only search by trial and
  error on panel output, which is slower, loses the sun overnight and is fooled by
  storms.
- The maths is the old `solar_named_tracking` script's, which was marked Functional.
  Panel `Horizontal` is a local angle with the data port at 270 (game data); sensor
  `Vertical` is taken as degrees from straight up.
- Changes from the old script:
  - `SENSOR_DIR_Q` (quarter turns) is now `SENSOR_PORT` (degrees).
  - `H_BIAS`, `V_BIAS`, `H_INV` and the night-park offsets are gone.
  - Status 901 is now 9.
  - At night panels follow the sun instead of parking at a fixed angle.
  - Dual and 1x5 panels were added; 1x5 panels get a half-turn offset (they are flipped).
- Device notes: `docs/usage/daylight_sensor.md`, `docs/usage/solar_panels.md`

## Change history

- 2026-11-21: new script, rebuilt from `solar_named_tracking`. Adds Dual and 1x5
  panels, follows the sun at night, re-aims only on change with a periodic re-send,
  checks the sensor every loop, and keeps the panel naming.
- 2026-11-21: 1x5 and Heavy 1x5 panels are flipped in-game (name `0` = data port at
  180), so their `Horizontal` is turned 180°.

## Status

Functional (author's label; the maths matches the old Functional script).
This version has been simulated, not yet run in-game.
