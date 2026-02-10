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

## Script list

- `large_satellite_dish_random_scan/` — Moves a Large Satellite Dish to random angles until it finds a non-zero SignalID (button toggles scanning).
- `large_satellite_dish_sweep_scan/` — Deterministic H/V sweep with edge flip, strength threshold option, and button toggle.
- `phase_change_temp_valve/` — Opens a Pipe Digital Valve when a phase_change_device temperature is above 30°C.
- `pipe_temp_hot_cold_valves/` — Reads a Pipe Analyzer temperature and opens either a "cold" or "hot" Pipe Digital Valve based on thresholds.
- `active_vent_dual_sets/` — Sets one named group of Active Vents to intake and another to exhaust using batch hashes.
- `room_pressure_active_vent/` — Reads room pressure (Gas Sensor) and sets an Active Vent mode based on low/high pressure thresholds.
- `volatiles_purge_active_vent/` — Turns an Active Vent on when Volatiles are present until Oxygen ratio is >= Volatiles ratio.
