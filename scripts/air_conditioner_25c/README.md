# air_conditioner_25c

## Purpose

Keep one **Air Conditioner** enabled with its target output temperature set to **25C**.

This script is for an **IC10 chip installed in the Air Conditioner's own IC slot**.

The script continuously enforces:

- `Setting = TARGET_C + 273.15`
- `Mode = 1` / Active
- `On = 1`

## Devices

Required:

- Air Conditioner
- IC10 chip installed in the Air Conditioner

## Device registers

When this script runs inside the Air Conditioner's IC slot:

- `db` = Air Conditioner interface

You do **not** manually wire `db`; the Air Conditioner provides it automatically.

## Usage

1. Build and pipe the Air Conditioner normally, including a pressurized waste/coolant loop.
2. Insert an IC10 chip into the Air Conditioner's IC slot.
3. Paste `air_conditioner_25c.ic10` into that chip.
4. Run the script.

## Tuning

Edit the constant near the top of `air_conditioner_25c.ic10`:

- `TARGET_C` (Celsius): default `25`

## Air Conditioner setup notes

- Air Conditioner logic `Setting` is Kelvin. The script lets you tune in Celsius and writes Kelvin.
- 25C = 298.15K. Writing `25` makes the display show about `-248C`.
- Air Conditioner `TemperatureInput` is Kelvin. Example: `l r0 db TemperatureInput`.
- The imported catalog documents Air Conditioner `Mode` as:
  - `0` = Idle
  - `1` = Active
- The Air Conditioner still needs a valid pipe setup and coolant/waste loop. The IC script only keeps the control values set.

## Status

Functional.
