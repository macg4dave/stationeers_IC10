# stationeers_IC10

This repository is intended to become IDE/tooling for the **Stationeers IC10** scripting language (plus project-specific extras).

At the moment, the repo contains a small but useful foundation:

- `catalog/` — local device I/O catalog (JSON)
- `tools/wiki_import.py` — import a device’s Data Network Properties from a Stationeers wiki page into `catalog/`
- `tools/ic10_size_check.py` — check IC10 script size constraints (128 lines, 90 chars/line)

## VS Code setup

This repo includes VS Code workspace helpers for the extension you installed:

- Recommended extension: `Traineratwot.stationeers-ic10` (see `.vscode/extensions.json`)
- Debugger launch config: `.vscode/launch.json` (uses debug `type: ic10`)

The extension also supports an optional **hardware environment** file in TOML:

- A `.toml` file in a folder can define device setup (e.g. `d0` PrefabHash/slots/reagents).
- A script-specific environment can be named to match the script base name (example: `solar.icx.ic10` → `solar.toml`).

## Hard limits (IC10 chip constraints)

- Max **128 lines**
- Max **90 characters per line**

## Tools

### Import device IO from the Stationeers wiki

- Script: `tools/wiki_import.py`
- Output: `catalog/devices/<WikiTitle>.json` and `catalog/index.json`

### Check IC10 script size

- Script: `tools/ic10_size_check.py`
- Checks:
  - line count
  - line width

