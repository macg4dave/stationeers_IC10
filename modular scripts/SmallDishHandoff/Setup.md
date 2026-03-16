# SmallDishHandoff setup

Use this page to set up a cheap **Medium -> Medium Satellite Dish** handoff pair.

## Build list

- 2x IC Housing + IC Chip
  - SmallDishHandoff Scanning Worker
  - SmallDishHandoff Contact Worker
- 1x Logic Memory
  - `handoff_slot`
- 2x Medium Satellite Dish

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `scanning_worker`
- IC Housing: `contact_worker`
- IC Housing: `small_scan_worker` (legacy filename compatibility)
- IC Housing: `medium_track_worker` (legacy filename compatibility)
- Logic Memory: `handoff_slot`

## Wiring map

### small_dish_handoff_worker_scanning.ic10

- `d0` -> Scanning Medium Satellite Dish
- `d1` -> Logic Memory `handoff_slot`

### small_dish_handoff_worker_contact.ic10

- `d0` -> Contact Medium Satellite Dish
- `d1` -> Logic Memory `handoff_slot`
- `d2` -> Scanning Medium Satellite Dish

## Setup steps

- Put both chips, the Logic Memory, and both dishes on one shared data network.
- Paste scripts:
  - `modular scripts/SmallDishHandoff/small_dish_handoff_worker_scanning.ic10`
  - `modular scripts/SmallDishHandoff/small_dish_handoff_worker_contact.ic10`
  - `modular scripts/SmallDishHandoff/small_dish_handoff_worker_small.ic10` (legacy filename; use `scanning` for new setups)
  - `modular scripts/SmallDishHandoff/small_dish_handoff_worker_medium.ic10` (legacy filename; use `contact` for new setups)
- Apply required names from **Name contract**.
- Wire both chips exactly as shown in **Wiring map**.
- Power the network and let the small dish start sweeping.
- Watch `handoff_slot` move through `0 -> token -> -1` when a target is handed off.

## Controls

There are no buttons or dials in normal use.

The system is automatic:

- the scanning worker finds a contact and publishes a handoff token
- the contact worker claims that handoff, reads the exact `SignalID` from the scanning dish on `d2`, sets its `TargetPadIndex`, and drives the contact dish toward it
- when the target clears, the handoff slot reopens for another scan

Landing behavior:

- the contact worker uses `PAD_INDEX` inside `small_dish_handoff_worker_contact.ic10`
- default is `0`; change that define if your landing pad setup uses a different index

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `scanning_worker` (`db Setting`)
- `contact_worker` (`db Setting`)
- `handoff_slot` (`Setting`)

Quick interpretation:

- `handoff_slot = 0` means ready for a new handoff
- `handoff_slot = -1` means the contact worker owns a target right now
- any positive value in `handoff_slot` is just a handoff token, not the actual `SignalID`
- `scanning_worker = 110` proves the scanning dish published a target
- `contact_worker = 221` means the contact dish is sweeping for the handed-off target; re-check `d2` if it never leaves this state
- `contact_worker = 220` means the contact dish sees the target but is still waiting for lock or enough watts

## Migration note

The old `small` / `medium` filenames are still present in the folder for now.
Use the new `scanning` / `contact` files going forward.
