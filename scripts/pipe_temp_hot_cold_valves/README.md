# pipe_temp_hot_cold_valves

**Category:** Controller  
**Status:** Functional


## Purpose

Reads a **Pipe Analyzer** temperature and opens one of two **Pipe Digital Valves**:

- If temperature is **below 20°C**: open the **cold** valve
- If temperature is **above 40°C**: open the **hot** valve
- Otherwise: **close both**

Also reads **Pipe Analyzer** pressure and toggles a **Pipe Volume Pump** to keep the
pipe near **10 MPa** (10,000 kPa).


## Devices

Required:

- 1× Pipe Analyzer
- 2× Pipe Digital Valve
- 1× Pipe Volume Pump


## Device registers

Assign these in the IC housing UI:

- `d0` = Pipe Analyzer (temperature source)
- `d1` = Pipe Digital Valve for the **hot** path (name/label it `hot`)
- `d2` = Pipe Digital Valve for the **cold** path (name/label it `cold` for your own sanity)
- `d3` = Pipe Volume Pump (pressure regulator)


## Tuning

In `pipe_temp_hot_cold_valves.ic10`:

- `TEMP_COLD_BELOW_C` (default `20`) — cold valve turns on below this temperature (°C)
- `TEMP_HOT_ABOVE_C` (default `40`) — hot valve turns on above this temperature (°C)

Pressure control:

- `PRESSURE_TARGET_KPA` (default `10000`) — target pressure in **kPa** (10 MPa)
- `PRESSURE_HYST_KPA` (default `250`) — hysteresis band in **kPa**
- `PUMP_SETTING_L` (default `10`) — volume pump setting (liters per tick)


## Notes

- Pipe Analyzer `Temperature` is **Kelvin** (K). The script converts using: $C = K - 273.15$.
- If you want “deadband keeps last state” behavior instead of closing both in the middle range, say so and I’ll tweak it (it’s a small change).
