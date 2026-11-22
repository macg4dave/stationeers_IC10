# Solar panels (batch control) setup checklist

Script: `scripts/solar_panels_track_sun/` (one Daylight Sensor, panels named by direction).

## Which panels move

Prefab data (ic10emu's game data, 2024) lists eight solar prefabs, and all of them
accept `Horizontal`/`Vertical` writes. Only these rotate, though:

- Solar Panel `StructureSolarPanel` (-2045627372)
- Solar Panel (Heavy) `StructureSolarPanelReinforced` (-934345724)
- Solar Panel (Dual) `StructureSolarPanelDual` (-539224550)
- Solar Panel (Heavy Dual) `StructureSolarPanelDualReinforced` (-1545574413)
- 1x5 panels: newer than that data, both confirmed in-game (2026-11-21):
  - Solar Panel 1x5 `StructureSolarPanel1x5` (939649277)
  - Solar Panel 1x5 (Heavy), prefab name unknown (-2049226859, `PrefabHash` read
    in-game; `StructureSolarPanel1x5Reinforced` is wrong)

  Both are built flipped (confirmed in-game): their data port sits opposite a normal
  panel's, so `Horizontal` needs an extra 180°.

Angled (`StructureSolarPanel45*`) and Flat (`StructureSolarPanelFlat*`) panels are
built in a fixed pose.

## What scripts write

- `Horizontal`: a local angle, clockwise, with the data port at 270°. A world heading
  W becomes `W + 270 - <world direction of the data port>`.
- `Vertical`: degrees above the horizon, 15–165, 90 = straight up. Values below 90
  tilt toward `Horizontal`.

## Minimum to work

- Panels connected to the same data network as the IC Housing.
- Panel names exactly as the script expects. Name hashes are exact: no substrings,
  case-sensitive.

## Common gotchas

- Batch writes only reach devices on the data network.
- One panel type pointing wrong while the others are right means its data port sits
  elsewhere on that panel. Rename it to the next direction group.
