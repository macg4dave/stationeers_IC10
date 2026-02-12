# led_display_hms_clock

**Category:** Utility  
**Status:** Functional

## Purpose

Runs a simple 24-hour clock on LED Displays:

- `d0` = hours
- `d1` = minutes
- `d2` = optional (unused / separator display)

Time is derived from the **Daylight Sensor Horizontal angle** each loop.
No sleep/timer accumulation is used.
Each active display is rendered as a 2-digit field (e.g., `02`, `52`).

## Devices

Required:

- 2x LED Display (hours, minutes)
- 1x Daylight Sensor

## Device registers

Assign these in the IC housing UI:

- `d0` = LED Display for **hours**
- `d1` = LED Display for **minutes**
- `d2` = optional LED Display (unused / visual separator)
- `d3` = Daylight Sensor (**time source**)

## Tuning

Edit these constants in `led_display_hms_clock.ic10`:

- `SENSOR_PORT_DIRECTION` (default `0`) — Daylight Sensor rotation
  - `0`=North, `1`=East, `2`=South, `3`=West
- `CLOCK_DEG_OFFSET` (default `0`) — angle-to-time map offset
- `CLOCK_DEG_INVERT` (default `0`) — set to `1` if time runs backward
- `TIME_SHIFT_MIN` (default `0`) — fine calibration in minutes (can be negative)

## Notes

- Displays are forced to `On=1` with role-specific modes:
  - Hours display: `Mode=10` (string)
  - Minutes display: `Mode=10` (string)
- The script packs two ASCII digits into each active display `Setting` so leading zeros show.
- Separators (`:`) are not generated directly by the script.
  - Place displays side-by-side and use decorative separators/signage between them.
- Time source is in-game sensor data, so it tracks world day progression.
- If your displayed time is shifted, adjust in this order:
  1) `SENSOR_PORT_DIRECTION`
  2) `CLOCK_DEG_INVERT` (if direction is reversed)
  3) `CLOCK_DEG_OFFSET`
  4) `TIME_SHIFT_MIN`
