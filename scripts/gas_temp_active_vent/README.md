# gas_temp_active_vent

## Purpose

Turn an **Active Vent** on when a **Gas Sensor** reports a temperature above a threshold.

## Devices

Required:

- Gas Sensor
- Active Vent

## Device registers

- `d0` = Gas Sensor
- `d1` = Active Vent

## Usage

1. Place a Gas Sensor where you want to monitor atmosphere temperature.
2. Place / pipe / wire an Active Vent you want to control.
3. (Recommended) Rename devices so they’re easy to select in the IC housing UI:
   - Gas Sensor: `read_gas_temp_1`
   - Active Vent: `read_gas_temp_1_vent`
4. In the IC housing, assign:
   - `d0` = `read_gas_temp_1`
   - `d1` = `read_gas_temp_1_vent`
5. Copy/paste `gas_temp_active_vent.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `gas_temp_active_vent.ic10`:

- `TEMP_ON_ABOVE_C` (°C): vent is forced **ON** when `tempC > TEMP_ON_ABOVE_C`.

Temperature notes:

- The Gas Sensor reports `Temperature` in Kelvin (K).
- The script converts to Celsius using: $C = K - 273.15$.

## Status

Functional.
