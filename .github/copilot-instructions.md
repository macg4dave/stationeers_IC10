# Copilot instructions (stationeers_IC10)

This repository is intended to become an **IDE/tooling project for the Stationeers IC10 language** (MIPS-like in-game scripting) plus project-specific “extras”.

## Repository reality check
- The workspace may be empty at times; if there’s no code yet, **don’t invent** architecture, conventions, or workflows.
- Prefer **discovering** conventions from existing files rather than imposing generic patterns.
- For language semantics, treat these as the current spec:
  - https://stationeers-wiki.com/IC10
  - https://stationeers-wiki.com/IC10/instructions

## First steps for any coding task
- List the repo contents and look for newly added files/directories.
- Scan for project-level guidance first:
  - `README.md`
  - `.github/copilot-instructions.md` (this file)
  - `AGENTS.md`, `AGENT.md`, `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`

## IC10 essentials (for parsers, linters, and editor UX)
- Comments start with `#` and run to end-of-line.
- Labels end with `:` and represent a **line number** for jumps/branches (avoid relying on label numeric values in calculations).
- Registers: `r0`…`r15`, plus special `sp` (stack pointer) and `ra` (return address).
- Device registers: `d0`…`d5` and `db` (device the IC is mounted on). Network/connection refs use `d?:<n>` (example `db:0`).
- Numbers: decimal floating point; hex prefix `$` (common for ReferenceId); binary prefix `%` with optional `_` separators.
- Indirect addressing: extra leading `r` enables pointer dereference (example `rr0` points to `r<value-of-r0>`; similarly `dr0` for devices).
- Stack is 512 entries; `push/pop/peek/poke` exist and the stack can be persistent on IC chips.
- Execution pacing: `yield` pauses 1 tick; scripts also auto-pause after a fixed number of executed lines if no `yield` is used.
- Common gotcha: labels that shadow keywords/LogicTypes (for example `Temperature:`) can break scripts.

## In-game constraints (only when generating paste-into-game IC10)
- The Stationeers in-game IC chip imposes line/size limits on the text you paste into the chip.
- These limits are **game constraints**, not repo constraints; do not apply them to tooling/IDE code unless a task explicitly targets the in-game script output.

## Recommended repo layout (scripts + environments)
This repo is text-based and currently does not enforce a canonical scripts directory. When adding scripts, prefer a simple, scalable layout (adjust if the repo later standardizes differently):

- `scripts/`
  - `ic10/` — hand-written IC10 programs (the text you paste in-game)
  - `icx/` — optional icX sources (compiled to IC10 by the VS Code extension)
  - `env/` — optional environment `.toml` files (either per-folder or per-script)

Guidelines:
- Keep “source” vs “generated” explicit.
- If you use icX, treat `.icX` as the source-of-truth and the generated `.ic10` as output.
- If you’re not using icX, just use `scripts/ic10/` and skip the rest.

## Script management conventions
### File naming
- Use short, descriptive names; avoid spaces; prefer `snake_case`.

### Script catalog + maturity status (helps humans and AI)
- Keep a lightweight “catalog” of scripts (for example in `scripts/README.md`) so people can quickly find the right automation.
- For each script, track a **status** to set expectations (example scale): `Experimental` → `Work in Progress` → `Functional` → `Stable` → `Mature`, plus `Legacy` / `Retired` when applicable.
- Group scripts by a simple category label to make intent obvious:
  - **Controller**: device automation (thresholds, timers, PID/PD, etc.)
  - **Set Controller**: broadcast one command to many devices (often batch writes)
  - **Array**: loop over devices and manage each independently
  - **Mirror**: read → write passthrough (rebroadcast telemetry)
  - **Utility / Logistics**: orchestration/QoL beyond a single device

### In-file header (keep it short)
Add a compact comment header at the top of scripts when helpful, without wasting lines:
- purpose (1 line)
- device map: what is connected to `d0..d5` and assumptions about `db`
- key hashes/constants

### Per-script README (player-facing documentation)
If a script is meant to be used by players, prefer keeping it in a per-script folder with a `README.md` describing setup.
Use a consistent structure so tooling (and the AI) can find details quickly:
- **Purpose**: 1–2 lines, plain language (avoid heavy control-theory jargon)
- **Devices**: what’s required vs optional
- **Device registers**: what `d0..d5` and `db` should point at
- **Batch/hashes/labels/slots/reagents/stack**: only if used; list what is targeted and why
- **Usage**: numbered setup steps (include an in-game rename scheme if helpful)
- **Tuning**: constants to adjust, including units
- **Status**: maturity of the script
- **Credit**: if inspired by or adapted from elsewhere, credit the idea/source

### Device mapping discipline
- Document device intent near the top (comments and/or `alias`).
- Prefer `alias` for readability, but keep alias names short to stay under 90 columns.
- When writing/reading device flags (Data Network Properties), prefer canonical names/types from `catalog/` over guessing.

Documentation tip:
- When a script uses constants (`define`) for tuning (thresholds, pressures, temperatures), annotate units and intent in the README (and optionally in comments near the defines).

In-game note:
- Players can rename devices in Stationeers. When authoring scripts meant for players, include a recommended rename scheme in the per-script `README.md` (example: rename a Pipe Analyzer to `read_pipe_temp_1`) to make assigning `d0..d5` less error-prone.

### Labels and control flow
- Keep labels short and non-colliding.
- Avoid labels that shadow instruction names or LogicType-style identifiers.
- For loop-style scripts, include `yield` (or explicitly design around pacing).

### In-game size checks (optional)
- Only when you are producing IC10 that will be pasted into the in-game chip, you can validate constraints with `tools/ic10_size_check.py`.

### Environment files (.toml)
When using the `Traineratwot.stationeers-ic10` VS Code extension:
- Folder environment: a `.toml` file in a folder can define the hardware environment for scripts in that folder.
- Script-specific environment: name the `.toml` to match the script base name (example from extension docs: `solar.icx.ic10` → `solar.toml`).

## Tooling and workflows
- This is a **text-based** project: IC10 programs are authored and stored as **plain text files** in the repo (no binary formats).

### VS Code extension support
- The extension `Traineratwot.stationeers-ic10` provides syntax highlighting, tooltips, snippets, and an IC10 debugger (`type: ic10`).
- This repo includes starter VS Code configs:
  - `.vscode/extensions.json` recommends the extension
  - `.vscode/launch.json` includes example debug configurations

### Local device IO catalog
- Device IO flags (“Data Network Properties” variables like `Temperature`, `Pressure`, `On`) should come from the local catalog in `catalog/` when available.
- To add/update device variables from the wiki, use `tools/wiki_import.py`:
  - input: a stationeers-wiki device URL
  - output: `catalog/devices/<WikiTitle>.json` plus `catalog/index.json`

### Size checker
- `tools/ic10_size_check.py` exists to validate in-game paste-into-chip constraints when needed.

## Clarifying questions to unblock work
- What Stationeers/IC10 workflow do you use (in-game editor only, or external editor + copy/paste)?
- What script file extensions should this repo treat as canonical (`.ic10`, `.icX`, `.icx.ic10`, `.txt`)?
- Do you want generated `.ic10` output committed, or treated as disposable build output?
- What are the “extras” beyond baseline IC10 (icX-like macros/compilation, custom directives, additional diagnostics, etc.)?
