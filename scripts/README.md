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

- `pipe_temp_hot_cold_valves/` — Reads a Pipe Analyzer temperature and opens either a "cold" or "hot" Pipe Digital Valve based on thresholds.
