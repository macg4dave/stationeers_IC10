# large_satellite_dish_led_readout

**Status:** Functional  
**Category:** Utility

## Purpose

Read a **Large Satellite Dish** and display these outputs on LED Displays:

- `Horizontal`
- `Vertical`
- `SizeX`
- `SizeZ`

## Devices

Required:

- 1x **Large Satellite Dish**
- 4x **LED Display**
- 1x **IC10** in an IC Housing

## Device registers

- `d0` = Large Satellite Dish
- `d1` = LED Display (Horizontal)
- `d2` = LED Display (Vertical)
- `d3` = LED Display (SizeX)
- `d4` = LED Display (SizeZ)

## Usage

1. Wire the dish and all 4 LED Displays to the same data network as the IC housing.
2. Assign screws exactly as listed above (`d0..d4`).
3. Paste `large_satellite_dish_led_readout.ic10` into the IC.
4. Run the chip.

The script continuously mirrors dish values to the displays.

## Notes / gotchas

- The script sets all displays to `Mode=0` (number) on startup.
- If a display is manually changed in-game, restart the IC to re-apply mode.
- Dish values are read directly; if the dish is unpowered or in error state, outputs may be stale or not meaningful.
