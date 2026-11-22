# power_apc_on_high_battery

Switches an **Area Power Control** on while the station batteries are charged (over
70 %), and off again when they run down (below 60 %). Use it to power non-essential
loads only when there is energy to spare.

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Area Power Control |

Batteries are not pins. Every battery of these types on the IC Housing's data network
is read:

| Battery | Prefab | Hash |
| --- | --- | --- |
| Station Battery | `StructureBattery` | `-400115994` |
| Station Battery (Large) | `StructureBatteryLarge` | `-1388288459` |

`StructureBatteryLarge` is the hash `power_generator_on_low_battery` already uses.
`StructureBattery` follows the same naming but is not confirmed in-game. If small
batteries are ignored, read their real hash (see [Setup](#setup)) and replace `BAT`.

## What it does

- Adds up the `Charge` and `Maximum` of every battery and works out the total charge.
  A large battery counts for its real size, not as one vote.
- Total over 70 %: APC ON.
- Total below 60 %: APC OFF.
- Between 60 % and 70 %: holds, so the APC does not flicker at the threshold.
- No batteries found: APC OFF, status 2.
- Writes `On` only when it changes. The APC pin is checked every loop: unplug it and
  the chip waits instead of halting.
- At start-up it keeps the APC as it is until the charge leaves the 60–70 % band.

## Settings

Edit the `define` lines at the top of `power_apc_on_high_battery.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `ON_ABOVE` | `0.70` | APC on above this total charge (0..1) |
| `OFF_BELOW` | `0.60` | APC off below this total charge (0..1) |
| `BAT`, `BAT_LARGE` | see above | Battery prefab hashes |

Keep `OFF_BELOW` under `ON_ABOVE`. Setting them equal removes the band and the APC
can switch every tick.

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | APC off |
| `1` | APC on |
| `2` | no batteries found (APC off) |
| `9` | Area Power Control missing on `d0` |

## Setup

1. Connect the batteries, the Area Power Control and the IC Housing to one data
   network.
2. Set `d0` to the Area Power Control.
3. Paste `power_apc_on_high_battery.ic10` into the chip and run it.

To read a battery's real hash, put it on `d0` of a spare chip and run
`l r0 d0 PrefabHash` then `s db Setting r0`. The housing shows the number.

## Notes

- The APC's own internal battery is not counted: only Station Batteries are read.
- The chip itself needs power. If it runs from the circuit the APC switches, it turns
  itself off with the APC. Power the IC Housing from the battery side.
- Related: `power_generator_on_low_battery` starts a generator below 30 %.

## Change history

- 2026-11-22: new script.

## Status

Functional. Simulated, not run in-game.
