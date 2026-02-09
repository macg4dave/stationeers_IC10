# gas_temp_active_vent

## Purpose

Control one **Active Vent** using a **Gas Sensor**:

- If room pressure is too high: force **BLOW** (pressure relief) until safe.
- If room is too hot and pressure is in a safe range: run a simple **sawtooth** cycle
   by alternating vent Mode between **SUCK/BLOW** while ON to help equalize temp/pressure.

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

Temperature (°C):

- `T_ON`: start cooling when `tempC > T_ON`
- `T_OFF`: stop cooling when `tempC < T_OFF`

Pressure (kPa):

- `P_REL_ON`: start relief (force BLOW) when `pressure > P_REL_ON`
- `P_REL_OFF`: stop relief when `pressure < P_REL_OFF`
- `P_COOL_ON`: allow cooling to start only when `pressure < P_COOL_ON`
- `P_COOL_OFF`: stop cooling if `pressure > P_COOL_OFF`

Active Vent pressure setpoints (kPa):

- `PEX_BLOW` / `PIN_BLOW`: setpoints used in BLOW (Outward / Mode 0)
- `PEX_SUCK` / `PIN_SUCK`: setpoints used in SUCK (Inward / Mode 1)

Note: the Active Vent resets these values when Mode changes, so the script writes
them *after* any Mode write.

Mode mapping:

- `SUCK` / `BLOW`: if your vent behaves opposite to what you expect, swap these values.

Temperature notes:

- The Gas Sensor reports `Temperature` in Kelvin (K).
- The script converts to Celsius using: $C = K - 273.15$.

## Status

Functional.
