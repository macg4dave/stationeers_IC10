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
| `air_conditioner_hold_25c/` | Runs an Air Conditioner at a 25°C target (chip inside the AC) | db | Functional | yes |
| `pipe_heater_hold_20c/` | Pipe Heater on below 20°C (Pipe Analyzer); off on analyzer error | Pins | Functional | yes |
| `room_heater_hold_20c/` | Wall Heater on below 20°C (Gas Sensor) | Pins | Functional | yes |
| `room_cooler_and_steam_vent/` | Wall Cooler above 30°C; Active Vent on while no steam | Pins | Functional | yes |
| `furnace_heat_pipe_below_20c/` | Below 20°C: valve + Advanced Furnace on, input/output 5; furnace >100°C stops input | Pins | Functional | yes |
| `furnace_pulse_when_pipes_cold/` | Gas <30°C or liquid <80°C: pulse Advanced Furnace and valve every ~30 s | Pins | Functional | yes |
| `room_door_open_when_hot/` | Opens a Glass Door above 30°C, closes below | Pins | Functional | yes |

### Temperature-routed valves (one family: same pattern, different sensor/targets)

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `pipe_valves_open_when_cold/` | Valves named `cold`: open <10°C, close >30°C | Names | Functional | yes |
| `liquid_valves_open_when_cold/` | All Liquid Digital Valves: open <20°C, close >30°C | Prefab | Functional | yes |
| `phase_change_cooling_valve/` | Valves named `cold`: open above 30°C | Names | Functional | yes |
| `pipe_sort_hot_cold_with_pump/` | Routes `cold`/`hot` valves with hysteresis; pump holds ~10 MPa (fixed 2026-11) | Pins | Functional | yes |

### Pressure and atmosphere

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `room_vents_hold_pressure/` | Room <90 kPa intake, >120 kPa exhaust (vents named `ROOM_VENT`) (fixed 2026-11) | Names | Functional | yes |
| `pipe_vents_fill_to_10mpa/` | Fills a pipe to 10 MPa with vents named `PIPE_VENT` | Names | Functional | yes |
| `room_vents_swap_air_when_hot/` | Above 30°C: vents `IN` blow in, vents `OUT` pull out; below: all off (fixed 2026-11) | Names | Functional | yes |
| `greenhouse_co2_pressure_vent/` | Vent on when CO2 <20% or room <100 kPa (fixed 2026-11) | Pins | Functional | yes |
| `pipe_vent_fill_to_half/` | Vent on below 50 kPa, off above 55 kPa | Pins | Functional | yes |
| `liquid_pipe_top_up_vent/` | Vent on while liquid volume <50% of pipe volume | Pins | Functional | yes |
| `gas_mixer_stop_at_10mpa/` | Gas Mixer off above 10 MPa | Pins | Functional | yes |

### Methane (formerly "volatiles") handling

The folder names keep the old "volatiles" wording so existing installs and links keep
working; the scripts read the current `RatioMethane` LogicType.

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `pipe_valve_open_when_methane/` | Valve on while any methane is present, off when none | Pins | Functional | yes |
| `pipe_valve_open_when_clean/` | Valve on only with no methane, no steam and >1 kPa | Pins | Functional | yes |
| `pipe_methane_purge_valve/` | Valve on while methane present and O2 < 33% of methane | Pins | Functional | yes |
| `pipe_methane_purge_vent/` | Vent on while methane present and O2 < 33% | Pins | Functional | yes |
| `power_generator_on_methane/` | Gas Fuel Generator on while any methane is present | Pins | Functional | yes |
| `landing_pad_methane_unload/` | Landingpad Gas Output + valve on at ~100% methane; 20 MPa cutoff; override | Pins | Functional | yes |
| `liquid_pipe_purge_lever/` | Lever-armed purge of a liquid pipe (valve, vent, outlet) with LED status | Pins | Functional | yes |

### Power, suits, displays, logistics

| Script | What it does | Targeting | Status | Sim |
| --- | --- | --- | --- | --- |
| `power_generator_on_low_battery/` | Generator on when mean Large Battery charge <30% | Prefab | Functional | yes |
| `suit_helmet_auto_open/` | Opens the helmet in safe air (4–45°C, 80–150 kPa); respects manual close | db + pin | Functional | yes |
| `display_clock_from_sun/` | Hours and minutes on two LED Displays from a Daylight Sensor (no seconds) | Pins | Functional | yes |
| `vending_export_exact_count/` | Exports an exact item count via Stacker + Sorter return loop | Pins | Functional | no |

## Naming and batch targeting

- Name hashes are exact and case-sensitive: `HASH("cold")` matches `cold`, not `cold_1`
  or `Cold`.
- If a script "can't find" devices: check the data network, then the exact name, then
  the device's `Lock`/`Mode` (`docs/usage/README.md`).

## Adding a script

Copy `scripts/_template/`, follow `docs/ic10_script_checklist.md`, add a scenario to
`tests/test_standalone_scripts.py`, then run `python tools/check_all.py`.
