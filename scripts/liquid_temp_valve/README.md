# liquid_temp_valve

## Purpose

Open/close a **Liquid Digital Valve** based on liquid pipe temperature from a **Liquid Pipe Analyzer**, using simple hysteresis (Schmitt-trigger style).

## Devices

Required:

- Liquid Pipe Analyzer
- Liquid Digital Valve

## Device registers

- `d0` = Liquid Pipe Analyzer
- `d1` = Liquid Digital Valve

## Usage

1. Place the Liquid Pipe Analyzer on the liquid pipe network you want to monitor.
2. Place a Liquid Digital Valve on the liquid pipe network you want to control.
3. (Recommended) Rename the devices so they’re easy to pick in the IC housing UI:
   - Liquid Pipe Analyzer: `read_liquid_temp_1`
   - Liquid Digital Valve: `read_liquid_temp_1_valve`
4. In the IC housing, assign:
   - `d0` = `read_liquid_temp_1`
   - `d1` = `read_liquid_temp_1_valve`
5. Copy/paste `liquid_temp_valve.ic10` into the in-game IC editor and run it.

## Behavior

- Reads `d0 Temperature` (Kelvin) and converts to Celsius.
- Opens the valve (**On = 1**) when temperature is below **20°C**.
- Closes the valve (**On = 0**) when temperature is above **30°C**.
- Between **20°C** and **30°C** it leaves the valve state unchanged (hysteresis).

## Tuning

Edit the constants at the top of `liquid_temp_valve.ic10`:

- `TEMP_OPEN_BELOW_C` (°C): valve is forced **open** when `tempC < TEMP_OPEN_BELOW_C`
- `TEMP_CLOSE_ABOVE_C` (°C): valve is forced **closed** when `tempC > TEMP_CLOSE_ABOVE_C`

Temperature notes:

- The Liquid Pipe Analyzer reports `Temperature` in Kelvin (K).
- The script converts to Celsius using: $C = K - 273.15$.

## Status

Functional.
