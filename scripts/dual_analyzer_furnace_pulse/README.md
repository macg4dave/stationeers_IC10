# dual_analyzer_furnace_pulse

## Purpose

Every ~30 seconds, read **Temperature** from:

- a **Liquid Pipe Analyzer** (liquid pipe network), and
- a **Pipe Analyzer** (gas pipe network)

If **either** measured temperature is below its threshold, then:

- turn **ON** a **Pipe Digital Valve**
- set an **Advanced Furnace** to `Activate = 1` for a short pulse (~1 second by default)
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

The pulse runs when **any enabled check** is below its threshold:

- gas/air: `gasTempC < 30`
- liquid: `liquidTempC < 80`

The thresholds are currently hard-coded in the script (search for `slt ... 30` / `slt ... 80`).

### Selecting what to check (CHECK_TYPE)

In `dual_analyzer_furnace_pulse.ic10`, set:

- `CHECK_TYPE = 0` → check **both** gas + liquid (default)
- `CHECK_TYPE = 1` → check **gas/air only** (Pipe Analyzer on `d1`)
- `CHECK_TYPE = 2` → check **liquid only** (Liquid Pipe Analyzer on `d0`)

If you pick gas-only or liquid-only, the script will skip reading the other analyzer.

### Timing

IC10 can only wait in ticks (`yield`). The defaults assume **~2 ticks/second**:

- `PULSE_TICKS = 2`   → ~1 second
- `LOOP_TICKS = 60`   → ~30 seconds

If your in-game timing differs, adjust these constants in `dual_analyzer_furnace_pulse.ic10`.

## Tuning

In `dual_analyzer_furnace_pulse.ic10`:

- `CHECK_TYPE`: which analyzer(s) to read (0=both, 1=gas only, 2=liquid only)
- `PULSE_TICKS`: how long to set `Activate = 1`
- `LOOP_TICKS`: how often to re-check and potentially pulse

## Status

Functional.
