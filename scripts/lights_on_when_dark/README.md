# lights_on_when_dark

Turns every light on the data network **on when it gets dark** and **off when it gets
light**, using one **Daylight Sensor**. Lights are found by type, so you never wire them
to pins or rename them.

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Daylight Sensor |

The sensor can be the one your solar tracker already uses: point both chips' `d0` at it.

## Light types

| Light | Prefab | Hash |
| --- | --- | --- |
| Wall Light | `StructureWallLight` | `-1860064656` |
| Wall Light (Battery) | `StructureWallLightBattery` | `-1306415132` |
| Wall Light (Long) | `StructureLightLong` | `797794350` |
| Wall Light (Long Angled) | `StructureLightLongAngled` | `1847265835` |
| Wall Light (Long Wide) | `StructureLightLongWide` | `555215790` |
| Light Round | `StructureLightRound` | `1514476632` |
| Light Round (Angled) | `StructureLightRoundAngled` | `1592905386` |
| Light Round (Small) | `StructureLightRoundSmall` | `1436121888` |

The prefab names are not confirmed in-game: they are not in the repo's catalog. If a
light type doesn't switch, read its real hash (see [Setup](#setup)) and replace its
`L_*` define. A wrong hash is harmless: that line then matches nothing.

Grow lights, LEDs and consoles are not touched.

## What it does

- Reads the sun's `Vertical` from the sensor. Sun height above the horizon is
  `90 − Vertical`.
- Lights **ON** when the sun is under 5° above the horizon (dusk, night).
- Lights **OFF** when the sun is over 10° above the horizon (morning, day).
- Between 5° and 10° nothing changes, so the lights don't flicker at dusk and dawn.
- Each loop it reads every light type and writes only if a light differs. A light
  switched by hand, or a new light, is put back to the right state within a tick.
- If the sensor is switched off, the script switches it on.
- If the sensor is unplugged or `d0` is a different device, the lights stay as they are
  and the status shows 9. The chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `lights_on_when_dark.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `ON_BELOW` | `5` | Lights on when the sun is lower than this (degrees above the horizon) |
| `OFF_ABOVE` | `10` | Lights off when the sun is higher than this (degrees) |
| `L_*` | see above | Light prefab hashes |

Raise both numbers to switch the lights on earlier in the evening.

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | day: lights off |
| `1` | dark: lights on |
| `9` | Daylight Sensor missing, or `d0` is a different device |

## Setup

1. Build the Daylight Sensor **flat, facing up**, and connect it, the lights and the IC
   Housing to one data network. The sensor needs power.
2. Set `d0` to the Daylight Sensor.
3. Paste `lights_on_when_dark.ic10` into the chip and run it.

To read a light's real hash, put the light on `d0` of a spare chip and run
`l r0 d0 PrefabHash` then `s db Setting r0`. The housing shows the number.

## Notes

- It goes by the sun's position, not by how bright it is. Storms, rooms with no windows
  and planets with long dark spells are not detected; the lights follow the sun only.
- Sensor `Vertical` is taken as degrees from straight up, as in `solar_panels_track_sun`
  (which works in-game). Sun on the horizon = 90.
- Device notes: `docs/usage/daylight_sensor.md`

## Change history

- 2026-11-22: new script.

## Status

Functional. Simulated, not run in-game.
