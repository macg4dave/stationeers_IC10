# Stationeers IC10 (scripts + tooling)

Copy/paste-friendly **Stationeers IC10** programs, plus small tools and VS Code helpers.

Start here: `scripts/` (each script has a folder with a setup guide + an `.ic10` file to paste into the game).

## Contents

- [What's in this repo](#whats-in-this-repo)
- [Quick start (players)](#quick-start-players)
- [AI-assisted scripting](#ai-assisted-scripting-copilot--chatgpt--etc)
- [Repo setup (optional)](#repo-setup-optional)
- [VS Code setup (recommended)](#vs-code-setup-recommended)
- [Tools (advanced)](#tools-advanced)
- [Developer notes](#developer-notes-contributing--repo-internals)

## What's in this repo

- `scripts/` - player-facing scripts (each script includes a `README.md` + a pasteable `.ic10`)
- `script set/` - groups of independent single-chip scripts that do one job together (e.g. landing pad gas into tanks)
- `modular scripts/` - modular multi-chip projects (master + worker IC10 files)
- `src/`, `Cargo.toml` - Rust tooling: IC10 lint, simulator, repo checks (`cargo test`)
- `catalog/` - local JSON catalog of device Logic I/O names/types (originally imported from the Stationeers wiki)
- `catalog/recipes/` - local JSON catalog of wiki recipe tables for producer devices (starting with `Autolathe`)
- `tests/` - simulated behaviour scenarios for the scripts (Rust integration tests)
- `docs/engineering_audit.md` - architecture, known defects, open risks, in-game test list
- `.vscode/` - recommended VS Code extension + debug config
- `AGENTS.md` - engineering guide for AI assistants (`.github/copilot-instructions.md` points to it)

## Quick start (players)

### 1) Pick a script

- Browse `scripts/` (quick list: `scripts/README.md`).
- Open the script folder and read its `README.md` first (it explains the required devices and the `d0..d5` mapping).

### 2) Copy the IC10 code

- Open: `scripts/<script_name>/<script_name>.ic10`
- Select all, copy.

Copy/paste tips:

- Copy from a plain-text editor (VS Code recommended) so you don't pick up extra formatting.
- Avoid "smart quotes" or unusual Unicode characters (the in-game editor can be picky).

### 3) Paste into the in-game IC chip

In Stationeers:

- Place an **IC Housing** and insert an **IC Chip**
- Open the chip editor
- Paste the script text
- Save/exit

Run `cargo run -- lint` before pasting (see "Tools" below), especially after editing a script.

## AI-assisted scripting (Copilot / ChatGPT / etc.)

AI can be great for **small, testable** IC10 changes, script variants, and documentation. It's also easy for AI to generate IC10 that *looks* right but fails in-game, so use a tight loop: generate -> `cargo test` -> paste -> test in-game.

### Using GitHub Copilot in this repo (VS Code)

- Install **GitHub Copilot** (and **Copilot Chat**) in VS Code and sign in.
- Open this repo as a workspace.
- Copilot Chat picks up `.github/copilot-instructions.md`, which points to `AGENTS.md`
  (the full guide; other agents such as Claude Code and Codex read `AGENTS.md` directly).

### Good tasks for AI

- Create a new script skeleton using this repo's existing script folder pattern.
- Add/adjust thresholds, timing, and fail-safe behavior (one change at a time).
- Refactor to fit paste limits (reduce line count / shorten long comment lines).
- Turn a one-off `d0..d5` script into a batch/network script using hashes (`lb/sb/lbn/sbn`).
- Write or improve a per-script (devices, mapping, tuning, usage steps).

### Prompt template (copy/paste)

```text

- Purpose: <what it should do>
- Devices: <list of required devices and their roles>
(optional) Device registers: <which devices go in d0..d5/db>
- Tuning constants (with units): <thresholds, pressures, temperatures, etc.>
(optional) Behavior rules: <if-then rules based on device readings>

E.g. For making a script.:
- Purpose: Turn on an Active Vent when Methane is present until Oxygen ratio is >= 33%.
- Devices:
  - Pipe Analyzer
  - Active Vent
```

E.g. For modular (master + workers):

```text
- Build this as modular IC10 scripts (master + workers).
- Put files under: modular scripts/<feature>/
- Feature name: <feature>
- Master chip: <button/mode/orchestration responsibilities>
- Worker chips:
  - worker A: <single task>
  - worker B: <single task>
- Shared memory contract:
  - command slot: <Logic Memory device used as command token>
  - data slots: <Logic Memory device(s) and meaning>
- Status protocol:
  - each chip writes status to its own db Setting
  - include status-code table in README
```

## Repo setup (optional)

### Option A: Download a ZIP

- Download the repo as a ZIP, extract it anywhere.
- Open it in VS Code (optional) to browse scripts and copy/paste cleanly.

### Option B: Clone with git

```bash
git clone <repo-url>
cd stationeers_IC10
```

## VS Code setup (recommended)

This repo includes VS Code workspace helpers:

- Extension: `Traineratwot.stationeers-ic10` (see `.vscode/extensions.json`)
- Debug launch config: `.vscode/launch.json` (uses debug `type: ic10`)

The extension also supports an optional **hardware environment** file in TOML:

- Put a `.toml` file next to scripts to define a device setup (e.g. `d0` prefab hash, slots, reagents).
- You can use a script-specific environment by matching the script base name (example: `solar.ic10` -> `solar.toml`).

## Tools (advanced)

The tooling is one Rust crate at the repo root (`Cargo.toml`, `src/`, `tests/`). Install
Rust from <https://rustup.rs>, then:

### Run every check (start here)

```bash
cargo test                      # static checks + every behaviour scenario
cargo run -- check              # static checks only, with a readable report
```

`cargo test` runs the IC10 lint (paste limits included), setup contracts, catalog
schema, doc path references, the generated-file check and the simulated scenarios in
`tests/`. Results mean different things:

- **static checks pass** - files are paste-ready and structurally sound
- **tests pass** - simulated behaviour matches the scenarios in `tests/`
- neither proves in-game behaviour; `docs/engineering_audit.md` lists what to test in-game

### Lint IC10 scripts

```bash
cargo run -- lint                                   # every shipped script
cargo run -- lint --info scripts/room_heater_hold_20c
```

Catches paste-limit overruns (128 lines, 90 chars, 4096 bytes), unknown instructions,
wrong operand counts, undefined labels, relative branches given a label
(`brlt x y label`), absolute jumps to a numeric line, LogicTypes not in the catalog,
unreachable code and registers read before they are written.

### Behaviour tests

`src/engine.rs` simulates the chip (128 lines per tick, `yield`/`sleep`, batch ops,
exact name hashes). Scenarios drive each script through its thresholds, hysteresis,
startup and fault cases; modular tests run several chips in lockstep.

### Game hashes

```bash
cargo run -- hash StructureActiveVent               # -1129453144
```

### Emit opt-in Autolathe profile variants

```bash
cargo run -- emit free_ingots
```

- Output:
  - `modular scripts/autolathe_restock_vending/autolathe_restock_worker_stock.<profile>.ic10`
  - `modular scripts/autolathe_restock_vending/autolathe_restock_worker_logistics.<profile>.ic10`
- Profile data lives in `catalog/recipes/Autolathe/profiles/`.

### Catalog

`catalog/` is edited by hand (the wiki importers were removed in the Rust rewrite).
`cargo test` checks every file against its schema (`src/catalog.rs`).

### Modular Setup.md contracts

Each modular feature's `Setup.md` must list its required sections (`Name contract`,
`Setup steps`), every `HASH("name")`, every shared channel (`cmd_token`, `cmd_type`,
`slotN`, `dataN`) and every script file. `cargo test` enforces this.

## Hashing quick rules (batch/network scripts)

When scripts use `lb/sb/lbn/sbn`, hash matching is strict:

- **Name hash is exact-match only** (case-sensitive). `HASH("cold")` matches only devices named exactly `cold`.
- Name-hash matching is **not** substring matching (so `cold_1` does not match `cold`).
- Prefer authoritative prefab hashes from `catalog/devices/<Device>.json` when filtering by type.
- If a script writes `On` but a device appears unchanged, verify lock/state requirements (many devices also need `Lock=0`).

If a script appears to "not find" devices, check in this order:

1. data network connectivity
2. exact in-game device name used by `HASH("...")`
3. prefab/type hash value used by the script
4. required lock/mode settings on the target device

---

## Developer notes (contributing / repo internals)

- IC10 language reference:
  - <https://stationeers-wiki.com/IC10>
  - <https://stationeers-wiki.com/IC10/instructions>
- AI-specific guidance for this repo lives in `AGENTS.md` (IC10 facts, sources of truth,
  rules for changing working scripts, testing requirements).
- Script conventions (when adding new scripts):
  - Prefer short `snake_case` names.
  - Keep scripts in `scripts/<script_name>/` with:
    - `<script_name>.ic10` (pasteable program)
    - `README.md` (player-facing setup and tuning)
  - Keep comments compact (paste limits count comment text).
- Keep `scripts/README.md` as a lightweight catalog so humans (and AI) can find the right automation quickly.
  - Consider tagging each script with a simple **status** (example scale: Experimental -> WIP -> Functional -> Stable -> Mature).
  - Optional: group by category labels like Controller / Set Controller / Array / Mirror / Utility.
- Per-script `README.md` (recommended structure):
  - Purpose (plain language), Devices (required/optional), Device registers (`d0..d5`/`db`), Usage (setup steps), Tuning (constants + units), Status, Credit.
- When authoring scripts that read/write device flags, prefer canonical names/types from `catalog/` over guessing.
