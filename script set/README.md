# Script sets

A script set is a group of single-chip scripts that do one job together. Each chip
works on its own: there is no shared Logic Memory, no master and no command
channel (those are `modular scripts/`). You can build one chip of a set and add the
others later.

Each set has its own folder:

- `script set/<set>/<chip>.ic10` — paste each into its own IC chip
- `script set/<set>/README.md` — what the set does, the build, every chip's pins,
  settings and status codes, setup steps

Chips follow the same conventions as `scripts/README.md` (pins checked every loop,
faults switch outputs off, status on the IC Housing `Setting`, `9` = device missing or
bad reading).

## Sets

| Set | What it does | Chips | Sim |
| --- | --- | --- | --- |
| `landing_pad_gas_storage/` | Trader gas from the landing pad into one tank per gas (8 gases known, room for 12); dirty gas to Waste; purge vent when Waste is full; the main pipe is cleared before the next gas | 2 (`pad_gas_router`, `main_pipe_purge`) | yes |

Every chip is simulated in `tests/standalone.rs`, not yet run in-game.
