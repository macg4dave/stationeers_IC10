# vending_machine_export

## Purpose

Exports an exact quantity of one item from a **Vending Machine** by using a **Stacker**
and **Sorter** as a small item-routing chain.

This is based on the Stationeers wiki guide, with two practical updates for current
behavior:

- the **Sorter** is configured to **Mode 2 (Logic)** so IC10 `Output` writes control
  each routed stack reliably
- the script does **not** rely on a Vending Machine `ClearMemory` parameter, because
  the current local catalog does not document that field for this device

## Devices

Required:

- 1× Vending Machine
- 1× Stacker
- 1× Sorter
- 2× Logic Memory

## Device registers

- `d0` = Vending Machine
- `d1` = Stacker
- `d2` = Sorter
- `d3` = Logic Memory holding requested item hash
- `d4` = Logic Memory holding requested quantity

## Setup

1. Connect the **Vending Machine** export to the **Stacker** import with chutes.
2. Connect the **Stacker** export to the **Sorter** import.
3. Connect the Sorter **export lane for `Output = 0`** to your destination.
4. Connect the Sorter **export lane for `Output = 1`** back to the Vending Machine
   import so leftover items return to storage.
5. Wire all devices and both Logic Memories to the same data network as the IC.
6. Paste `vending_machine_export.ic10` into the chip.

### Sorter lane orientation

Per the current Sorter docs: when you face the Sorter outputs with the power switch
on your right:

- `Output = 0` exits **right**
- `Output = 1` exits **left**

If you physically build it the other way around, swap the chute connections.

## Usage

1. Write the target item hash into `d3` Logic Memory `Setting`.
2. Write the desired quantity into `d4` Logic Memory `Setting`.
3. The script accepts the request by resetting the quantity memory to `0`.
4. Requested items go to the main export lane; leftovers in the Stacker are sent back
   to the Vending Machine.

### Request protocol

- `d3` = item hash request channel
- `d4` = quantity request channel
- `d4 == 0` means idle or request accepted
- `d4 > 0` means a pending request still has not been accepted

Tip: write the hash first, then the quantity second.

## Notes

- The **Vending Machine stores up to 100 individual stacks** and does **not** merge
  them internally. Lots of tiny partial stacks will fill it quickly.
- If the Vending Machine does **not** contain enough of the requested item, this script
  waits for more stock instead of failing fast.
- A restock chute/inlet back into the Vending Machine is handy so you can refill it
  without rebuilding the export chain.
- See `docs/usage/sorter.md` for the important Sorter mode/orientation details.

## Status

Functional
