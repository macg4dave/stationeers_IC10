# Satellite Dish setup checklist (small / medium / large)

Script: `scripts/trader_dish_auto_land/`.

## Signal model (current game, 2026, from community write-ups; not yet confirmed here)

- `SignalStrength` = angle in **degrees** between where the dish points and the
  contact. **Smaller is closer**; about 2° counts as locked. `-1` = nothing visible.
  Older wiki text ("negative value, larger is better") describes the pre-2026 behaviour.
- A contact is visible only while `WattsReachingContact` ≥ its minimum, so more dish
  power (`Setting`, watts) means contacts are visible from further off-axis.
- `Vertical` 0 = straight up, 90 = horizon. Horizontal steps matter less near straight up.

## What scripts read

- `Idle` (1 = not moving: wait for it before trusting signal outputs)
- `SignalStrength`, `SignalID`, `ContactTypeId`
- `InterrogationProgress` (0..1), `Activate` (1 while interrogating)
- `MinimumWattsToContact`, `WattsReachingContact` (`-1` = no data)

## What scripts write

- `Horizontal`, `Vertical`, `Setting` (watts)
- `BestContactFilter` = a `SignalID` to track only that contact, `-1` to release
- `Activate` 1: start interrogation; after `InterrogationProgress` = 1, call the trader down
  (community scripts; confirm in-game)
- `TargetPadIndex`: landing pad for the call-down (mapping to pads is unclear)

## Gotchas

- While the dish moves (`Idle = 0`), signal outputs are meaningless.
- Pressing `Activate` while interrogating stops the interrogation. Read `Activate` first.
- If `Error = 1`, fix the in-game error first.
