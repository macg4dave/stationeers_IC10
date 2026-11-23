# pipe_sort_hot_cold_with_pump

Sends gas down a **hot** or **cold** pipe depending on its temperature, while an optional **Pipe Volume Pump** holds the line near 10 MPa and any **Pipe Heaters** warm cold gas.

*Previously called `pipe_temp_hot_cold_valves`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Pipe Digital Valve (hot path) |
| `d2` | Pipe Digital Valve (cold path) |
| `d3` | Pipe Volume Pump (optional) |

Pipe Heaters are not pins: every Pipe Heater (`StructurePipeHeater`, `-419758574`) on
the data network is switched together, by type.

## What it does

- Cold valve: open below 18 °C, close above 20 °C.
- Hot valve: open above 40 °C, close below 36 °C.
- Never both open at once.
- Pump ON below 9.75 MPa, OFF above 10.25 MPa; pump `Setting` kept at 1 L.
- **Pipe Heaters:** ON while the cold valve is open, OFF otherwise. Without heaters on
  the network, nothing changes.
- Analyzer `Error`: pump and heaters OFF, valves hold, status 9.
- **No pump:** leave `d3` empty and the chip runs the valves only. The pump bit of the
  status stays 0. Unplug the pump while running and the valves keep working.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_sort_hot_cold_with_pump.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `COLD_OPEN_BELOW_C` | `18` | Cold valve and heaters on below (°C) |
| `COLD_CLOSE_ABOVE_C` | `20` | Cold valve and heaters off above (°C) |
| `HOT_OPEN_ABOVE_C` | `40` |  |
| `HOT_CLOSE_BELOW_C` | `36` |  |
| `TARGET_KPA` | `10000` | Pressure target (kPa) |
| `BAND_KPA` | `250` | ± band around the target (kPa) |
| `PUMP_SETTING_L` | `1` | Pump volume setting (L) |
| `HEATER` | `-419758574` | Pipe Heater prefab hash |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0..7` | cold valve + 2 × hot valve + 4 × pump (e.g. 5 = cold open, pump on). Heaters follow the cold bit |
| `9` | analyzer error, or the analyzer or a valve is missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. Optional: add Pipe Heaters on the cold pipe and connect them to the same data network.
3. In the IC Housing screen, set each pin as listed above. Leave `d3` empty if you have no pump.
4. Paste `pipe_sort_hot_cold_with_pump.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_digital_valve.md`,
  `docs/usage/pipe_heater.md`
- Heaters run whenever the cold valve is open, even if no gas is flowing. They are off
  on an analyzer error, so a broken reading cannot overheat the pipe.

## Change history

- 2026-11-23: cold side now closes above 20 °C and reopens below 18 °C (was 24 / 20).
  In-game, the cold valve and pipe heaters stayed on above 20 °C: the old band held
  them open until 24 °C, which the heaters did not reach (owner's request).

- 2026-11-21: Pipe Heaters on the network now turn on while the cold valve is open.
  Alias `pipe` renamed `analyzer`. Pins unchanged (`d1` hot, `d2` cold).
- 2026-11-21: the pump on `d3` is optional. Without it the chip ran nothing (it waited
  for `d3`); now the valves run alone and the pump bit of the status reads 0.
- 2026-11-21: remade and renamed. Pump stops on analyzer error; pins checked in the loop; status on the housing.
- 2026-11: fixed the pump never stopping above 2 MPa (an old "Pa → kPa" guess divided readings above 2,000 kPa by 1000).

## Status

Functional (author's label from before the remake; re-test in-game).
