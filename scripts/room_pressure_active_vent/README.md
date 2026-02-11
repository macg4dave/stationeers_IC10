# room_pressure_active_vent

## Purpose

Reads a **Gas Sensor** for room pressure and drives an **Active Vent** mode:

- If **Pressure < 90 kPa** → set vent to **Intake** mode and turn it **On**
- If **Pressure > 120 kPa** → set vent to **Exhaust** mode and turn it **On**
- Otherwise (90–120 kPa) → keep the current state (see below)

The check runs every **1 second** when idle.

While the vent is actively changing pressure, the script sets `Lock = 1` and keeps it
locked until the room reaches the opposite threshold:

- Intake continues until **HIGH_PRESSURE_KPA**
- Exhaust continues until **LOW_PRESSURE_KPA**

Then it turns the vent off and unlocks it.

This script also includes a small timing workaround for some builds: it writes vent
`Mode`, waits **one tick** (`yield`), then writes the pressure/setpoint fields.

## Devices

Required:

- 1× Gas Sensor
- 1× Active Vent

## Device registers

- `d0` = Gas Sensor
- `d1` = Active Vent

Suggested in-game names (optional):

- Gas Sensor: `room_sensor_1`
- Active Vent: `room_vent_1`

## Tuning

Edit the `define` constants at the top of `room_pressure_active_vent.ic10`:

- `LOW_PRESSURE_KPA` (default `90`)
- `HIGH_PRESSURE_KPA` (default `120`)
- `MIN_PIPE_PRESSURE_KPA` (default `10`)
- `MAX_PIPE_PRESSURE_KPA` (default `60000`)
- `LOOP_SLEEP_S` (default `1`)

## Notes

- Pressure is in **kPa**.
- If the Gas Sensor reports a value that looks like **Pa** (e.g. ~101000), the script
  auto-normalizes to kPa.
- Active Vent `Mode` values:
  - `0` = Outward (pipe → room) — pressurize / “intake”
  - `1` = Inward (room → pipe) — depressurize / “exhaust”

The script sets these Active Vent parameters (after setting `Mode`; changing `Mode`
can reset pressures to defaults):

- `Setting` to the target room pressure (`LOW_PRESSURE_KPA` or `HIGH_PRESSURE_KPA`)
- `PressureExternal` to the target room pressure (`LOW_PRESSURE_KPA` or `HIGH_PRESSURE_KPA`)
- `PressureInternal` to a pipe constraint (`MIN_PIPE_PRESSURE_KPA` or `MAX_PIPE_PRESSURE_KPA`)

Troubleshooting if it “does nothing”:

- For **intake/pressurize** (Mode `0`, pipe → room): ensure the pipe network pressure is
  above your target room pressure (e.g. > `LOW_PRESSURE_KPA`).
- For **exhaust/depressurize** (Mode `1`, room → pipe): ensure the pipe network has
  somewhere for gas to go (tank/storage/active vent to space) and isn't already maxed.
- Ensure the vent face is inside the room you want to pressurize.
- Double-check chip device assignments: `d0` is the Gas Sensor, `d1` is the Active Vent.

Status: **Functional**
