# lights_on_when_dark

Turns every light on the data network **on at 18:00** and **off at 06:30**, in the same
sun time that `display_clock_from_sun` shows, using one **Daylight Sensor**. Lights are
found by type, so you never wire them to pins or rename them.

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Daylight Sensor, **flat, facing up** (or on a wall with `WALL 1`) |

The sensor can be the one your clock or solar tracker already uses: point this chip's
`d0` at it.

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

- Works out the sun time exactly like `display_clock_from_sun`: how far the sun is along
  its path, from the sensor's `Horizontal` and `Vertical`. Sunrise is 06:00, the sun's
  highest point 12:00, sunset 18:00.
- Lights **ON** from `ON_AT` to `OFF_AT` (default 18:00 to 06:30), **OFF** otherwise.
  The period can cross midnight (18:00–06:30) or not (01:00–05:00).
- No dead band is needed: the time passes each switching point once a day, so the
  lights do not flicker the way a "sun below 5°" threshold could.
- Each loop it reads every light type and writes only if a light differs. A light
  switched by hand, or a new light, is put back to the right state within a tick.
- If the sensor is switched off, the script switches it on.
- If the sensor is unplugged or `d0` is a different device, the lights stay as they are
  and the status shows 9. The chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `lights_on_when_dark.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `ON_AT` | `1800` | Lights on at this sun time, as HHMM (`1800` = 18:00) |
| `OFF_AT` | `630` | Lights off at this sun time, as HHMM (`630` = 06:30) |
| `RISE_DEG` | `0` | Sensor `Horizontal` at sunrise. **Same value as in the clock** |
| `SHIFT_MIN` | `0` | Moves the sun time by whole minutes. **Same value as in the clock** |
| `WALL` | `0` | `1` = the sensor is on a wall (a guess, see [Wall sensor](#wall-sensor)) |
| `WALL_FACE` | `180` | Wall only: where the sensor faces, in degrees from the sunrise direction |
| `WALL_TURN` | `0` | Wall only: turn for the sensor's `Horizontal` (`0`, `90`, `180`, `270`) |
| `L_*` | see above | Light prefab hashes |

With the same `RISE_DEG` and `SHIFT_MIN` in both scripts, the lights switch exactly when
the clock shows `ON_AT` and `OFF_AT`.

## Wall sensor

`WALL 1` reads a Daylight Sensor mounted on a wall. **This is a guess**, checked against
one pair of in-game readings only. The guess is that a wall sensor reports:

- `Vertical` = the angle between the sun and the way the sensor faces;
- `Horizontal + WALL_TURN` = the angle round that facing, from straight up.

From that the script works out the same sun time as a flat sensor. `RISE_DEG` is not
used with `WALL 1`; `WALL_FACE` takes its place.

At sunrise on 2026-11-22 a flat sensor read H 4 / V 81 (06:39) and a wall sensor read
H 22 / V 171. With `WALL_FACE 180` and `WALL_TURN 0` the wall reading gives 06:36, so
those are the defaults.

To check it: with the clock's optional wall input (`d2`, see `display_clock_from_sun`)
the clock housing shows how far the wall guess is from the flat sensor. Near 0 all day
means the guess holds. If the lights switch at the wrong times with `WALL 1`, try
`WALL_TURN` `180`, then `WALL_FACE` `0`, and send the sensor readings if neither helps.

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | lights off |
| `1` | lights on |
| `9` | Daylight Sensor missing, or `d0` is a different device |

## Setup

1. Build the Daylight Sensor **flat, facing up**, and connect it, the lights and the IC
   Housing to one data network. The sensor needs power.
2. Set `d0` to the Daylight Sensor.
3. Copy `RISE_DEG` and `SHIFT_MIN` from your clock script, if you changed them there.
4. Paste `lights_on_when_dark.ic10` into the chip and run it.

To read a light's real hash, put the light on `d0` of a spare chip and run
`l r0 d0 PrefabHash` then `s db Setting r0`. The housing shows the number.

## Notes

- It goes by the sun's position, not by how bright it is. Storms and rooms with no
  windows are not detected.
- A sensor on a wall reports different angles: use `WALL 1` (a guess, see above).
- Device notes: `docs/usage/daylight_sensor.md`

## Change history

- 2026-11-22: new script.
- 2026-11-22: lights never came on in-game (status stayed 0 at night); a wall-mounted
  sensor is suspected. Added `WALL` / `WALL_TURN` (a guessed conversion) and
  `SHOW_HEIGHT` to test it in-game.
- 2026-11-22: switches by sun time (`ON_AT`/`OFF_AT`, the clock's maths) instead of sun
  height (`ON_BELOW`/`OFF_ABOVE`), at the user's request once the clock worked in-game.
  `WALL`, `WALL_TURN` and `SHOW_HEIGHT` are removed: the wall check now lives in the
  clock (`d2`), and this script needs a flat sensor.
- 2026-11-22: wall sensor support again, now for the sun time: `WALL 1` with
  `WALL_FACE` (default 180) and `WALL_TURN` (default 0), from the in-game sunrise
  readings. A guess until checked over a whole day.

## Status

Functional. Simulated, not run in-game.
