# room_pressure_active_vent

## Purpose

Reads a **Gas Sensor** for room pressure and drives an **Active Vent** mode:

- If **Pressure < 90 kPa** → set vent to **Intake** mode and turn it **On**
- If **Pressure > 120 kPa** → set vent to **Exhaust** mode and turn it **On**
- Otherwise (90–120 kPa) → **do nothing** (leave vent settings unchanged)

The check runs every **5 seconds**.

While the vent is actively changing pressure, the script sets `Lock = 1` and keeps it
locked until the room reaches the target pressure (then it turns the vent off and
unlocks it).

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
- `LOOP_SLEEP_S` (default `5`)

## Notes

- Pressure is in **kPa**.
- Active Vent `Mode` values:
  - `0` = Outward (pipe → room) — pressurize / “intake”
  - `1` = Inward (room → pipe) — depressurize / “exhaust”

The script also sets these Active Vent parameters (after setting `Mode`, because
changing `Mode` resets the pressures to defaults):

- `PressureExternal` to the target room pressure (`LOW_PRESSURE_KPA` or `HIGH_PRESSURE_KPA`)
- `PressureInternal` to a pipe constraint (`MIN_PIPE_PRESSURE_KPA` or `MAX_PIPE_PRESSURE_KPA`)

Status: **Functional**
