# dual_analyzer_furnace_pulse

## Purpose

Every ~30 seconds, read **Temperature** from:

- a **Liquid Pipe Analyzer** (liquid pipe network), and
- a **Pipe Analyzer** (gas pipe network)

If **any** measured temperature is below **20°C** and **none** are above **30°C**, then:

- turn **ON** a **Pipe Digital Valve**
- set an **Advanced Furnace** to `Activate = 1` for ~5 seconds
- then turn the valve back **OFF**

## Devices

Required:

- Liquid Pipe Analyzer
- Pipe Analyzer
- Pipe Digital Valve
- Advanced Furnace

## Device registers

- `d0` = Liquid Pipe Analyzer
- `d1` = Pipe Analyzer
- `d2` = Pipe Digital Valve
- `d3` = Advanced Furnace

## Usage

1. Place the Liquid Pipe Analyzer and Pipe Analyzer on the networks you want to monitor.
2. Place the Pipe Digital Valve you want to control.
3. Place (and power) the Advanced Furnace.
4. (Recommended) Rename devices so they’re easy to pick in the IC housing UI:
   - Liquid Pipe Analyzer: `read_liquid_temp_1`
   - Pipe Analyzer: `read_pipe_temp_1`
   - Pipe Digital Valve: `warmup_valve_1`
   - Advanced Furnace: `adv_furnace_1`
5. In the IC housing, assign:
   - `d0` = `read_liquid_temp_1`
   - `d1` = `read_pipe_temp_1`
   - `d2` = `warmup_valve_1`
   - `d3` = `adv_furnace_1`
6. Copy/paste `dual_analyzer_furnace_pulse.ic10` into the in-game IC editor and run it.

## Behavior details

### Temperature units

Both analyzers report `Temperature` in Kelvin (K). The script converts to Celsius using:

$$C = K - 273.15$$

### Trigger condition

The pulse runs when:

- `(liquidTempC < 20) OR (gasTempC < 20)`
- AND `(liquidTempC <= 30) AND (gasTempC <= 30)`

So if either side is “cold”, but either side is “too hot”, it will **not** pulse.

### Timing

IC10 can only wait in ticks (`yield`). The defaults assume **~2 ticks/second**:

- `PULSE_TICKS = 10`  → ~5 seconds
- `LOOP_TICKS = 60`   → ~30 seconds

If your in-game timing differs, adjust these constants in `dual_analyzer_furnace_pulse.ic10`.

## Tuning

In `dual_analyzer_furnace_pulse.ic10`:

- `TEMP_LOW_C` (°C): “cold” threshold (default 20)
- `TEMP_HIGH_C` (°C): “too hot” ceiling (default 30)
- `PULSE_TICKS`: how long to set `Activate = 1`
- `LOOP_TICKS`: how often to re-check and potentially pulse

## Status

Functional.
