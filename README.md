# stationeers_IC10

This repository is intended to become IDE/tooling for the **Stationeers IC10** scripting language (plus project-specific extras).

At the moment, the repo contains a small but useful foundation:

- `catalog/` — local device I/O catalog (JSON)
- `tools/wiki_import.py` — import a device’s Data Network Properties from a Stationeers wiki page into `catalog/`
- `tools/ic10_size_check.py` — optional checker for in-game paste-into-chip constraints

## VS Code setup

This repo includes VS Code workspace helpers for the extension you installed:

- Recommended extension: `Traineratwot.stationeers-ic10` (see `.vscode/extensions.json`)
- Debugger launch config: `.vscode/launch.json` (uses debug `type: ic10`)

The extension also supports an optional **hardware environment** file in TOML:

- A `.toml` file in a folder can define device setup (e.g. `d0` PrefabHash/slots/reagents).
- A script-specific environment can be named to match the script base name (example: `solar.icx.ic10` → `solar.toml`).

## In-game constraints (IC10 chip)

The Stationeers in-game IC chip imposes size/line limits on the text you paste into the chip.
These limits are **in-game only** (they do not apply to repo tooling/source code unless you are generating final IC10 output).

## Tools

### Import device IO from the Stationeers wiki

- Script: `tools/wiki_import.py`
- Output: `catalog/devices/<WikiTitle>.json` and `catalog/index.json`

### Check IC10 script size

- Script: `tools/ic10_size_check.py`
- Checks:
  - line count
  - line width

