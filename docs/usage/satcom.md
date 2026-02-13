# SatCom setup checklist

SatCom now uses name-first auto-naming and shared data-network discovery.

Primary setup guide:

- `modular scripts/SatCom/Setup.md`

Quick checks:

- all SatCom devices are on one data network
- required names are exact/case-sensitive (`discover`, `cycle`, `dish`, etc.)
- manual dials are named exactly `dial_h` and `dial_v`
- controls worker housing is named exactly `controls_worker`
- `cmd_token`, `cmd_type`, `slot0..slot2` Logic Memory devices exist
- setup guard shows `db Setting = 1` before runtime testing

## Runtime debug flow (fast)

When controls appear unresponsive, read these values first:

- `master` (`db Setting`)
- `setup_guard` (`db Setting`)
- `controls_worker` (`db Setting`)
- `discover_worker` (`db Setting`)
- `cycle_worker` (`db Setting`)
- Logic Memory `cmd_type`, `cmd_token`
- Logic Memory `filter_status` (if configured)

Interpretation:

- `cmd_token` increments on button press -> controls worker command publish is working.
- `cmd_type` changes (`1` discover, `2` cycle, `3` clear) -> button routing is working.
- `controls_worker=344` -> missing/wrong controls (`discover`, `cycle`, `dial_h`, `dial_v`).
- `controls_worker=345` -> manual dial writes are active.
- `discover_worker=100` and `cycle_worker=200` while token increments -> workers are idle,
  usually due to missing prerequisite names/devices, not button failure.
- `cycle_worker=220` -> tune filter write verified.
- `cycle_worker=223` -> tune filter write mismatch.
- `cycle_worker=230` -> clear filter write verified.
- `cycle_worker=233` -> clear filter write mismatch.
- `setup_guard=97` -> missing/wrong `dish` on network.
- `setup_guard=98` -> missing/wrong `slot0/slot1/slot2` memories.
- `setup_guard=99` -> missing/wrong `dial_h`/`dial_v` dials.
- `master=44` -> controls worker reports missing controls.

## Guardrail learned from live debugging

Setup/validation chips must not continuously reset shared command channels.

- Initialize `cmd_type`/`cmd_token` once at startup.
- After init, only validate and report status; do not overwrite active command traffic.
