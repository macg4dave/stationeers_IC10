# large_satellite_dish_sweep_scan

**Status:** Functional  
**Category:** Controller

## Purpose

Button toggles a deterministic sweep:

- Steps Horizontal by `H_STEP`; when hitting an edge, flips direction and steps Vertical by `V_STEP`.
- After each move, waits for `Idle` and pauses 1 second before checking for signals.
- Wraps Vertical after `V_MAX` back to `V_MIN` and keeps sweeping.
- Stops when a Signal is detected (SignalID match or SignalStrength threshold).
- In any-signal mode, auto-locks `BestContactFilter` to the first new detected `SignalID`.
- If the locked signal is lost for several scans, clears filter and resumes broad sweep.

## Devices

Required:

- 1x **Large Satellite Dish**
- 1x **Logic Switch (Important Button)**
- 1x **IC10** in an IC Housing (for `db Setting` status)

## Device registers

- `d0` = Large Satellite Dish
- `d1` = Logic Switch (Important Button)

## Usage

1. Wire dish + important button to the IC housing data network.
2. Set screws: `d0` → dish, `d1` → important button.
3. Paste `large_satellite_dish_sweep_scan.ic10` into the IC.
4. Press button: toggle scanning ON/OFF.

When it stops, it writes the found `SignalID` to `db Setting` and leaves the dish pointed there.

## Tuning

In `large_satellite_dish_sweep_scan.ic10`:

- `H_MIN/H_MAX`, `V_MIN/V_MAX` — sweep bounds (inclusive).
- `H_STEP`, `V_STEP` — sweep increments (set to `10` by default).
- `TARGET_SIGNAL_ID`
  - `0` = stop on any non-zero `SignalID`
  - non-zero = require exact match; sets `BestContactFilter` to that value while scanning
- `REACQUIRE_MISSES`
  - used when `TARGET_SIGNAL_ID = 0`
  - if signal is missing for this many scan checks while locked, clears `BestContactFilter` back to `-1`
- `STOP_ON_STRENGTH`, `SIGNAL_STRENGTH_STOP`
  - enable/disable strength-based stop and set threshold (SignalStrength ≥ threshold).
  - Strength checks only apply when a non-zero `SignalID` is present.

## Notes / gotchas

- The important button is momentary; each press toggles scanning.
- BestContactFilter behavior:
  - `TARGET_SIGNAL_ID != 0`: filter is fixed to target while scanning.
  - `TARGET_SIGNAL_ID = 0`: filter auto-locks to first new hit, then clears to `-1` after `REACQUIRE_MISSES` misses.
- For large dishes, `SignalStrength` is typically negative; use a threshold like `-10` to start.
- The sweep keeps its position/direction while the IC is running; restarting the chip resets to `H_MIN/V_MIN`.
