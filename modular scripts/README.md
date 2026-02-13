# Modular scripts

This folder contains **multi-chip IC10 projects** using a master + workers architecture.

## Folder layout

Each modular feature lives in:

- `modular scripts/<feature>/`
  - `<feature>_master.ic10`
  - `<feature>_worker_<task>.ic10` (one or more)
  - `README.md` (wiring + command/data contract + status table)

## Included projects

- `SatCom/` — Satellite communications modular scaffold.
- `_template/` — Starter master/worker template for new modular features.

## Notes

- Wiring standard: if chips are wired to other chips/channels, assign those
  links first at `d0`, `d1`, `d2`... then map buttons/feature devices.
- End-user setup guide: `docs/usage/modular_wiring_setup.md`.
- SatCom example setup guide: `docs/usage/satcom.md`.
- Keep every chip paste-ready: 128 lines / 90 chars per line.
- Validate with:
  - `python tools/ic10_size_check.py "modular scripts/" --ext .ic10`
