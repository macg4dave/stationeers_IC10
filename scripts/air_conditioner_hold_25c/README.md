# air_conditioner_hold_25c

Keeps one **Air Conditioner** switched on and set to a 25 °C target.

*Previously called `air_conditioner_25c`.*

## Pins

| Pin | Device |
| --- | --- |
| `db` | The Air Conditioner itself (the chip goes in the AC's own IC slot) |

## What it does

- Writes `Setting` = 25 °C (in Kelvin), `Mode` = 1 (Active) and `On` = 1, only when they differ.

## Settings

Edit the `define` lines at the top of `air_conditioner_hold_25c.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `TARGET_C` | `25` | Target temperature (°C) |
| `MODE_ACTIVE` | `1` | Mode value written to the AC |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. Put an IC10 chip in the device's own IC slot.
3. Paste `air_conditioner_hold_25c.ic10` into the chip and run it.

## Notes

- No status number: `db` is the AC, so writing a status would overwrite its target.
- The catalog lists AC Mode 0 = Idle, 1 = Active. If the AC reports Mode itself, the Mode write is harmless but unnecessary.

## Change history

- 2026-11-21: remade and renamed. Tidied: the target is computed once; the loop is shorter. Behaviour unchanged.

## Status

Functional (author's label from before the remake; re-test in-game).
