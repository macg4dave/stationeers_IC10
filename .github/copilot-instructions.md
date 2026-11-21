# Copilot instructions (stationeers_IC10)

Read **`AGENTS.md`** at the repo root first; it is the authoritative engineering
guide. The essentials, in case you only read this file:

- Shipped `.ic10` must paste into the game: 128 lines, 90 chars/line, 4096 bytes.
- `br*` instructions take a relative *offset*; labels go with `j`/`b*`.
- Temperatures are Kelvin; analyzer and gas sensor `Pressure` is kPa (no Pa guessing).
- The game uses `RatioMethane` (Volatiles was replaced); the wiki may lag.
- Batch name hashes are exact and case-sensitive; use structure prefab hashes.
- Read `catalog/devices/<Device>.json` for LogicTypes and `modeValues`; never guess.
- Preserve working behaviour: add a failing test in `tests/` before fixing a script.
- Run `cargo test` before and after changes; Rust rules are in `AGENTS.md`.
