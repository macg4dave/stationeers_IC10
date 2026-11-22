# IC10 script checklist

Use this when creating or editing a script in `scripts/` (most points also apply to
modular chips). Background and the reasons behind each rule: `AGENTS.md`.

## 1. Files

- `scripts/<script_name>/<script_name>.ic10` (short `snake_case`) and `README.md`.
- Copy `scripts/_template/` to start.

## 2. Header (top of the `.ic10`)

Script name, `Category | Status`, purpose in 1–3 lines, the `d0..d5`/`db` map, and any
note that prevents a common failure (units, required in-game settings).
Then one `alias <name> dN` per used pin, so the IC Housing labels it (naming rules:
`AGENTS.md`, "Names"). Use the alias names in the code, not `dN`.

## 3. Device guards

- Wait loop: `yield` then `bdns <alias> wait` for every required pin.
- In the main loop, guard pins before critical `l` reads if a device can be removed or
  lose power while the chip runs (`bdns sensor wait` at the top of `main`).
- Reading an unset pin halts the chip in-game.

## 4. Units

- Temperatures: Kelvin. `C = K - 273.15`.
- `Pressure` on Pipe Analyzer, Liquid Pipe Analyzer and Gas Sensor: **kPa**.
  Do not add "if it looks like Pa, divide by 1000" logic.
- Ratios (`Ratio*`, battery `Ratio`): 0..1.

## 5. Modes and enums

- Take `Mode` values from `catalog/devices/<Device>.json` → `io.modeValues`; `define`
  them; set them explicitly at startup; document them in the README.
- Active Vent: write `Mode`, `yield`, then `Setting` (a mode change resets its limits).
- LED Display `Mode 10` (string): pack two ASCII bytes as `c0*256 + c1`, digits as
  `48 + n`; quantise to integers first.

## 6. Control logic

- Hysteresis on every threshold that drives an actuator, unless the README explains why not.
- Read before write: `l cur dev On`, write only when it differs (also for `Setting`).
- Do not assume the start state of devices or registers: registers boot at 0.
- Branches: labels with `j`/`b*`; offsets with `br*`/`jr`.
- Use literal values in `define`.

## 7. Batch / name targeting

- `sbn`/`lbn`: structure prefab hash + exact `HASH("name")` (case-sensitive, no
  substrings). Verify hard-coded hashes with `ic10_hash()` (see `AGENTS.md`).
- Use the placed structure's prefab, not the kit item (Active Vent: `-1129453144`,
  not `-842048328`).
- Some devices ignore writes while `Lock = 1`; clear it first if the README says so.
- List every required in-game name in the README.

### Landingpad outputs

- Gas output → `RatioMethane`; liquid output → `RatioLiquidMethane`.
- Landingpad catalog entries are inferred (no wiki data network table). If a field
  faults at runtime, remove that access first (`Lock` is the usual suspect).

## 8. Status output

Write a small numeric status to `db Setting` when it helps in-game debugging, and list
the codes in the README.

## 9. Player README

Purpose; required devices and `d0..d5`; required names; in-game prerequisites (link
`docs/usage/<device>.md`); tuning constants with units; behaviour at and between
thresholds; limitations; troubleshooting; Status.

## 10. Validate

- Add or update a scenario in `tests/standalone.rs`.
- `cargo test` (paste limits, lint, contracts, catalog, docs, scenarios).
- Tell the user what was verified statically, what was simulated, and what still
  needs an in-game test.

## 11. Catalog and playbooks

- New "device does nothing" gotcha → add it to `docs/usage/`.
- Need authoritative LogicTypes → read the wiki page in a browser, edit `catalog/` by hand
  (see `catalog/README.md`). The wiki may lag the game.

## 12. Daylight-derived clocks

Document orientation, invert, offset and fine-shift constants with a calibration order;
say clearly that the time is derived from the sun angle (whole-degree resolution =
4 game minutes in `display_clock_from_sun`).

## 13. Modular features

See `docs/modular_master_worker_pattern.md` and the "Modular systems" section of
`AGENTS.md`; `cargo test` validates `Setup.md`.
