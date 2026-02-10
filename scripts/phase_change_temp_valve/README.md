# phase_change_temp_valve

## Purpose

Open a Pipe Digital Valve when a phase_change_device temperature is above 30°C.

## Devices

- **Required:**
  - phase_change_device (temperature source)
  - Pipe Digital Valve (controlled valve)

## Device registers

- `d0` = phase_change_device
- `d1` = Pipe Digital Valve

## Usage

1) Assign the phase_change_device to `d0`.
2) Assign the Pipe Digital Valve to `d1`.
3) Paste `phase_change_temp_valve.ic10` into an IC chip and run it.

## Tuning

- `TEMP_OPEN_ABOVE_C` (°C): open valve when temperature is strictly above this value.

## Status

Functional
