# pipe_sort_hot_cold_with_pump

**Category:** Controller  
**Status:** Functional


## Purpose

Reads a **Pipe Analyzer** temperature and selects one of two **Pipe Digital Valves**.
Uses hysteresis so valves do not flap on/off around a single threshold:

- **Cold route ON** below `20°C`, and stays on until temperature rises above `24°C`
- **Hot route ON** above `40°C`, and stays on until temperature drops below `36°C`
- Between those bands, current route is held for stability (unless close threshold is crossed)

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

In `pipe_sort_hot_cold_with_pump.ic10`:

- `TEMP_COLD_OPEN_BELOW_C` (default `20`) — cold route can turn on below this temperature (°C)
- `TEMP_COLD_CLOSE_ABOVE_C` (default `24`) — cold route turns off above this temperature (°C)
- `TEMP_HOT_OPEN_ABOVE_C` (default `40`) — hot route can turn on above this temperature (°C)
- `TEMP_HOT_CLOSE_BELOW_C` (default `36`) — hot route turns off below this temperature (°C)

Pressure control:

- `PRESSURE_TARGET_KPA` (default `10000`) — target pressure in **kPa** (10 MPa)
- `PRESSURE_HYST_KPA` (default `250`) — hysteresis band in **kPa**
- `PUMP_SETTING_L` (default `1`) — volume pump setting (liters per tick)

Pump behaviour: ON below 9,750 kPa, OFF above 10,250 kPa, unchanged in between.


## Notes

- Pipe Analyzer `Temperature` is **Kelvin** (K). The script converts using: $C = K - 273.15$.
- Pipe Analyzer `Pressure` is read as **kPa** (wiki: "In kPa").

## Change history

- 2026-11: fixed the pump never stopping above 2 MPa. An old "Pa -> kPa"
  guess divided any reading above 2,000 kPa by 1000, so at the 10 MPa target the
  script saw ~10 and kept pumping. Temperature/valve behaviour is unchanged.
  Status stays **Functional**; re-test the pump stop in-game.
