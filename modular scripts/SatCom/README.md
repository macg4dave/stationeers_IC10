# SatCom control system (modular)

This is a full modular system for controlling a Large Satellite Dish and its
discovered contacts.

Player setup guide: `docs/usage/satcom.md`.

## Architecture

- `satcom_master.ic10` - command router (buttons -> command bus)
- `satcom_worker_discover.ic10` - discover and refresh contact slots
- `satcom_worker_cycle.ic10` - cycle/tune contacts and clear active filter

The system uses a shared command bus and three shared contact slots.

## Shared memory contract

Use Logic Memory devices for all channels (`Setting`).

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

Wiring note for new modular projects: prefer chip-link/channel mapping starting
at `d0` and descending before buttons and feature devices. See
`docs/usage/modular_wiring_setup.md`.

### Master (`satcom_master.ic10`)

- `d0` = Discover worker IC housing
- `d1` = Cycle worker IC housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = Important Button (Discover/Refresh)
- `d5` = Important Button (Cycle Next)

### Discover worker (`satcom_worker_discover.ic10`)

- `d0` = Logic Memory `slot0`
- `d1` = Logic Memory `slot1`
- `d2` = Logic Memory `slot2`
- `d3` = Logic Memory `cmd_token`
- `d4` = Logic Memory `cmd_type`
- `d5` = Large Satellite Dish

### Cycle worker (`satcom_worker_cycle.ic10`)

- `d0` = Logic Memory `slot0`
- `d1` = Logic Memory `slot1`
- `d2` = Logic Memory `slot2`
- `d3` = Logic Memory `cmd_token`
- `d4` = Logic Memory `cmd_type`
- `d5` = Large Satellite Dish

## Controls

- Press Discover button (`d4`) to issue command `1` (discover/refresh).
- Press Cycle button (`d5`) to issue command `2` (next contact).
- Press both buttons together to issue command `3` (clear all contacts + unlock
  `BestContactFilter`).

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

## Setup flow

1. Paste each script into its assigned IC.
2. Wire `cmd_token` and `cmd_type` memory slots to master + both workers.
3. Wire `slot0..slot2` memory slots to discover + cycle workers.
4. Press Discover (`d4`) to build contact list.
5. Press Cycle (`d5`) to tune through discovered contacts.

## Limits

- Every `.ic10` stays within 128 lines and 90 chars per line.
- Validate with:
  - `python tools/ic10_size_check.py "modular scripts/SatCom" --ext .ic10`
