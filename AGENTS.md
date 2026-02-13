# Copilot instructions (stationeers_IC10)

This repo is a **paste-ready IC10 script library** plus **stdlib-only Python tools**.
Start with `README.md`, then `scripts/README.md` and `modular scripts/README.md`.

## Layout & what to touch
- `scripts/<name>/<name>.ic10` + `scripts/<name>/README.md` (player setup and `d0..d5`).
- `modular scripts/<feature>/` (master + workers + feature README).
- Checklists/patterns/templates: `docs/ic10_script_checklist.md`, `docs/modular_master_worker_pattern.md`, `scripts/_template/`, `modular scripts/_template/`.
- Setup playbooks: `docs/usage/*.md`.
- Device source of truth: `catalog/devices/*.json` + `catalog/index.json` (schema: `catalog/README.md`).
- Tooling: `tools/ic10_size_check.py`, `tools/wiki_import.py`.
- VS Code IC10 debugging: `.vscode/extensions.json` + `.vscode/launch.json` (`type: "ic10"`, `Traineratwot.stationeers-ic10`).

## Non-obvious conventions
- IC10 comments use `#`; labels end with `:`; keep `alias` names short (paste limits count everything).
- Gate required devices with `bdns` + `yield`; keep in-loop guards before critical `l` reads.
- Example: `scripts/pipe_temp_hot_cold_valves/pipe_temp_hot_cold_valves.ic10`.
- Many temperatures are Kelvin; convert with $C = K - 273.15$ before threshold logic.
- Avoid label/alias names that shadow LogicType-like identifiers (example to avoid: `Temperature:`).
- Avoid redundant writes (`On`, `Open`, `Setting`): read first, write only on change.
- `sbn/lbn` name hashes are exact/case-sensitive (`HASH("IN")` matches `IN`, not `IN_1`).
- For hash-targeted devices, prefer numeric prefab hashes from `catalog/devices/<Device>.json` (example: Pipe Digital Valve `-1280984102`), then optionally combine with exact name hashes for subsets.
- For any device `Mode`/enum field, read `modeValues` from `catalog/devices/<Device>.json` first; never guess defaults.
- If a device “does nothing”, assume missing in-game settings first: check `docs/usage/README.md` then the device playbook (Active Vent commonly needs **both** `On=1` and `Open=1` plus correct `Mode`/pressure: `docs/usage/active_vent.md`).

## Modular rules (master + workers)
- Prefer folder-local modular architecture: `modular scripts/<feature>/`, `<feature>_master.ic10`, `<feature>_worker_<task>.ic10`, `README.md` (wiring + command/data contract + status table).
- Master handles orchestration/input edges; workers stay single-purpose and publish status via each chip’s `db Setting`.
- Prefer Logic Memory token/data channels; wiring order is inter-chip links from `d0` downward, then user inputs, then feature devices.

## Critical workflows and guardrails
- Validate paste limits for shipped IC10 (**128 lines**, **90 chars/line**, including comments/blanks):
  - `python tools/ic10_size_check.py scripts/ --ext .ic10`
  - `python tools/ic10_size_check.py "modular scripts/" --ext .ic10`
- Update catalog from wiki when I/O names or modes are unclear:
  - `python tools/wiki_import.py https://stationeers-wiki.com/Pipe_Analyzer`
  - Section import supported: `.../Sensors#Gas_Sensor`
- Keep outputs paste-ready `.ic10`; avoid opportunistic renames; if scope is unclear between tooling/catalog vs gameplay IC10, preserve existing IC10 patterns and call out paste-limit impact.
