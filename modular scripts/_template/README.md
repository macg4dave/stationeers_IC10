# modular scripts template (master + workers)

Use this folder as a starter for modular IC10 projects.

## Files

- `_template_master.ic10` - master orchestration skeleton
- `_template_worker_task.ic10` - worker token-consumer skeleton
- `_template_setup_guard.ic10` - generic auto-setup guard (portable)
- `_template_setup_guard_satcom_profile.ic10` - ready profile for button-based modules
- `Setup.md` - player-facing setup checklist template

## Recommended copy pattern

1. Create `modular scripts/<feature>/`
2. Copy and rename files:
   - `<feature>_master.ic10`
   - `<feature>_worker_<task>.ic10` (copy worker skeleton per task)
   - `<feature>_setup_guard.ic10` (optional, strongly recommended)
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

## Setup guard porting workflow (recommended)

Use setup guard scripts to make setup/debugging consistent across modules.

1. Start from `_template_setup_guard.ic10`.
2. Wire it using this stable map:
   - `d0` worker A housing
   - `d1` worker B housing
   - `d2` logic memory `cmd_token`
   - `d3` logic memory `cmd_type`
   - `d4` control A
   - `d5` control B
3. Optional type checks:
   - set `EXPECTED_A_HASH` / `EXPECTED_B_HASH`
   - keep `HASH_SKIP` to disable checks
4. Keep status codes reserved:
   - `0` boot
   - `10` one-time init completed
   - `1` steady/healthy
   - `94` control A type mismatch
   - `95` control B type mismatch

For button-based modules, `_template_setup_guard_satcom_profile.ic10` is a
ready baseline (`491845673` for both controls).

## Default reliability rails (use by default)

Make these part of every new modular feature unless there is a strong reason not to:

- **One-time channel init only** in setup guard:
  - initialize shared `cmd_token` / `cmd_type` once at startup
  - do not keep resetting shared channels in `main` loop
- **Prerequisite checks before healthy status**:
  - setup guard should report healthy only after required controls/channels/devices
    are validated
  - for name-based modules, validate required named channels/devices explicitly
- **Stable status-code contract**:
  - `0` boot, `10` init complete, `1` healthy
  - `94/95` control A/B mismatch
  - reserve `97/98` for missing critical downstream prerequisites
  - reserve `44` in master for missing primary controls (if used)
- **Runtime snapshot-first debugging**:
  - capture `master`, `setup_guard`, worker statuses, and command channel values
  - if `cmd_token` increments, input/master path is proven alive

## Status code ranges (suggested)

- Master: `0-99`
- Worker A: `100-199`
- Worker B: `200-299`

## Constraints

- Each `.ic10` must fit: **128 lines** and **90 chars/line**.
- Run: `python tools/ic10_size_check.py "modular scripts/" --ext .ic10`
- Run: `python tools/setup_contract_check.py`
