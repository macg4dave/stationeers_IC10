# Modular scripts

This folder contains **multi-chip IC10 projects** using a master + workers architecture.

## Folder layout

Each modular feature lives in:

- `modular scripts/<feature>/`
  - `<feature>_master.ic10`
  - `<feature>_worker_<task>.ic10` (one or more)
  - `README.md` (wiring + command/data contract + status table)

## Included projects

- `AutolatheBatch/` — Simple modular Autolathe batch-runner test rig (master + worker + setup guard).
- `AutolatheVendStock/` — Simplified fully automatic single-Autolathe vending stocker (no buttons).
- `PrinterHall/` — Shared-bus multi-Autolathe hall controller with selector, logistics, overflow, and idle workers.
- `SmallDishHandoff/` — Two-chip scanning/contact satellite dish handoff using one Logic Memory slot.
- `SatCom/` — Satellite communications modular scaffold.
- `_template/` — Starter master/worker template for new modular features.

## Notes

- Wiring standard: if chips are wired to other chips/channels, assign those
  links first at `d0`, `d1`, `d2`... then map buttons/feature devices.
- End-user setup guide: `docs/usage/modular_wiring_setup.md`.
- SatCom example setup guide: `modular scripts/SatCom/Setup.md`.
- Keep every chip paste-ready: 128 lines / 90 chars per line.
- Validate with:
  - `python tools/ic10_size_check.py "modular scripts/" --ext .ic10`
  - `python tools/setup_contract_check.py`
