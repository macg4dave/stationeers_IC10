# SatCom (multi-chip architecture)

This folder is a **modular Satellite Comms** stack split across multiple IC chips.

## Goal

Break one large dish program into smaller chips with clear responsibilities:

- `satcom_master.ic10` — orchestration and button handling
- `satcom_worker_discover.ic10` — sweep and collect unique contacts
- `satcom_worker_cycle.ic10` — tune dish to stored contacts in order

## Shared devices / contract

Use three **Logic Memory** devices as shared contact slots:

- slot0 (`d1`) stores first discovered `SignalID`
- slot1 (`d2`) stores second discovered `SignalID`
- slot2 (`d3`) stores third discovered `SignalID`

Use one additional **Logic Memory** as the cycle command slot:

- cmd slot carries a monotonically increasing command token (`Setting`)

All scripts expect those slots to expose a writable/readable `Setting`.

## Wiring plan

### Master chip (`satcom_master.ic10`)

- `d0` = Important Button (user input)
- `d1` = IC Housing running `satcom_worker_discover.ic10`
- `d2` = IC Housing running `satcom_worker_cycle.ic10`
- `d3` = Logic Memory cmd slot

### Discover worker status (`satcom_worker_discover.ic10`)

- `d0` = Large Satellite Dish
- `d1` = Logic Memory slot0
- `d2` = Logic Memory slot1
- `d3` = Logic Memory slot2

### Cycle worker status (`satcom_worker_cycle.ic10`)

- `d0` = Large Satellite Dish
- `d1` = Logic Memory slot0
- `d2` = Logic Memory slot1
- `d3` = Logic Memory slot2
- `d4` = Logic Memory cmd slot

## Control flow

1. Press button once: master enables **discover** worker, disables **cycle** worker.
2. Discover worker sweeps and fills up to 3 unique contacts in slots.
3. Press button again: master enables **cycle** worker, disables **discover** worker.
4. Each additional button press: master increments cmd slot token.
5. Cycle worker locks dish (`BestContactFilter`) to next non-zero slot in order.

## Status protocol (`db Setting`)

Each chip writes status to its **own** IC Housing `Setting`.

### Master (`satcom_master.ic10`)

- `0` = init / all workers off
- `1` = waiting for next button edge
- `10` = switched to discover mode
- `20` = switched to cycle mode (first cycle command)
- `21` = next-cycle command issued

### Discover worker (`satcom_worker_discover.ic10`)

- `100` = init complete / slots cleared
- `110` = sweeping for contacts
- `120` = new contact stored
- `130` = collection complete (3 contacts)

### Cycle worker (`satcom_worker_cycle.ic10`)

- `200` = idle (no new command token)
- `210` = processing new command token
- `220` = tuned to contact (`BestContactFilter` written)
- `221` = no non-zero contacts available to tune

## Notes

- This is a clean baseline architecture designed for iterative expansion.
- Keep each chip under IC paste limits (128 lines / 90 chars per line).
