# Scripts

This folder contains **player-facing** Stationeers IC10 programs.

## Folder layout

Each script lives in its own folder:

- `scripts/<script_name>/`
  - `README.md` — how to set it up in-game (device mapping, settings, tips)
  - `<script_name>.ic10` — the IC10 code you paste into the in-game IC chip

## In-game device naming (recommended)

Stationeers lets you rename items. Renaming devices to match a script’s README makes setup much faster:

- You can quickly find the right devices in the in-game UI when assigning `d0..d5`.
- You can deploy multiple copies of the same script by using numbered names like `_1`, `_2`, etc.

Example naming pattern:

- `read_pipe_temp_1`
- `read_pipe_temp_2`

The exact names are optional, but consistency helps.

## Notes

- These scripts are intended to be pasted into the **in-game** IC10 chip.
- Repo tooling/source files are not constrained by in-game chip limits unless you are producing final paste-into-game IC10.

## Hash-targeted script setup (important)

Some scripts target devices via network hashes (`lb/sb/lbn/sbn`) instead of direct `d0..d5` references.

- Name hashes are exact and case-sensitive.
  - `HASH("cold")` matches only `cold`.
  - `cold_1`, `Cold`, and `COLD` are different names.
- Batch name hash matching is not substring matching.
- If a script README says "name valves `cold`", rename targets exactly to `cold`.

If behavior looks like "script can't find device", verify data-network connection and exact rename first.

## Creating a new script (template)

- Start from `scripts/_template/` (copy the folder, then rename folder + `.ic10` file).
- Follow `docs/ic10_script_checklist.md` to stay consistent and paste-ready.

## Script list

- `led_display_hms_clock/` — Drives 3 LED Displays as a 24h HH:MM:SS clock.
- `large_satellite_dish_sweep_scan/` — Deterministic H/V sweep with edge flip, strength threshold option, and button toggle.
- `large_satellite_dish_cycle_contacts/` — Collects unique contacts, then button-cycles lock target in discovery order.
- `large_satellite_dish_led_readout/` — Mirrors dish `Horizontal`, `Vertical`, `SizeX`, and `SizeZ` to 4 LED Displays.
- `phase_change_temp_valve/` — Opens a Pipe Digital Valve when a phase_change_device temperature is above 30°C.
- `pipe_temp_hot_cold_valves/` — Reads a Pipe Analyzer temperature and opens either a "cold" or "hot" Pipe Digital Valve based on thresholds.
- `active_vent_dual_sets/` — Sets one named group of Active Vents to intake and another to exhaust using batch hashes.
- `room_pressure_active_vent/` — Reads room pressure (Gas Sensor) and sets an Active Vent mode based on low/high pressure thresholds.
- `volatiles_purge_active_vent/` — Turns an Active Vent on when Volatiles are present until Oxygen ratio is >= Volatiles ratio.
- `liquid_pipe_fill_percent_active_vent/` — Turns an Active Vent on when a Liquid Pipe Analyzer reports liquid volume below a configurable percentage.
- `landingpad_volatiles_pressure_valve/` — Enables Landingpad Liquid Output + Liquid Digital Valve only at 100% liquid volatiles, with 20 MPa safety cutoff.
- `SatCom/` — Multi-chip satellite comms scaffold (master + discover worker + cycle worker).

Additional scripts in this repo:

- `dual_analyzer_furnace_pulse/`
- `liquid_temp_valve/`
- `no_volatiles_valve/`
- `no_volatiles_no_steam_valve/`
- `pipe_temp_valve/`
- `pipe_half_full_active_vent/`
- `purge_valve/`
- `room_cooler_steamless_vent/`
- `solar_tracking/`
