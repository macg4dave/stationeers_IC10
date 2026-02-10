# large_satellite_dish_random_scan

**Status:** Functional  
**Category:** Controller

## Purpose

Press a **Logic Switch (Button)** to start a scan cycle:

- When the dish is **Idle**, it moves to a random **Horizontal/Vertical**.
- After each move (once **Idle** again), it checks **SignalID**:
  - If a signal is found, scanning stops and the dish stays pointed.
  - If no signal is found, it picks another random point and tries again.

## Devices

Required:

- 1x **Large Satellite Dish**
- 1x **Logic Switch (Button)**
- 1x **IC10** in an IC Housing (recommended so `db Setting` can be used as a tiny status display)

## Device registers

- `d0` = Large Satellite Dish
- `d1` = Logic Switch (Button)

## Usage

1. Wire the dish and the button to the same data network as the IC housing.
2. Set the IC housing screws:
   - `d0` → the Large Satellite Dish
   - `d1` → the Logic Switch (Button)
3. Paste `large_satellite_dish_random_scan.ic10` into the IC.
4. Press the button:
   - First press: scanning toggles **ON**
   - Press again: scanning toggles **OFF** (useful as an abort)

When a signal is found, the script stops scanning automatically and writes the found `SignalID` to `db Setting` (so you can see it on the IC housing).

## Tuning

In `large_satellite_dish_random_scan.ic10`:

- `H_MIN`, `H_MAX` — horizontal angle range (inclusive)
- `V_MIN`, `V_MAX` — vertical angle range (inclusive)
  - Default vertical range is `0..89` to focus on “above the horizon”. Adjust if you want to scan lower/higher.
- `TARGET_SIGNAL_ID`
  - `0` = stop on **any** non-zero `SignalID`
  - non-zero = stop only if the dish reports that exact `SignalID`

## Notes / gotchas

- The button is momentary: `Activate` briefly becomes `1` when pressed. This script treats that as a **toggle**.
- If the dish isn’t powered (`Power == 0`) or is in an error state (`Error == 1`), scanning waits.
