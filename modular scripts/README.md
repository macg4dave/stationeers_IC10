# Modular scripts

Multi-chip IC10 systems (master + workers) for jobs that do not fit one chip or that
need several independent loops. Each feature folder contains:

- `<feature>_master.ic10`, `<feature>_worker_<task>.ic10`, often a `_setup_guard`
- `README.md` — wiring, shared-memory contract, status-code tables
- `Setup.md` — player build list and step-by-step setup

## Features

| Feature | What it does | Chips | Sim coverage |
| --- | --- | --- | --- |
| `AutolatheVendStock/` | Keeps a Vending Machine stocked from one Autolathe; feeds ingots | 7 (+2 Free Ingots variants) | stock → machine → prep handshake, worker restart |
| `ingot_printer/` | Multi-Autolathe ingot printer for the Free Ingots mod | 5 | master slot sync |
| `PotatoHarvieTest/` | Potato grow loop: Hydroponics + Harvie(s) + Grow Light | 4 | actuator light cycle, harvest |
| `SatTraderTrack/` | Trader tracking with medium → large dish handoff and auto-land | 4 | master tokens, dish sweep |
| `_template/` | Starter master / worker / setup-guard files | — | lint + run only |

`AutolatheVendStock` `*.free_ingots.ic10` files are generated:
`python tools/autolathe_profile_emit.py free_ingots` (checked by `tools/check_all.py`).

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
Validate: `python tools/check_all.py`.
