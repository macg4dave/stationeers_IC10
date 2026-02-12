# liquid_temp_valve

## Purpose

Open/close **all Liquid Digital Valves on the IC network** based on liquid pipe temperature from a **Liquid Pipe Analyzer**, using simple hysteresis (Schmitt-trigger style).

## Devices

Required:

- Liquid Pipe Analyzer
- One or more Liquid Digital Valves on the same data network as the IC housing

## Device registers

- `d0` = Liquid Pipe Analyzer

## Usage

1. Place the Liquid Pipe Analyzer on the liquid pipe network you want to monitor.
2. Place one or more Liquid Digital Valves on the liquid pipe network(s) you want to control.
3. (Recommended) Rename the devices so they’re easy to pick in the IC housing UI:
   - Liquid Pipe Analyzer: `read_liquid_temp_1`
4. In the IC housing, assign:
   - `d0` = `read_liquid_temp_1`
5. Copy/paste `liquid_temp_valve.ic10` into the in-game IC editor and run it.

## Behavior

- Reads `d0 Temperature` (Kelvin) and converts to Celsius.
- Turns all network Liquid Digital Valves **On = 1** when temperature is below **20°C**.
- Turns all network Liquid Digital Valves **On = 0** when temperature is above **30°C**.
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
