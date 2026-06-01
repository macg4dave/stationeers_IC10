# pipe_furnace_valve_below_20c

## Purpose

Read a **Pipe Analyzer** and control an **Advanced Furnace** plus a
**Pipe Digital Valve** from pipe temperature:

- if temperature is **below 20°C**, turn the valve **ON** and turn the furnace **ON**
- if the pipe is still below **20°C**, set furnace `SettingInput = 5` and `SettingOutput = 5`
- if the pipe is still below **20°C** and the furnace is above **100°C**, override furnace `SettingInput = 0`
- if temperature is **above 20°C**, turn the furnace and valve **OFF**
- if temperature is **exactly 20°C**, keep the current state

## Devices

Required:

- Pipe Analyzer
- Pipe Digital Valve
- Advanced Furnace

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Pipe Digital Valve
- `d2` = Advanced Furnace

## Usage

1. Place a Pipe Analyzer on the pipe network you want to monitor.
2. Place the Pipe Digital Valve you want to control.
3. Place and power the Advanced Furnace.
4. Make sure all three devices are on the same data network as the IC Housing.
5. (Recommended) Rename devices so they are easy to assign:
   - Pipe Analyzer: `read_pipe_temp_1`
   - Pipe Digital Valve: `warm_valve_1`
   - Advanced Furnace: `adv_furnace_1`
6. In the IC Housing, assign:
   - `d0` = `read_pipe_temp_1`
   - `d1` = `warm_valve_1`
   - `d2` = `adv_furnace_1`
7. Paste `pipe_furnace_valve_below_20c.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `pipe_furnace_valve_below_20c.ic10`:

- `TEMP_ON_BELOW_C` (°C):
  - turn furnace + valve on when `tempC < TEMP_ON_BELOW_C`
  - turn furnace + valve off when `tempC > TEMP_ON_BELOW_C`
  - hold current state when `tempC == TEMP_ON_BELOW_C`
- `FURNACE_MAX_ON_C` (°C):
  - if the Advanced Furnace temperature is above this value while the pipe is still below `TEMP_ON_BELOW_C`, override furnace `SettingInput` with the hot-mode value below
  - the furnace still stays on while the pipe is cold
- `COLD_INPUT`:
  - furnace `SettingInput` to use while the pipe is below `TEMP_ON_BELOW_C`
- `HOT_INPUT`:
  - furnace `SettingInput` override to use when the furnace is hotter than `FURNACE_MAX_ON_C` and the pipe is still cold
- `HOT_OUTPUT`:
  - furnace `SettingOutput` to use while the pipe is still cold

Temperature notes:

- Pipe Analyzer `Temperature` is reported in Kelvin (K).
- Advanced Furnace `Temperature` is also reported in Kelvin (K).
- The script converts to Celsius using $C = K - 273.15$.

## In-game setup notes

- This script checks that `d0` is actually a Pipe Analyzer by reading `PrefabHash`.
- This script clears `Lock` on the valve and furnace if needed.
- It writes the valve `On`, furnace `On`, and furnace `Activate` states only when needed.
- If you wanted the furnace to pulse instead of staying on while cold, say the word and I
  can turn this into a pulse-style variant.

## Status

Functional.
