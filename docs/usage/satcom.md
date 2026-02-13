# SatCom setup checklist

SatCom now uses name-first auto-naming and shared data-network discovery.

Primary setup guide:

- `modular scripts/SatCom/Setup.md`

Quick checks:

- all SatCom devices are on one data network
- required names are exact/case-sensitive (`discover`, `cycle`, `dish`, etc.)
- manual dials are named exactly `dial_h` and `dial_v`
- `cmd_token`, `cmd_type`, `slot0..slot2` Logic Memory devices exist
- setup guard shows `db Setting = 1` before runtime testing

## Runtime debug flow (fast)

When controls appear unresponsive, read these values first:

- `master` (`db Setting`)
- `setup_guard` (`db Setting`)
- `discover_worker` (`db Setting`)
- `cycle_worker` (`db Setting`)
- Logic Memory `cmd_type`, `cmd_token`

Interpretation:

- `cmd_token` increments on button press -> master edge and command publish are working.
- `cmd_type` changes (`1` discover, `2` cycle, `3` clear) -> button routing is working.
- `discover_worker=100` and `cycle_worker=200` while token increments -> workers are idle,
  usually due to missing prerequisite names/devices, not button failure.
- `cycle_worker=240` -> manual dial control is actively writing dish H/V.
- `setup_guard=97` -> missing/wrong `dish` on network.
- `setup_guard=98` -> missing/wrong `slot0/slot1/slot2` memories.
- `master=44` -> missing/wrong `discover` or `cycle` button name/type.

## Guardrail learned from live debugging

Setup/validation chips must not continuously reset shared command channels.

- Initialize `cmd_type`/`cmd_token` once at startup.
- After init, only validate and report status; do not overwrite active command traffic.
