# Scripts

Single-chip, paste-ready Stationeers IC10 programs. Each lives in its own folder:

- `scripts/<name>/<name>.ic10` — paste this into the in-game IC chip
- `scripts/<name>/README.md` — devices, `d0..d5` mapping, settings, tuning

Multi-chip systems live in `modular scripts/` instead.

## Script index

**Pins** = devices are assigned to `d0..d5` in the IC Housing.
**Names** = devices are found on the data network by prefab + exact name (`sbn`/`lbn`),
so you must rename them in-game exactly as the README says.

Status is the author's in-game status label (unchanged by tooling).
**Sim** = behaviour scenario in `tests/test_standalone_scripts.py` passes
(simulated only; it does not replace an in-game test).

### Temperature control

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `air_conditioner_25c/` | Runs an Air Conditioner at a 25°C target (chip inside the AC) | db | Functional | yes |
| `pipe_heater_below_20c/` | Pipe Heater on below 20°C (Pipe Analyzer); off on analyzer error | Pins | Functional | yes |
| `room_heater_below_20c/` | Wall Heater on below 20°C (Gas Sensor) | Pins | Functional | yes |
| `room_cooler_steamless_vent/` | Wall Cooler above 30°C; Active Vent on while no steam | Pins | Functional | yes |
| `pipe_furnace_valve_below_20c/` | Below 20°C: valve + Advanced Furnace on, input/output 5; furnace >100°C stops input | Pins | Functional | yes |
| `dual_analyzer_furnace_pulse/` | Gas <30°C or liquid <80°C: pulse Advanced Furnace and valve every ~30 s | Pins | Functional | yes |
| `gas_sensor_glass_door_30c/` | Opens a Glass Door above 30°C, closes below | Pins | Functional | yes |

### Temperature-routed valves (one family: same pattern, different sensor/targets)

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `pipe_temp_valve/` | Valves named `cold`: open <10°C, close >30°C | Names | Functional | yes |
| `liquid_temp_valve/` | All Liquid Digital Valves: open <20°C, close >30°C | Prefab | Functional | yes |
| `phase_change_temp_valve/` | Valves named `cold`: open above 30°C | Names | Functional | yes |
| `pipe_temp_hot_cold_valves/` | Routes `cold`/`hot` valves with hysteresis; pump holds ~10 MPa (fixed 2026-11) | Pins | Functional | yes |

### Pressure and atmosphere

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `room_pressure_active_vent/` | Room <90 kPa intake, >120 kPa exhaust (vents named `ROOM_VENT`) (fixed 2026-11) | Names | Functional | yes |
| `pipe_pressure_active_vent/` | Fills a pipe to 10 MPa with vents named `PIPE_VENT` | Names | Functional | yes |
| `active_vent_dual_sets/` | Above 30°C: vents `IN` blow in, vents `OUT` pull out; below: all off (fixed 2026-11) | Names | Functional | yes |
| `room_co2_below_20pct_active_vent/` | Vent on when CO2 <20% or room <100 kPa (fixed 2026-11) | Pins | Functional | yes |
| `pipe_half_full_active_vent/` | Vent on below 50 kPa, off above 55 kPa | Pins | Functional | yes |
| `liquid_pipe_fill_percent_active_vent/` | Vent on while liquid volume <50% of pipe volume | Pins | Functional | yes |
| `pipe_pressure_gas_mixer/` | Gas Mixer off above 10 MPa | Pins | Functional | yes |

### Methane (formerly "volatiles") handling

The folder names keep the old "volatiles" wording so existing installs and links keep
working; the scripts read the current `RatioMethane` LogicType.

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `no_volatiles_valve/` | Valve on while any methane is present, off when none | Pins | Functional | yes |
| `no_volatiles_no_steam_valve/` | Valve on only with no methane, no steam and >1 kPa | Pins | Functional | yes |
| `volatiles_purge_valve/` | Valve on while methane present and O2 < 33% of methane | Pins | Functional | yes |
| `volatiles_purge_active_vent/` | Vent on while methane present and O2 < 33% | Pins | Functional | yes |
| `pipe_volatiles_gas_fuel_generator/` | Gas Fuel Generator on while any methane is present | Pins | Functional | yes |
| `landingpad_volatiles_pressure_valve/` | Landingpad Gas Output + valve on at ~100% methane; 20 MPa cutoff; override | Pins | Functional | yes |
| `purge_valve/` | Lever-armed purge of a liquid pipe (valve, vent, outlet) with LED status | Pins | Functional | yes |

### Power, suits, displays, logistics

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `large_battery_mean_gas_generator/` | Generator on when mean Large Battery charge <30% | Prefab | Functional | yes |
| `hardsuit_helmet_temp_pressure_open/` | Opens the helmet in safe air (4–45°C, 80–150 kPa); respects manual close | db + pin | Functional | yes |
| `led_display_hms_clock/` | Hours and minutes on two LED Displays from a Daylight Sensor (no seconds) | Pins | Functional | yes |
| `vending_machine_export/` | Exports an exact item count via Stacker + Sorter return loop | Pins | Functional | no |

## Naming and batch targeting

- Name hashes are exact and case-sensitive: `HASH("cold")` matches `cold`, not `cold_1`
  or `Cold`.
- If a script "can't find" devices: check the data network, then the exact name, then
  the device's `Lock`/`Mode` (`docs/usage/README.md`).

## Adding a script

Copy `scripts/_template/`, follow `docs/ic10_script_checklist.md`, add a scenario to
`tests/test_standalone_scripts.py`, then run `python tools/check_all.py`.
