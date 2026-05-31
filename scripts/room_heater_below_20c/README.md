# room_heater_below_20c

## Purpose

Read a **Gas Sensor** and turn a **Wall Heater** **ON** when room temperature is below **20°C**.

If the room is **20°C or warmer**, the script turns the heater **OFF**.

## Devices

Required:

- Gas Sensor
- Wall Heater

## Device registers

- `d0` = Gas Sensor
- `d1` = Wall Heater

## Usage

1. Place a Gas Sensor in the room you want to monitor.
2. Place a Wall Heater in that room.
3. Make sure both devices are powered and on the same data network as the IC Housing.
4. (Recommended) Rename devices so they are easy to assign:
   - Gas Sensor: `room_heat_1_sensor`
   - Wall Heater: `room_heat_1_heater`
5. In the IC Housing, assign:
   - `d0` = `room_heat_1_sensor`
   - `d1` = `room_heat_1_heater`
6. Paste `room_heater_below_20c.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `room_heater_below_20c.ic10`:

- `HEAT_ON_BELOW_C` (°C): heater is forced **ON** when `tempC < HEAT_ON_BELOW_C`

Temperature notes:

- Gas Sensor `Temperature` is reported in Kelvin (K).
- The script converts to Celsius using $C = K - 273.15$.

## In-game setup notes

- See `docs/usage/gas_sensor.md` for Gas Sensor reading gotchas.
- See `docs/usage/wall_heater.md` for Wall Heater setup notes.
- This script only toggles `On`; any extra device-specific settings should be handled in the heater UI if needed.

## Status

Functional.
