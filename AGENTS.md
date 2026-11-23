# AGENTS.md — engineering guide for AI agents (authoritative)

This repo ships **paste-ready Stationeers IC10 scripts** plus **one Rust crate**
that lints, simulates and checks them. This file is the single source of truth
for how to work here; `.github/copilot-instructions.md` only points back to it.

## Start every task with

1. `cargo test` — record what already fails *before* you change anything.
2. Read the script's `README.md` (and feature `README.md` + `Setup.md` for modular).
3. Read its scenario in `tests/` — it states the behaviour that must be preserved.

## Layout

- `scripts/<name>/<name>.ic10` + `README.md` — single-chip scripts (index: `scripts/README.md`)
- `modular scripts/<feature>/` — multi-chip systems: master, workers, setup guard,
  `README.md` (contract + status codes), `Setup.md` (player steps)
- `catalog/devices/*.json` — device LogicTypes, Mode values, prefab hashes (`catalog/README.md`)
- `src/` + `Cargo.toml` — Rust tooling (see "Rust tooling rules"); `cargo run -- check`
  for a static-check report, `cargo run -- lint|hash|emit`
- `tests/` — Rust scenarios run by the simulator (`cargo test`)
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
  `cargo run -- hash StructureActiveVent`.
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
3. The wiki, read by the user in a browser (the live wiki blocks scripts with a
   Cloudflare challenge). Catalog edits are by hand and additive: the wiki lags the
   game, so a field missing there is not proof it was removed.
4. Catalog entries with `"kind": "best_guess"` — treat as hypotheses.

When you cannot verify a behaviour, keep the existing implementation and write the
uncertainty down (README "Notes", `docs/engineering_audit.md`). Never invent an
instruction, LogicType, Mode value or device capability.

## Changing a script that already works in-game

- Reproduce first: add a scenario that fails on the current script, then fix it in the
  same commit. A defect that is not fixed yet goes in `docs/engineering_audit.md`, not
  in an ignored test.
- One defect per commit; say *why* in the commit and in the script README
  ("Change history"). Keep the author's `Status` label unchanged.
- Script names follow `<where it lives>_<what it does>` (old names: `docs/renames.md`).
  Do not rename folders, device names (`HASH("...")`), pins or status codes unless the
  user asks: players have these wired in-game. If a contract must change, update every script, `README.md`
  and `Setup.md` that uses it in the same commit and call it out.
- Prefer the smallest correct change. Do not restyle working code.
- Re-run `cargo test`; report results as **static**, **simulated** or
  **in-game** — only the user can confirm the last one.

## Writing a new script

- Start from `scripts/_template/` (or `modular scripts/_template/`) and follow
  `docs/ic10_script_checklist.md`.
- Paste limits: **128 lines, 90 chars/line, 4096 bytes**, comments included. Keep
  aliases short (see "Names"). When a script is over a limit, remove comments first
  (header lines included; README keeps that information), and only then compress code,
  keeping behaviour unchanged.
- Actuators: read before write (`l cur dev On` → write only on change).
- Thresholds: add hysteresis unless the README says why not.
- House style for single-chip scripts (all of `scripts/` follows it): a 2–6 line
  header (name - purpose, pins, behaviour, status codes), unless the lines are needed
  for code; `bdns` for every pin in the
  wait loop *and* the main loop; analyzer `Error` / no reading → safe state; status on
  `db Setting` with `9` = device missing or bad reading (skip when `db` is the device
  the chip lives in, e.g. an AC or a suit).
- Startup: never assume a device's initial state.
- Prefer exact-name targeting (`sbn` with prefab + `HASH("name")`) for groups and
  safety-critical paths; document every required name in the README.
- Add a scenario to `tests/` and a row to `scripts/README.md`.
- Solar panels in this repo use only the four cardinal headings `0/90/180/270` unless
  the user asks otherwise.

## Names: aliases, defines, labels

The IC Housing labels a pin only after the script runs `alias <name> dN`. A script
without aliases shows bare, unlabelled pins in-game, so every script aliases its pins.

- **Pins:** one `alias <name> dN` per used pin, straight after the header, in pin
  order. Mark optional pins with a trailing comment (`alias led d3  # optional, ...`).
  After the alias, use the name everywhere, `bdns` included, never the raw `dN`.
  Never alias `db`.
- **Pin names** say what the device does in this script, in short lower case:
  `dish`, `vent`, `heater`, `sensor`, `lever`, `led`. Use the role, not the prefab
  (`dish`, not `large_dish`). For two of a kind, name each by its role (`hot`/`cold`,
  `in`/`out`). Use `_a`/`_b` only when the roles are the same, and digits only for
  indexed slots (`slot0`). Modular systems name inter-chip links after what is on the
  other end (`worker_a`, `cmd_slot`) and alias unused pins `n0..n5`.
- **Registers:** alias the ones that keep a meaning across the loop, in lower case:
  `cur`/`want` for read-before-write, quantities with their unit (`kpa`, `tc` for °C),
  `state`, `ticks`. Short-lived scratch values may stay raw `rN`. When the line limit
  leaves no room, raw registers are fine.
- **`define`** names are `UPPER_SNAKE` with their unit where it helps (`SCAN_W`,
  `MAX_KPA`). **Labels** are lower-case `snake_case` verbs or states (`wait`, `scan`,
  `lock`, `set_on`).
- A name must not be an instruction (`move`, `select`), a register or pin (`r0`, `sp`,
  `ra`, `d0`, `db`), or another alias/define/label in the same script. LogicTypes are
  PascalCase, so lower-case names never clash with them.
- The README pin table has a `Name` column: `| Pin | Name | Device |`.
- In a shipped script, do not rename existing aliases to fit this convention: players
  know their pins by those labels. A script that has no aliases gets them, keeping the
  same pin numbers.

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
  shared channel; `cargo test` enforces this (`src/repo.rs`).

## Rust tooling rules

All tooling is one Rust crate: `src/engine.rs` (IC10 parser, lint, simulator),
`src/catalog.rs` (catalog schemas, check, generated workers), `src/repo.rs` (repo-wide
checks), `src/main.rs` (`ic10` CLI), `tests/*.rs` (scenarios; helpers in
`tests/common/mod.rs`). Keep it that way: new tooling goes in Rust, in these files.

**Style: combine, merge, delete.**

- Before adding code, look for code to reuse, extend or delete. A change that removes
  lines beats one that adds them; the best fix often deletes a special case.
- Merge near-duplicates: two functions or tests that differ by data become one with a
  table (`for (input, want) in [...]`). Grow an existing module before making a new one.
- Delete dead code, unused parameters, forwarding wrappers, commented-out code and
  stale comments in the same change. Nothing is kept "for later".
- No abstractions without two real callers: no traits, generics, builders or config
  for a single use. The `Logic` trait exists because tests model reacting devices.
- Use well-known crates for generic work (`serde`/`serde_json`, `regex`, `glob`,
  `clap`, `crc32fast`) instead of writing your own; use std when it is a few lines. Add
  a dependency only when it removes real code. The IC10 engine is ours on purpose:
  `ryex/ic10emu` was evaluated on 2026-11-21. Its game data predates Methane
  (`RatioVolatiles`, no `RatioMethane`), and it needs the full prefab database for
  every device.

**No placeholders, no try.**

- No `todo!()`, `unimplemented!()`, `TODO`/`FIXME`/`XXX` comments, stub functions or
  `#[ignore]` tests. Finish the work or leave it out, and record open questions in
  `docs/engineering_audit.md`.
- No `?`, `try` blocks, `try!` or `catch_unwind`. Handle each failure where it
  happens:
  - a check records it as an error line (`path:line: message`);
  - the simulator records it in `Chip::halted`, as the in-game chip halts;
  - `main` prints it and returns a failing `ExitCode`.
  Use `match`, `let ... else` and `unwrap_or*`.
- No `unwrap()`. `expect("...")` only for values that cannot fail at runtime (constant
  regexes). No `unsafe`, no `dbg!`.
- These rules are enforced by `[lints]` in `Cargo.toml` and
  `tests/repo.rs::rust_code_follows_the_house_rules`.

**Workflow.** `cargo fmt`, `cargo clippy --all-targets -- -D warnings` and
`cargo test` all pass before every commit. A new scenario must be able to fail: break
the script on purpose once and watch the test go red. Assertion messages say which
behaviour broke (`"analyzer error forces OFF"`).

## Do not

- Add frameworks, macro systems or "shared libraries" for IC10: every shipped `.ic10`
  must stand alone and paste into the game.
- Merge scripts only because they look alike — they often serve different setups.
- Claim a script works in-game because lint and tests pass.
- Overwrite `*.free_ingots.ic10` by hand: they are generated
  (`cargo run -- emit free_ingots`).
