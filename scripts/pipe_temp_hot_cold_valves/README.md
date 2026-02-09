# pipe_temp_hot_cold_valves

**Category:** Controller  
**Status:** Functional


## Purpose

Reads a **Pipe Analyzer** temperature and opens one of two **Pipe Digital Valves**:

- If temperature is **below 20°C**: open the **cold** valve
- If temperature is **above 40°C**: open the **hot** valve
- Otherwise: **close both**


## Devices

Required:

- 1× Pipe Analyzer
- 2× Pipe Digital Valve


## Device registers

Assign these in the IC housing UI:

- `d0` = Pipe Analyzer (temperature source)
- `d1` = Pipe Digital Valve for the **cold** path (name/label it `cold` for your own sanity)
- `d2` = Pipe Digital Valve for the **hot** path (name/label it `hot`)


## Tuning

In `pipe_temp_hot_cold_valves.ic10`:

- `TEMP_COLD_BELOW_C` (default `20`) — cold valve turns on below this temperature (°C)
- `TEMP_HOT_ABOVE_C` (default `40`) — hot valve turns on above this temperature (°C)


## Notes

- Pipe Analyzer `Temperature` is **Kelvin** (K). The script converts using: $C = K - 273.15$.
- If you want “deadband keeps last state” behavior instead of closing both in the middle range, say so and I’ll tweak it (it’s a small change).
