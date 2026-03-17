# pipe_pressure_active_vent

## Purpose

Reads a **Pipe Analyzer** for gas pipe pressure and batch-drives a **named group of Active Vents on the same data network**:

- If pipe pressure is below the configured fill threshold, turn the vent group **ON** in
  **room → pipe** mode
- Once the pipe reaches the target pressure, turn the vent group **OFF**

The check runs every **1 second** when idle.

While active, the script periodically re-applies the batch vent configuration so testing is easy
even if a vent gets bumped out of sync.

## Devices

Required:

- 1× Pipe Analyzer
- 1+ × Active Vent on the same data network

## Device registers

- `d0` = Pipe Analyzer

Suggested in-game names (optional):

- Pipe Analyzer: `pipe_sensor_1`
- Active Vents: rename every controlled vent exactly to `PIPE_VENT`

## Tuning

Edit the `define` constants at the top of `pipe_pressure_active_vent.ic10`:

- `TARGET_PRESSURE_MPA` (default `10`)
- `HYSTERESIS_KPA` (default `100`)
- `LOOP_SLEEP_S` (default `1`)
- `REAPPLY_TICKS` (default `12`)
- `VENT_NAME_HASH` (default `HASH("PIPE_VENT")`)

## Notes

- Pipe Analyzer `Pressure` is already in **kPa**.
- `TARGET_PRESSURE_MPA` is converted to kPa in the script (`1 MPa = 1000 kPa`).
- The script batch-targets Active Vents using:
  - prefab hash `-1129453144` (`StructureActiveVent`)
  - exact name hash `HASH("PIPE_VENT")`
- Rename every vent you want controlled to exactly `PIPE_VENT`.

The script uses one Active Vent mode constant:

- `MODE_FILL = 1` → Inward (`room → pipe`) in the current repo convention

If your build uses the opposite mapping, change `MODE_FILL` to `0`.

The script sets these Active Vent parameters (after setting `Mode`; changing `Mode`
can reset the vent's extra pressure-limit fields to defaults):

- `Setting = target pipe pressure in kPa`
- `Open = 1`
- `On = 1`

The real stop condition is still the **Pipe Analyzer pressure**. The vent `Setting` is written
to match the same target so the vent and analyzer are aiming at the same number.

Troubleshooting if it “does nothing”:

- Make sure every Active Vent you want controlled is on the **same data network** as the IC.
- Make sure every target vent is named exactly `PIPE_VENT`.
- Make sure the Pipe Analyzer is powered and connected to the pipe network you want to monitor.
- This script assumes the vented room is the **gas source** for the pipe.
  - If the room is near vacuum, `room → pipe` cannot fill the pipe.
- If pressure keeps flickering near the target, increase `HYSTERESIS_KPA`.
- If pressure changes in the wrong direction, change `MODE_FILL` in
  `pipe_pressure_active_vent.ic10`.

Status: **Functional**
