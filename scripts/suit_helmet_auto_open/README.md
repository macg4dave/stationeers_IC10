# suit_helmet_auto_open

Opens your **Hardsuit Helmet** in safe air and closes it the moment the air is not safe. If you close it yourself, it stays closed.

*Previously called `hardsuit_helmet_temp_pressure_open`.*

## Pins

| Pin | Device |
| --- | --- |
| `db` | Hardsuit (the chip goes in the suit) |
| `d0` | Hardsuit Helmet |

## What it does

- Safe = outside 4–45 °C **and** 80–150 kPa.
- Safe: opens the helmet once.
- If you close it after it opened, it stays closed until the air goes unsafe and safe again, or you open it yourself.
- Unsafe: closes immediately.
- Checks once a second.

## Settings

Edit the `define` lines at the top of `suit_helmet_auto_open.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `MIN_C` | `4` |  |
| `MAX_C` | `45` |  |
| `MIN_KPA` | `80` |  |
| `MAX_KPA` | `150` |  |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. Put an IC10 chip in the device's own IC slot.
3. Paste `suit_helmet_auto_open.ic10` into the chip and run it.

## Notes

- No status number: `db` is the suit.

## Change history

- 2026-11-21: remade and renamed. Rewritten to be shorter; only unlocks the helmet when it needs to move it. Behaviour unchanged.

## Status

Functional (author's label from before the remake; re-test in-game).
