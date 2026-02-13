# SatCom control system (modular)

Name-first SatCom automation for a Large Satellite Dish using a master + workers.
All active scripts now use exact prefab+name lookup (`lbn`/`sbn`).

Player setup guide: `modular scripts/SatCom/Setup.md`.

## Architecture

- `satcom_master.ic10` - button edge routing and command publication
- `satcom_setup_guard.ic10` - name/type validation + worker/channel init helper
- `satcom_worker_discover.ic10` - discover and refresh contact slots
- `satcom_worker_cycle.ic10` - cycle/tune contacts and clear active filter
- `satcom_worker_display.ic10` - optional H/V LED display updater

`satcom_master_named.ic10` is deprecated and intentionally not used.

## Name contract

Required exact names:

- Buttons: `discover`, `cycle`
- IC Housing: `discover_worker`, `cycle_worker`
- Logic Memory: `cmd_token`, `cmd_type`, `slot0`, `slot1`, `slot2`
- Large Satellite Dish: `dish`
- Optional LED Displays: `display_h`, `display_v`

Implementation notes:

- Workers and channels are targeted by prefab+name, not chip pin mapping.
- Master/setup guard read IC Housing prefab from `db PrefabHash`, so use one
  housing variant across SatCom ICs.
- Display worker resolves small/medium/large LED display prefabs.

## Shared memory contract

Use Logic Memory `Setting` channels:

- `slot0` - first discovered `SignalID`
- `slot1` - second discovered `SignalID`
- `slot2` - third discovered `SignalID`
- `cmd_token` - incrementing command token
- `cmd_type` - command code

Command codes:

- `1` = discover (rebuild contact slots)
- `2` = cycle (tune next non-zero contact)
- `3` = clear (clear slots and unlock dish filter)

Workers execute commands only when `cmd_token` changes.

## Wiring

- Put all SatCom devices on one shared data network.
- Button prefab can be either Logic Switch (Button) or Important Button.
- No manual `d0..d5` mapping is required for active SatCom scripts.

## Controls

- Press `discover` to issue command `1`.
- Press `cycle` to issue command `2`.
- Press both together to issue command `3`.

## Status protocol (`db Setting`)

Each chip writes status to its own housing `Setting`.

### Master status (`0-99`)

- `0` = init
- `1` = idle/ready
- `2` = discover worker busy
- `3` = cycle worker busy
- `4` = cycle ready/tuned
- `5` = contacts available
- `6` = no contacts found
- `10` = discover command sent
- `20` = cycle command sent
- `30` = clear command sent

### Setup guard status (`90-99`)

- `1` = setup valid
- `91` = missing/wrong `cmd_token`
- `92` = missing/wrong `cmd_type`
- `93` = missing/wrong `discover_worker` housing
- `94` = discover button wrong type/name
- `95` = cycle button wrong type/name
- `96` = missing/wrong `cycle_worker` housing

### Discover worker status (`100-199`)

- `100` = idle
- `110` = discover start/reset
- `120` = sweeping step
- `121` = contact stored
- `130` = complete with 3 contacts
- `131` = complete with zero contacts
- `132` = complete with partial contacts
- `140` = cleared by clear command

### Cycle worker status (`200-299`)

- `200` = idle
- `210` = cycling contacts
- `220` = tuned (`BestContactFilter` written)
- `221` = no valid contacts to tune
- `230` = filter cleared by clear command

### Display worker status (`300-399`)

- `300` = init
- `310` = updating H/V displays

## Limits

- Every `.ic10` stays within 128 lines and 90 chars per line.
- Validate with:
  - `python tools/ic10_size_check.py "modular scripts/SatCom" --ext .ic10`
  - `python tools/setup_contract_check.py`
