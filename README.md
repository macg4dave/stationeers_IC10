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
- `tools/` - helper tools (Python, stdlib-only)
- `catalog/` - local JSON catalog of device Logic I/O names/types (imported from the Stationeers wiki)
- `.vscode/` - recommended VS Code extension + debug config
- `.github/copilot-instructions.md` - extra context for AI coding assistants (especially GitHub Copilot)

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

Use the size checker tool before pasting (see "Tools" below), especially after editing a script.

## AI-assisted scripting (Copilot / ChatGPT / etc.)

AI can be great for **small, testable** IC10 changes, script variants, and documentation. It's also easy for AI to generate IC10 that *looks* right but fails in-game, so use a tight loop: generate -> size-check -> paste -> test.

### Using GitHub Copilot in this repo (VS Code)

- Install **GitHub Copilot** (and **Copilot Chat**) in VS Code and sign in.
- Open this repo as a workspace.
- Copilot Chat will pick up repository-specific guidance from `.github/copilot-instructions.md`.

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
- Purpose: Turn on an Active Vent when Volatiles are present until Oxygen ratio is >= Volatiles ratio.
- Devices:
  - Pipe Analyzer
  - Active Vent
```

E.g. For importing from the wiki:
```text
- Import this item: <URL of the Stationeers wiki page for a device>
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

All tools are **stdlib-only Python** (no pip installs required).

### Check IC10 script size (paste limits)

- Script: `tools/ic10_size_check.py`
- Example:

```bash
python tools/ic10_size_check.py scripts/ --ext .ic10
```

### Import device IO from the Stationeers wiki into `catalog/`

- Script: `tools/wiki_import.py`
- Example:

```bash
python tools/wiki_import.py https://stationeers-wiki.com/Pipe_Analyzer
```

- Output:
  - `catalog/devices/<WikiTitle>.json`
  - `catalog/index.json`

---

## Developer notes (contributing / repo internals)

- IC10 language reference:
  - https://stationeers-wiki.com/IC10
  - https://stationeers-wiki.com/IC10/instructions
- AI-specific guidance for this repo lives in `.github/copilot-instructions.md` (it covers IC10 syntax, pacing, batch patterns, and documentation conventions).
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
