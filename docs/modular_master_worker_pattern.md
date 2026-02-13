# IC10 modular master + workers pattern

Use this pattern when one IC script becomes hard to maintain or exceeds paste limits.

## When to choose modular

Prefer **master + workers** when:

- the feature naturally splits into phases (discover -> act -> monitor)
- one chip needs orchestration while others do focused loops
- you want easier in-game debugging through per-chip status
- you expect future feature growth

## Core architecture

- **Master chip**
  - owns user inputs (buttons, mode switches)
  - enables/disables worker housings (`On`)
  - sends command tokens through shared memory
  - exposes high-level status through its own `db Setting`
- **Worker chips**
  - each does one task only
  - consume command/data contracts
  - expose worker-local status through their own `db Setting`

## Recommended data contract

For cross-chip communication, prefer dedicated **Logic Memory** devices over overloading worker housing fields.

- command channel: 1 Logic Memory slot (`Setting` = monotonically increasing token)
- data channel(s): N Logic Memory slots (`Setting` for values like SignalIDs)

### Why token commands?

Workers can detect **new command** as `token != prev_token` without edge-timing issues.

## Naming and folder layout

Use one feature folder:

- `modular scripts/<feature>/`
  - `<feature>_master.ic10`
  - `<feature>_worker_<task1>.ic10`
  - `<feature>_worker_<task2>.ic10`
  - `README.md` (wiring + contract + status codes)

Keep names short; paste limits count comments/aliases.

## Wiring order standard (required)

For modular systems where chips are wired to other chips (directly or through
shared command/data channels), reserve IC registers in this priority:

1. **Inter-chip links first** at `d0`, then `d1`, then `d2` (descending order)
2. User input devices (buttons/levers/switches)
3. Feature devices (dish, vents, analyzers, etc.)

This gives humans and AI a predictable map every time.

Example (master):

- `d0` = worker A housing (or worker-link channel)
- `d1` = worker B housing (or worker-link channel)
- `d2` = command token memory
- `d3` = command type memory
- `d4` = button 1
- `d5` = button 2

If a script has no inter-chip links, use normal per-feature mapping.

## Status code protocol (required)

Each chip should publish numeric status to its own `db Setting`.

Document status tables in feature `README.md`:

- master status codes (mode transitions, command emission)
- worker status codes (idle, active, success, no-data, error)

Use compact code ranges per chip (example):

- `0-99` master
- `100-199` worker A
- `200-299` worker B

## Worker script rules

- Gate required devices with `bdns` each loop.
- Keep logic single-purpose.
- Keep retries/timeouts local to worker.
- Prefer idempotent writes (write only when changed when practical).

## Master script rules

- Debounce momentary inputs (`prev` edge detect).
- Centralize mode transitions.
- Do not duplicate worker internals in master.
- If a worker is disabled, do not keep writing commands to it.

## README checklist for modular features

Include all of the following:

1. device mapping per chip (`d0..d5`, `db`)
2. explicit confirmation that inter-chip links start at `d0` and descend
3. shared memory contract (who writes/reads each slot)
4. button/control flow timeline
5. status code tables per chip
6. recovery steps (what to reset if stuck)

## AI prompt template for modular requests

```text
Build this as modular IC10 scripts using master + workers.

Feature name: <name>
Goal: <overall behavior>

Master responsibilities:
- <input handling>
- <mode transitions>
- <command token writes>

Worker responsibilities:
- worker A: <task>
- worker B: <task>

Shared memory contract:
- cmd slot: <device + meaning>
- data slot(s): <device + meaning>

Status protocol:
- assign non-overlapping status code ranges per chip
- write status to each chip's db Setting

Constraints:
- each .ic10 must stay under 128 lines / 90 chars per line
- include README with wiring + status table + usage
```
