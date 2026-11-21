# AGENTS.md — engineering guide for AI agents (authoritative)

This repo ships **paste-ready Stationeers IC10 scripts** plus **stdlib-only Python
tooling** that validates and simulates them. This file is the single source of truth
for how to work here; `.github/copilot-instructions.md` only points back to it.

## Start every task with

1. `python tools/check_all.py` — record what already fails *before* you change anything.
2. Read the script's `README.md` (and feature `README.md` + `Setup.md` for modular).
3. Read its scenario in `tests/` — it states the behaviour that must be preserved.

## Layout

- `scripts/<name>/<name>.ic10` + `README.md` — single-chip scripts (index: `scripts/README.md`)
- `modular scripts/<feature>/` — multi-chip systems: master, workers, setup guard,
  `README.md` (contract + status codes), `Setup.md` (player steps)
- `catalog/devices/*.json` — device LogicTypes, Mode values, prefab hashes (`catalog/README.md`)
- `tools/` — `check_all.py` (run everything), `ic10_lint.py`, `ic10_engine.py`
  (parser + simulator), size/setup/catalog/doc checkers, wiki importers, generator
- `tests/` — `unittest` scenarios run by the simulator
- `docs/` — checklists, modular pattern, device playbooks (`docs/usage/`)
- `docs/engineering_audit.md` — known defects, open risks, what still needs in-game tests

## IC10 facts this repo relies on (verified or test-encoded)

- **Branches:** `j`, `beq`, `bnez`, `blt`, ... jump to an *absolute* line or label.
  `br*` (`brlt`, `breqz`, ...) and `jr` add an *offset* to the current line. A label
  passed to a `br*` instruction is a bug (lint `E004`); a numeric target on an
  absolute branch is almost always a bug (lint `W005`). This caused two shipped defects.
- **Timing:** one tick runs up to 128 lines, *including* comments, labels and blank
  lines, or until `yield`/`sleep`. 2 ticks per second (`sleep 1` = 2 ticks).
- **Registers** `r0..r15`, `sp` (r16), `ra` (r17). All registers start at 0, so a state
  register that means "off" at 0 will skip the first real write; initialise it to a
  sentinel (`-1`) if the first loop must apply state.
- **Devices:** reading/writing an unset pin halts the chip. Guard pins with
  `bdns d0 <label>` in the wait loop and before critical reads in the main loop.
- **Batch ops** (`lb/sb/lbn/sbn`) match **prefab hash** and, for `*n`, an **exact,
  case-sensitive name hash**. `HASH("cold")` matches `cold`, never `cold_1` or `Cold`.
- **Hashes** are the signed CRC-32 of the prefab name. Verify a hard-coded hash with
  `python -c "import sys; sys.path.insert(0,'tools'); from ic10_engine import ic10_hash; print(ic10_hash('StructureActiveVent'))"`.
  Use the **placed structure** prefab (`identity.structureHash` when present), not a
  kit/item hash, for devices on the network.
- **Units:** temperatures are Kelvin (`C = K - 273.15`). Pipe Analyzer, Liquid Pipe
  Analyzer and Gas Sensor `Pressure` are **kPa**. Do not add "looks like Pa, divide by
  1000" guesses — that heuristic caused a pump runaway at 10 MPa.
- **Methane replaced Volatiles** in the game (`RatioMethane`, `RatioLiquidMethane`).
  Many wiki tables still say Volatiles; trust the scripts and catalog.
- `and`/`or` are bitwise; flag words like `and r0 flags 16` work.
- `alias` executes at runtime (a script may re-bind an alias); `define` and labels are
  resolved before the program runs. Use literal values in `define` (not other names).
- `Mode` values: read `io.modeValues` in `catalog/devices/<Device>.json`. Never guess.
  Changing an Active Vent's `Mode` resets its pressure limits, so write `Mode`, `yield`,
  then `Setting`.

## Sources of truth (strongest first) and how to record confidence

1. Behaviour the user confirmed in-game.
2. Game data: prefab name → CRC-32 hash; LogicType names used by working scripts.
3. Wiki via browser export (the live wiki blocks scripts with a Cloudflare challenge):
   user exports `https://stationeers-wiki.com/Special:Export` ("Include templates") into
   `temp/`, then `python tools/wiki_xml_import.py temp/<file>.xml` (compare) or `--write`
   (additive merge). The wiki lags the game: a field missing there is not proof it was
   removed.
4. Catalog entries with `"kind": "best_guess"` — treat as hypotheses.

When you cannot verify a behaviour, keep the existing implementation and write the
uncertainty down (README "Notes", `docs/engineering_audit.md`). Never invent an
instruction, LogicType, Mode value or device capability.

## Changing a script that already works in-game

- Reproduce first: add a scenario that fails on the current script, then fix.
  The tests use `@known_defect("Dn")` for defects not yet fixed.
- One defect per commit; say *why* in the commit and in the script README
  ("Change history"). Keep the author's `Status` label unchanged.
- Script names follow `<where it lives>_<what it does>` (old names: `docs/renames.md`).
  Do not rename folders, device names (`HASH("...")`), pins or status codes unless the
  user asks: players have these wired in-game. If a contract must change, update every script, `README.md`
  and `Setup.md` that uses it in the same commit and call it out.
- Prefer the smallest correct change. Do not restyle working code.
- Re-run `python tools/check_all.py`; report results as **static**, **simulated** or
  **in-game** — only the user can confirm the last one.

## Writing a new script

- Start from `scripts/_template/` (or `modular scripts/_template/`) and follow
  `docs/ic10_script_checklist.md`.
- Paste limits: **128 lines, 90 chars/line, 4096 bytes**, comments included. Keep
  aliases short. Compressing code to fit is fine if behaviour is unchanged.
- Actuators: read before write (`l cur dev On` → write only on change).
- Thresholds: add hysteresis unless the README says why not.
- House style for single-chip scripts (all of `scripts/` follows it): a 2–6 line
  header (name - purpose, pins, behaviour, status codes); `bdns` for every pin in the
  wait loop *and* the main loop; analyzer `Error` / no reading → safe state; status on
  `db Setting` with `9` = device missing or bad reading (skip when `db` is the device
  the chip lives in, e.g. an AC or a suit).
- Startup: never assume a device's initial state.
- Prefer exact-name targeting (`sbn` with prefab + `HASH("name")`) for groups and
  safety-critical paths; document every required name in the README.
- Add a scenario to `tests/` and a row to `scripts/README.md`.
- Solar panels in this repo use only the four cardinal headings `0/90/180/270` unless
  the user asks otherwise.

## Modular systems

- Use multiple chips only when one chip cannot hold the job or needs independent
  loops. Fewer chips and fewer shared channels are better.
- Give each shared Logic Memory slot **one writer**. If two chips must write, document
  who writes which value and when.
- Publish a command token only if some chip consumes it.
- Setup guards initialise shared channels once, then only validate and report.
- Pins: inter-chip links first (`d0` upward), then user inputs, then devices; alias
  unused pins `n0..n5`. Status per chip on its own `db Setting`, documented in README.
- `Setup.md` must list every `IC Housing:` name, every `HASH("...")` name and every
  shared channel; `tools/setup_contract_check.py` enforces this.

## Do not

- Add frameworks, macro systems or "shared libraries" for IC10: every shipped `.ic10`
  must stand alone and paste into the game.
- Merge scripts only because they look alike — they often serve different setups.
- Claim a script works in-game because lint and tests pass.
- Overwrite `*.free_ingots.ic10` by hand: they are generated
  (`python tools/autolathe_profile_emit.py free_ingots`).
