# Copilot instructions (stationeers_IC10)

This repo is a **Stationeers IC10 script library** plus small **stdlib-only Python tools** (no build system).
Start with `README.md`, then `scripts/README.md` for the script catalog.

## Where things live (actual layout)
- Scripts: `scripts/<script_name>/README.md` + `scripts/<script_name>/<script_name>.ic10`
- Device Logic I/O catalog: `catalog/devices/*.json` + `catalog/index.json` (schema in `catalog/README.md`)
- Tooling (Python, stdlib-only): `tools/wiki_import.py`, `tools/ic10_size_check.py`
- VS Code helpers: `.vscode/extensions.json` and `.vscode/launch.json` (debug `type: ic10` via `Traineratwot.stationeers-ic10`).

## IC10 semantics & repo-specific gotchas
- Comments start with `#`; labels end with `:`.
- Registers: `r0..r15`, `sp`, `ra`; devices: `d0..d5`, `db`.
- Many temperatures are **Kelvin**; convert with `C = K - 273.15` (see `scripts/pipe_temp_hot_cold_valves/pipe_temp_hot_cold_valves.ic10`).
- Don’t use label/alias names that shadow LogicType-ish identifiers (e.g. `Temperature:`).
- Batch network ops are used; `lbn/sbn` name matching is **exact hash**, not substring (see `scripts/active_vent_dual_sets/active_vent_dual_sets.ic10`).

## Script patterns to follow when editing/adding `.ic10`
- Keep names short `snake_case`; **folder name == script filename**.
- Add/keep a compact header comment: Category, Status, Purpose, and `d0..d5` mapping.
- Use `alias` for readability, but keep names short (paste limits count characters).
- Gate device availability with `bdns` loops and use `yield` in long-running loops.
- Avoid redundant writes to reduce network spam (see `pipe_temp_hot_cold_valves.ic10` reading current values before `s`).
- In per-script `README.md`, include explicit in-game setup steps (e.g., vents often require `On=1` *and* `Open=1`, plus `Mode`). See `docs/usage/`.

## In-game setup playbooks (AI-common mistakes)
- Check `docs/usage/` for short checklists when a device “does nothing” after a script writes to it (start with `docs/usage/README.md`, then the specific device page like `docs/usage/active_vent.md`).
- Prefer recommending consistent in-game device renaming (see `scripts/README.md`), especially when using `lbn/sbn` exact name hashes.

## In-game paste limits (only for final/pasteable output)
- IC chip limits: **128 lines** and **90 chars/line** (including comments).
- Check before “shipping”: `python tools/ic10_size_check.py scripts/ --ext .ic10`
- **Agent rule:** after you create or patch any `scripts/**/*.ic10`, run the size checker on the changed file(s) (or the whole `scripts/` folder) and fix any violations before you finish.

## Catalog workflow (when adding device IO)
- Import/update from the Stationeers wiki: `python tools/wiki_import.py <wiki-device-url>`
- Output is `catalog/devices/<WikiTitle>.json` + updated `catalog/index.json`.

If you’re unsure whether a task targets **tooling** (Python/catalog) or **pasteable scripts** (IC10 constraints), ask and default to preserving existing patterns.
