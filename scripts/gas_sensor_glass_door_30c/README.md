# gas_sensor_glass_door_30c

## Purpose

Read a **Gas Sensor** and control a **Glass Door** from room temperature:

- if temperature is **above 30°C**, open the door
- if temperature is **below 30°C**, close the door
- if temperature is **exactly 30°C**, keep the current door state

## Devices

Required:

- Gas Sensor
- Glass Door

## Device registers

- `d0` = Gas Sensor
- `d1` = Glass Door

## Usage

1. Place a Gas Sensor in the room you want to monitor.
2. Place and power a Glass Door you want to control.
3. Make sure both devices are on the same data network as the IC Housing.
4. (Recommended) Rename devices so they are easy to assign:
   - Gas Sensor: `door_temp_sensor_1`
   - Glass Door: `door_temp_door_1`
5. In the IC Housing, assign:
   - `d0` = `door_temp_sensor_1`
   - `d1` = `door_temp_door_1`
6. Paste `gas_sensor_glass_door_30c.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `gas_sensor_glass_door_30c.ic10`:

- `TEMP_OPEN_ABOVE_C` (°C):
  - open when `tempC > TEMP_OPEN_ABOVE_C`
  - close when `tempC < TEMP_OPEN_ABOVE_C`
  - hold current state when `tempC == TEMP_OPEN_ABOVE_C`

Temperature notes:

- Gas Sensor `Temperature` is reported in Kelvin (K).
- The script converts to Celsius using $C = K - 273.15$.

## In-game setup notes

- See `docs/usage/gas_sensor.md` for Gas Sensor reading gotchas.
- This script clears the door `Lock` and forces door `On=1` if needed.
- The script writes `Open` only when the desired state changes.

## Status

Functional.
