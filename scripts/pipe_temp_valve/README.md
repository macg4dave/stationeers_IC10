# pipe_temp_valve

## Purpose

Open/close a **Pipe Digital Valve** based on pipe temperature from a **Pipe Analyzer**, using simple hysteresis (Schmitt-trigger style).

## Devices

Required:

- Pipe Analyzer
- Pipe Digital Valve

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Pipe Digital Valve

## Usage

1. Place the Pipe Analyzer on the pipe network you want to monitor.
2. Place a Pipe Digital Valve on the pipe network you want to control.
3. (Recommended) Rename the devices so they’re easy to pick in the IC housing UI:
   - Pipe Analyzer: `read_pipe_temp_1`
   - Pipe Digital Valve: `read_pipe_temp_1_valve`
4. In the IC housing, assign:
   - `d0` = `read_pipe_temp_1`
   - `d1` = `read_pipe_temp_1_valve`
5. Copy/paste `pipe_temp_valve.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `pipe_temp_valve.ic10`:

- `TEMP_OPEN_BELOW_C` (°C): valve is forced **open** when `tempC < TEMP_OPEN_BELOW_C`
- `TEMP_CLOSE_ABOVE_C` (°C): valve is forced **closed** when `tempC > TEMP_CLOSE_ABOVE_C`

Temperature notes:

- The Pipe Analyzer reports `Temperature` in Kelvin (K).
- The script converts to Celsius using: $C = K - 273.15$.

## Status

Functional.

## Credit

Hysteresis pattern is the common IC10 “Schmitt trigger” approach (see the IC10 wiki examples).
