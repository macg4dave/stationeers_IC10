# Modular scripts

Multi-chip IC10 systems (master + workers) for jobs that do not fit one chip or that
need several independent loops. Each feature folder contains (old folder names: `docs/renames.md`):

- `<feature>_master.ic10`, `<feature>_worker_<task>.ic10`, often a `_setup_guard`
- `README.md` — wiring, shared-memory contract, status-code tables
- `Setup.md` — player build list and step-by-step setup

## Features

| Feature | What it does | Chips | Sim coverage |
| --- | --- | --- | --- |
| `autolathe_restock_vending/` | Keeps a Vending Machine stocked from one Autolathe; feeds ingots | 7 (+2 Free Ingots variants) | stock → machine → prep handshake, worker restart, feeder requests once |
| `autolathe_ingot_printer/` | Multi-Autolathe ingot printer for the Free Ingots mod | 5 | master slot sync |
| `farm_potato_grower/` | Potato grow loop: Hydroponics + Harvie(s) + Grow Light | 4 | actuator light cycle, harvest |
| `_template/` | Starter master / worker / setup-guard files | — | lint + run only |

`autolathe_restock_vending` `*.free_ingots.ic10` files are generated:
`cargo run -- emit free_ingots` (checked by `cargo test`).

## Conventions

- Inter-chip links take the lowest pins (`d0`, `d1`, ...), then user inputs, then
  feature devices. Unused pins are aliased `n0..n5` so the housing labels stay current.
- Each chip reports a numeric status on its own `db Setting`; tables are in each
  feature `README.md`.
- Shared state lives in named Logic Memory devices (`cmd_token`, `cmd_type`, `slotN`).
  Give each slot a single writer where possible; see
  `docs/modular_master_worker_pattern.md`.
- Setup guards initialise shared channels once, then only validate.

Setup walkthrough for players: `docs/usage/modular_wiring_setup.md`.
Validate: `cargo test`.
