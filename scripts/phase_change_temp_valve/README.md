# phase_change_temp_valve

## Purpose

Open a Pipe Digital Valve when a phase_change_device temperature is above 30°C.

This version controls Pipe Digital Valves named `cold` on the same data network as the IC housing.

## Devices

- **Required:**
  - phase_change_device (temperature source)
  - One or more Pipe Digital Valves named `cold` (controlled valves)

## Device registers

- `d0` = phase_change_device

## Usage

1) Assign the phase_change_device to `d0`.
2) Ensure any target Pipe Digital Valves are named exactly `cold` and are on the same data network as this IC housing.
3) Paste `phase_change_temp_valve.ic10` into an IC chip and run it.

### Hash behavior used by this script

- Type filter uses Pipe Digital Valve prefab hash: `-1280984102`.
- Name filter uses `HASH("cold")` (exact/case-sensitive).
- Control writes clear lock before state write (`Lock=0` then `On=<0|1>`).

If the script seems to find no valves, first verify exact rename (`cold`) and data-network connection.

## Tuning

- `TEMP_OPEN_ABOVE_C` (°C): open valve when temperature is strictly above this value.

## Status

Functional
