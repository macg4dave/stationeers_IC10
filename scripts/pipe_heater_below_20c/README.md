# pipe_heater_below_20c

## Purpose

Read a **Pipe Analyzer** and turn a **Pipe Heater** **ON** when pipe temperature is below **20°C**.

If the pipe is **20°C or warmer**, the script turns the heater **OFF**.

## Devices

Required:

- Pipe Analyzer
- Pipe Heater

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Pipe Heater

## Usage

1. Place the Pipe Analyzer on the pipe network you want to monitor.
2. Place the Pipe Heater on the pipe network you want to heat.
3. Make sure both devices are powered and on the same data network as the IC Housing.
4. (Recommended) Rename devices so they are easy to assign:
   - Pipe Analyzer: `pipe_heat_1_read`
   - Pipe Heater: `pipe_heat_1_heater`
5. In the IC Housing, assign:
   - `d0` = `pipe_heat_1_read`
   - `d1` = `pipe_heat_1_heater`
6. Paste `pipe_heater_below_20c.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `pipe_heater_below_20c.ic10`:

- `HEAT_ON_BELOW_C` (°C): heater is forced **ON** when `tempC < HEAT_ON_BELOW_C`

Temperature notes:

- Pipe Analyzer `Temperature` is reported in Kelvin (K).
- The script converts to Celsius using $C = K - 273.15$.
- If the Pipe Analyzer reports `Error != 0`, the heater is forced **OFF**.

## In-game setup notes

- See `docs/usage/pipe_analyzer.md` for Pipe Analyzer setup and reading gotchas.
- See `docs/usage/pipe_heater.md` for Pipe Heater setup notes.
- This script only toggles `On` on the heater.

## Status

Functional.
