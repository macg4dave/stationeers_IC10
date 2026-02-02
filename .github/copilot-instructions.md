# Copilot instructions (stationeers_IC10)

This repository is intended to become an **IDE/tooling project for the Stationeers IC10 language** (MIPS-like in-game scripting) plus project-specific “extras”.

## Repository reality check
- The workspace may be empty at times; if there’s no code yet, **don’t invent** architecture, conventions, or workflows.
- When implementing language features, treat the Stationeers wiki as the current spec:
  - https://stationeers-wiki.com/IC10
  - https://stationeers-wiki.com/IC10/instructions

## First steps for any coding task
- Start by confirming what exists:
  - List the repo contents and look for newly added files/directories.
  - If the repo remains empty, ask the user whether they intended to clone/init the project, or want you to scaffold a structure.
- If files appear, immediately scan for project-level guidance first:
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
- Execution pacing: `yield` pauses 1 tick; scripts also auto-pause after a fixed number of executed lines (commonly 128) if no `yield` is used.
- Common gotcha: labels that shadow keywords/LogicTypes (for example `Temperature:`) can break scripts.

## When code is present
- Prefer **discovering** conventions from existing files rather than imposing generic patterns.
- When proposing changes, reference concrete examples by file path (for example: “follow the style in `path/to/file`”).
- If multiple script variants exist, ask which one is canonical before large refactors.

## Tooling and workflows
- This is a **text-based** project: IC10 programs are authored and stored as **plain text files** in the repo (no binary formats).
- Device IO flags (“Data Network Properties” variables like `Temperature`, `Pressure`, `On`) should come from the local catalog in `catalog/` when available.
- To add/update device variables from the wiki, use the importer in `tools/wiki_import.py` (input: a stationeers-wiki device URL; output: `catalog/devices/<WikiTitle>.json` plus `catalog/index.json`).
- No build/test/debug workflow is currently discoverable from this repository.
- If the user asks you to run anything, base commands on the actual files you find (for example, only suggest a toolchain after you locate config files).

## Clarifying questions to unblock work
- What Stationeers/IC10 environment or tooling do you use (in-game editor only, or external editor + upload)?
- What file format(s) are in this repo (for example `.ic10`, `.txt`, `.md`), and where do you want scripts organized?
- What are the “extras” beyond baseline IC10 (icX-like macros/compilation, custom directives, additional diagnostics, etc.)?
- Do you want a standard header/comment block in scripts (name, purpose, I/O pins, revision history)?
