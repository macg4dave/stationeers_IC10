# vending_export_exact_count

Exports an exact number of one item from a **Vending Machine**, using a Stacker to count and a Sorter to send the right amount out and the rest back.

*Previously called `vending_machine_export`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Vending Machine |
| `d1` | Stacker |
| `d2` | Sorter |
| `d3` | Logic Memory: item hash |
| `d4` | Logic Memory: count |

## What it does

- Write the item's hash to d3, then the count to d4. The count resets to 0 when the job starts.
- Items leave through Sorter output 0; leftovers go back through output 1.
- If the vending machine stops delivering for 20 s (item ran out or was never there), the job is abandoned and any partial stack is returned.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `vending_export_exact_count.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `TIMEOUT_S` | `20` | Give up after this many seconds without a delivery |
| `SORTER_MODE_LOGIC` | `2` | Sorter Mode used |
| `STACKER_MODE_MANUAL` | `1` | Stacker Mode used |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | idle |
| `1` | exporting |
| `2` | last job gave up (item ran out) |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `vending_export_exact_count.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/sorter.md`

## Change history

- 2026-11-21: remade and renamed. Fixed a hang: asking for an item the machine did not have waited forever (and the request was already cleared). Added the timeout and status.

## Status

Functional (author's label from before the remake; re-test in-game).
