# modular scripts template (master + workers)

Use this folder as a starter for modular IC10 projects.

## Files

- `_template_master.ic10` - master orchestration skeleton
- `_template_worker_task.ic10` - worker token-consumer skeleton
- `Setup.md` - player-facing setup checklist template

## Recommended copy pattern

1. Create `modular scripts/<feature>/`
2. Copy and rename files:
   - `<feature>_master.ic10`
   - `<feature>_worker_<task>.ic10` (copy worker skeleton per task)
3. Copy `Setup.md` and fill in player-facing setup only:
   - build list
   - setup steps
   - per-chip `d0..d5` wiring map
   - controls
4. Add a feature `README.md` with:
   - per-chip `d0..d5` mapping
   - for modular links, reserve `d0..` first for chip/channels then buttons/devices
   - shared memory contract (cmd/data slots)
   - status-code table (`db Setting` for each chip)

## Status code ranges (suggested)

- Master: `0-99`
- Worker A: `100-199`
- Worker B: `200-299`

## Constraints

- Each `.ic10` must fit: **128 lines** and **90 chars/line**.
- Run: `python tools/ic10_size_check.py "modular scripts/" --ext .ic10`
