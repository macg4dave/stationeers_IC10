# room_pressure_active_vent

## Purpose

Reads a **Gas Sensor** for room pressure and batch-drives a **named group of Active Vents on the same data network**:

- If **Pressure < 90 kPa** → set vent to **Intake** mode and turn it **On**
- If **Pressure > 120 kPa** → set vent to **Exhaust** mode and turn it **On**
- Otherwise (90–120 kPa) → keep the current state (see below)

The check runs every **1 second** when idle.

While the vents are actively changing pressure, the script sets `Lock = 1` and keeps them
locked until the room reaches the opposite threshold:

- Intake continues until **HIGH_PRESSURE_KPA**
- Exhaust continues until **LOW_PRESSURE_KPA**

Then it turns the vent off and unlocks it.

This script also includes a small timing workaround for some builds: it writes vent
`Mode`, waits **one tick** (`yield`), then writes the main setpoint/state fields.

While active, it periodically re-applies the batch vent configuration so testing is easy
even if a vent gets bumped out of sync.

## Devices

Required:

- 1× Gas Sensor
- 1+ × Active Vent on the same data network

## Device registers

- `d0` = Gas Sensor

Suggested in-game names (optional):

- Gas Sensor: `room_sensor_1`
- Active Vents: rename every controlled vent exactly to `ROOM_VENT`

## Tuning

Edit the `define` constants at the top of `room_pressure_active_vent.ic10`:

- `LOW_PRESSURE_KPA` (default `90`)
- `HIGH_PRESSURE_KPA` (default `120`)
- `LOOP_SLEEP_S` (default `1`)
- `REAPPLY_TICKS` (default `12`)
- `VENT_NAME_HASH` (default `HASH("ROOM_VENT")`)

## Notes

- Pressure is in **kPa**.
- If the Gas Sensor reports a value that looks like **Pa** (e.g. ~101000), the script
  auto-normalizes to kPa.
- The script batch-targets Active Vents using:
  - prefab hash `-1129453144` (`StructureActiveVent`)
  - exact name hash `HASH("ROOM_VENT")`
- Rename every vent you want controlled to exactly `ROOM_VENT`.
- Active Vent `Mode` values:
  - `0` = Outward (pipe → room) — pressurize / “intake”
  - `1` = Inward (room → pipe) — depressurize / “exhaust”
  - If your vent moves gas in the wrong direction, swap `MODE_OUTWARD` and
    `MODE_INWARD` in the script. Some builds/mod setups appear to invert this.

The script sets these Active Vent parameters (after setting `Mode`; changing `Mode`
can reset the vent's extra pressure-limit fields to defaults):

- `Setting` to the target room pressure in **kPa**
- `Open` to `1`
- `On` to `1`

It intentionally does **not** force `PressureExternal` / `PressureInternal`.
For this manual-style controller, those fields are left at the vent's mode defaults.

Troubleshooting if it “does nothing”:

- Make sure every Active Vent you want controlled is on the **same data network** as the IC.
- Make sure every target vent is named exactly `ROOM_VENT`.
- IC10 batch writes (`sb`/`sbn`) use the device **Prefab Hash**, not the item hash.
- `Power` is not a command you can force from IC10; it reflects whether the vent has real
  electrical power. If `Power = 0`, check the vent's cable/power network first.
- If you inspect a manually working vent and see values like `PressureExternal = 0`,
  `PressureInternal = 50662.5`, `Setting = 50`, that points to `Setting` being the useful
  control target for this script while the other pressure fields are left alone.
- For **intake/pressurize** (Mode `0`, pipe → room): ensure the pipe network pressure is
  above your target room pressure (e.g. > `LOW_PRESSURE_KPA`).
- For **exhaust/depressurize** (Mode `1`, room → pipe): ensure the pipe network has
  somewhere for gas to go (tank/storage/active vent to space) and isn't already maxed.
- Unrelated Active Vents on the same network will be ignored unless they also use the exact
  name `ROOM_VENT`.
- If pressure changes in the **wrong direction**, swap the `MODE_OUTWARD` /
  `MODE_INWARD` constant values in `room_pressure_active_vent.ic10`.
- Ensure the vent face is inside the room you want to pressurize.
- Double-check chip device assignments: `d0` is the Gas Sensor.

Status: **Functional**
