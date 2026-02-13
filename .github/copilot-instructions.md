# Copilot instructions (stationeers_IC10)

This repo is a **Stationeers IC10 script library** plus **stdlib-only Python tools** (no build system / no pip deps).
Start with `README.md`, then script catalogs in `scripts/README.md` and `modular scripts/README.md`.

## Layout & “what to touch”
- IC10 scripts: `scripts/<name>/<name>.ic10` + `scripts/<name>/README.md` (player-facing setup + `d0..d5` mapping)
- Modular IC10 scripts: `modular scripts/<feature>/` (master + workers + feature README)
- New-script checklist + patterns: `docs/ic10_script_checklist.md` (use this for consistent paste-ready output)
- Modular architecture pattern (master + workers): `docs/modular_master_worker_pattern.md`
- Starter template: `scripts/_template/` (copy/rename when creating a new script)
- Modular starter template: `modular scripts/_template/`
- In-game setup checklists: `docs/usage/*.md` (this is the repo’s “we learned this the hard way” library)
- Device Logic I/O catalog: `catalog/devices/*.json` + `catalog/index.json` (schema in `catalog/README.md`)
- Tooling (Python): `tools/ic10_size_check.py`, `tools/wiki_import.py`
- VS Code IC10 debugging: `.vscode/extensions.json` + `.vscode/launch.json` (debugger type `ic10` via `Traineratwot.stationeers-ic10`)

## IC10 conventions used in this repo (important gotchas)
- Comments start with `#`; labels end with `:`. Use `alias` heavily (keep names short: paste limits count chars).
- Gate device availability with `bdns` loops + `yield` (see `scripts/pipe_temp_hot_cold_valves/pipe_temp_hot_cold_valves.ic10`).
- Many temperatures are **Kelvin**; convert with $C = K - 273.15$ (see `pipe_temp_hot_cold_valves.ic10`).
- Avoid label/alias names that shadow LogicType-ish identifiers (example to avoid: `Temperature:`).
- Prefer avoiding redundant writes (reduce network spam): read current `On` then `s` only when changed (see `pipe_temp_hot_cold_valves.ic10`).
- Batch network ops: `sbn`/`lbn` use **exact NameHash match**, not substring (see `scripts/active_vent_dual_sets/active_vent_dual_sets.ic10`, hashes like `HASH("IN")`).
- For hash-targeted devices, prefer authoritative numeric prefab hashes from `catalog/devices/<Device>.json` when available (e.g., Pipe Digital Valve `-1280984102`), and combine with exact name hash only when you intentionally want a named subset.
- For any device with `Mode` (or enum-like settings), read `catalog/devices/<Device>.json` first and use `modeValues` explicitly.
	- Define constants in script (`define MODE_* ...`) and set mode in init/setup.
	- Don’t assume default mode values.
	- Example (`LED_Display`): `Mode=0` number, `Mode=8` minutes, `Mode=7` seconds.

## Script naming & exceptions
- Convention: **folder name == base script name** and file is `<name>.ic10`.
- This repo is **paste-ready `.ic10` first**; don’t introduce `.icX` sources unless a task explicitly asks.
- Verify the actual filename when editing: there’s at least one historical mismatch (`scripts/solar_tracking/solar_tacking.ic10`). Don’t “fix” names unless the task asks.

## Modular scripts (master + workers)
- When user asks for modular/chained/multi-chip behavior, prefer a folder-local architecture:
	- `modular scripts/<feature>/`
	- `<feature>_master.ic10`
	- `<feature>_worker_<task>.ic10` (one task per worker)
	- `README.md` with wiring + command/data contract + status table.
- Prefer **Logic Memory** devices for cross-chip command/data channels (token + slots), not ad-hoc worker housing fields.
- Require each chip to publish compact status codes via its own `db Setting` and document code meanings.
- Keep worker logic narrow and single-purpose; keep orchestration and button edge handling in master.
- Preserve paste limits for every worker/master independently (128 lines, 90 chars/line).

## Critical workflows
- Paste limits (final ship output): **128 lines** and **90 chars/line** (including comments/blanks).
	- After changing any `scripts/**/*.ic10`, run: `python tools/ic10_size_check.py scripts/ --ext .ic10`.
- Updating the device catalog from the wiki (writes JSON + updates index):
	- `python tools/wiki_import.py https://stationeers-wiki.com/Pipe_Analyzer`
	- Supports section imports for multi-device pages: `.../Sensors#Gas_Sensor`

## `docs/usage/` = failure-driven setup truth
- If a device “does nothing” in-game, assume a missing in-game setting first; check `docs/usage/README.md` then the device page.
- Example: Active Vent scripts often require **both** `On=1` **and** `Open=1`, plus correct `Mode`/pressure settings (see `docs/usage/active_vent.md`).

If unsure whether a task is **tooling/catalog** (Python/JSON) or **pasteable IC10**, default to preserving existing patterns and call out IC10 paste-limit implications.
