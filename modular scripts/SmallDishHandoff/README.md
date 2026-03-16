# SmallDishHandoff (modular)

Cheap two-chip satellite handoff:

- a **Scanning Medium Satellite Dish** fast-scans for a ship
- a shared **Logic Memory** carries one queued handoff token
- a **Contact Medium Satellite Dish** consumes that handoff and performs the real track / activate step

Player setup guide: `modular scripts/SmallDishHandoff/Setup.md`.

## Architecture

- `small_dish_handoff_worker_scanning.ic10` - fast coarse scan on the scanning medium dish and publish a handoff token when it has a target locked
- `small_dish_handoff_worker_contact.ic10` - consume the token, read the exact `SignalID` from the scanning dish, lock the contact dish, set a landing pad, and pulse `Activate`

## Device mapping per chip

### Scanning worker

- `d0` = Scanning Medium Satellite Dish
- `d1` = shared Logic Memory handoff slot
- `db` = scanning worker status

### Contact worker

- `d0` = Contact Medium Satellite Dish
- `d1` = shared Logic Memory handoff slot
- `d2` = Scanning Medium Satellite Dish (aim / SignalID source)
- `db` = contact worker status

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `scanning_worker`
- IC Housing: `contact_worker`
- Logic Memory: `handoff_slot`

## Shared memory contract

The shared Logic Memory `Setting` uses this single-slot protocol:

- `0` = slot empty / ready for a new handoff
- `-1` = slot busy; medium dish has claimed the current target
- any positive integer = handoff token published by the small dish worker

Flow:

1. scanning worker scans until it sees a valid contact and locks it locally
2. if the slot is `0`, it publishes a small integer token
3. contact worker sees that token, reads the exact `SignalID` directly from the scanning dish on `d2`, marks the slot as `-1`, and starts tracking
4. contact worker sets `TargetPadIndex` to `PAD_INDEX` before activation so the contacted ship can be called to that landing pad
5. when the contact dish loses or finishes with the target, it clears the slot back to `0`

## Status protocol (`db Setting`)

### Scanning worker (`100-199`)

- `100` = sweeping
- `110` = published a new handoff target
- `120` = holding current contact / queue not empty
- `190` = scanning dish reports `Error = 1`

### Contact worker (`200-299`)

- `200` = idle; no queued target
- `210` = target claimed / filter being applied
- `220` = waiting for lock or watts gate
- `221` = filtered search sweep in progress
- `230` = `Activate` pulse sent
- `240` = target cleared / handoff slot reopened
- `290` = medium dish reports `Error = 1`

## Limits / notes

- This feature uses only **2 IC Housings + 1 Logic Memory + 2 dishes**.
- Both workers use local pin wiring only; there is no name-based dish lookup.
- The scanning worker uses a coarse scan (`30°` horizontal, `15°` vertical rows) to stay fast and cheap.
- The contact worker keeps the handoff slot busy while it owns a target, so the scanning worker will not overwrite the queue mid-track.
- The handoff slot no longer stores `SignalID` directly; this avoids float precision loss in Logic Memory.
- The contact worker copies the scanning dish's current `Horizontal` / `Vertical` when it claims a target.
- After claiming a target, the contact worker performs its own filtered coarse sweep until it actually sees that handed-off `SignalID`.
- The contact worker writes `TargetPadIndex = PAD_INDEX` (default `0`) so a contacted ship is requested to land on that pad.
- If the contact dish never reaches the target watts requirement, it will keep waiting at status `220`.

## Tuning

In `small_dish_handoff_worker_contact.ic10`:

- `PAD_INDEX` — landing pad index to request for call-down (default `0`)
- `WATTS` — medium dish power setting (default `99999`)
- `SWH` / `SWV` — coarse filtered search spacing after target handoff

## Recovery steps

- If either worker shows `190` or `290`, fix the dish's in-game error state first.
- If the contact worker stays at `200`, check that the scanning worker can see contacts and that `handoff_slot` is wired to `d1` on both chips.
- If the contact worker stays at `221`, verify `d2` on the contact worker is wired to the same scanning dish.
- If the contact worker stays at `220`, increase contact dish watts or wait for better alignment.
- If the handoff slot gets stuck at `-1`, reset the Logic Memory `Setting` to `0` and let both workers reacquire.

## Migration note

The old filenames (`small_dish_handoff_worker_small.ic10` and
`small_dish_handoff_worker_medium.ic10`) are left in the folder for now.
Use the new `scanning` / `contact` files going forward.
