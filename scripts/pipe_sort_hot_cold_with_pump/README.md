# pipe_sort_hot_cold_with_pump

Sends gas down a **hot** or **cold** pipe depending on its temperature, while a **Pipe Volume Pump** holds the line near 10 MPa.

*Previously called `pipe_temp_hot_cold_valves`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Pipe Digital Valve (hot path) |
| `d2` | Pipe Digital Valve (cold path) |
| `d3` | Pipe Volume Pump |

## What it does

- Cold valve: open below 20 °C, close above 24 °C.
- Hot valve: open above 40 °C, close below 36 °C.
- Never both open at once.
- Pump ON below 9.75 MPa, OFF above 10.25 MPa; pump `Setting` kept at 1 L.
- Analyzer `Error`: pump OFF, valves hold, status 9.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_sort_hot_cold_with_pump.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `COLD_OPEN_BELOW_C` | `20` |  |
| `COLD_CLOSE_ABOVE_C` | `24` |  |
| `HOT_OPEN_ABOVE_C` | `40` |  |
| `HOT_CLOSE_BELOW_C` | `36` |  |
| `TARGET_KPA` | `10000` | Pressure target (kPa) |
| `BAND_KPA` | `250` | ± band around the target (kPa) |
| `PUMP_SETTING_L` | `1` | Pump volume setting (L) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0..7` | cold valve + 2 × hot valve + 4 × pump (e.g. 5 = cold open, pump on) |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_sort_hot_cold_with_pump.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Pump stops on analyzer error; pins checked in the loop; status on the housing.
- 2026-11: fixed the pump never stopping above 2 MPa (an old "Pa → kPa" guess divided readings above 2,000 kPa by 1000).

## Status

Functional (author's label from before the remake; re-test in-game).
