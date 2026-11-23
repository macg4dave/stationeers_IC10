# display_storm_countdown

An **LED Display** counts down to the next storm, read from a **Weather Station**, and
changes colour like the station's own light. Every **Flashing Light** on the network
turns on from `WARN_S` seconds (default 3 hours) before a storm until it ends.

## Pins

The IC Housing shows these names on its pins once the script is running.

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `weather` | Weather Station, built **outside** and **powered** |
| `d1` | `led` | LED Display |

**Network devices:** every Flashing Light (`StructureFlashingLight`, hash `-1535893860`) on
the IC Housing's data network. No names needed.

## What it shows

| Display | Colour | When |
| --- | --- | --- |
| `12:34` | green | no storm yet: minutes and seconds to the next weather event |
| `0:45` | yellow | a storm is coming (station `Mode` 1) |
| `STORM` | red | a storm is happening now (`Mode` 2) |
| `NONE` | green | no weather event is scheduled (`NextWeatherEventTime` 0) |
| `NO PWR` | grey | the station has no power: its logic output does not work then |

- Minutes have no leading zero and stop at `999`, so the text fits the display's six
  characters (`999:59`).
- The display is set to text mode (`Mode` 10), switched on and coloured by the script.
  Each value is written only when it changes.
- If a pin is not set, or `d0` is not a Weather Station, the status shows `9` and the
  display keeps its last text. The chip waits instead of halting.

## Flashing Lights

- **On** while a storm is happening, and while the next event is `WARN_S` seconds or
  less away (`NextWeatherEventTime` 1 to `WARN_S`). These are the same real-time seconds
  the display counts down.
- **Off** otherwise: when the storm ends the station's countdown jumps to the next
  event, so the lights go off. Also off when no event is scheduled.
- **Left as they are** while the station is unpowered (its readings do not work then).
- Written only when a light differs, so a light switched by hand is put back within a tick.

## Settings

Edit the `define` lines at the top of `display_storm_countdown.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `WARN_S` | `10800` | Seconds before a storm that the Flashing Lights turn on (3 h) |
| `GREEN` / `YELLOW` / `RED` / `GREY` | `2` / `5` / `4` / `1` | Display colours (wiki Data Network Colors: 0 Blue, 1 Gray, 2 Green, 3 Orange, 4 Red, 5 Yellow, 6 White, 7 Black, 8 Brown, 9 Khaki, 10 Pink, 11 Purple) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | no storm |
| `1` | storm coming |
| `2` | in a storm |
| `9` | a pin is not set, or `d0` is not a Weather Station |

## Setup

1. Build the Weather Station **outside**: indoors it never reports an event (wiki).
2. Connect the station, the LED Display, the IC Housing and power to one data network.
3. Set `d0` to the Weather Station and `d1` to the LED Display.
4. Paste `display_storm_countdown.ic10` into the chip and run it.

## Notes

- `Mode` (0 no storm, 1 storm incoming, 2 in storm), `NextWeatherEventTime` (seconds,
  0 = none scheduled) and `Power` come from the wiki
  (`catalog/devices/Weather_Station.json`). Text mode works in-game for
  `display_clock_from_sun`.
- Whether `NextWeatherEventTime` counts to the start of the storm or also to its end is
  not known: during a storm the display shows `STORM`, not a time.
- Flashing Light hash: `StructureFlashingLight` (`cargo run -- hash`), the same value as
  a community emulator and a working weather-alert script; the wiki page lists `On`
  and `Lock` but no hash.
- Device notes: `docs/usage/led_display.md`.

## Change history

- 2026-11-23: Flashing Lights on the network turn on `WARN_S` (3 h) before a storm and
  off when it ends (owner's request).
- 2026-11-23: new script (owner's request).

## Status

Functional (author's label). Simulated, not yet run in-game.
