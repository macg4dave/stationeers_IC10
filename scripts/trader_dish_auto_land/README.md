# trader_dish_auto_land

One chip that drives a **Satellite Dish** to find a trader, lock on, interrogate it and,
if the lever is on, call it down to your landing pad.

*Replaces the four-chip `SatTraderTrack` multi-chip system, which never worked in-game. That system was removed on 2026-11-21; it is still in git history.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Satellite Dish (Large recommended; Medium should work) |
| `d1` | (optional) Dial: trader type to accept, `0` = any |
| `d2` | (optional) Lever: auto-land on/off. Not connected = never call down |
| `d3` | (optional) LED Display: live SignalStrength (degrees to the contact) |

## What it does

1. **Scan.** The script points the dish across the sky, 30° steps around (Horizontal) and
   20° steps down from straight up (Vertical 0, 20, 40, 60, 80). It waits for the dish to
   stop moving, then reads `SignalStrength`. `-1` means nothing is in view.
2. **Lock.** A contact is in view. The script checks it against the dial
   (`ContactTypeId`) and locks the dish onto it with `BestContactFilter`. It then steps
   Horizontal/Vertical one direction at a time and keeps any move that makes
   `SignalStrength` smaller, halving the step when nothing helps. It stops when the dish is
   within 2°, or when the step is below 0.5°. Steps can go "over the top" (past straight up).
3. **Interrogate.** Power goes to `MAX_W`, then `Activate` 1 starts interrogation. Once a
   second it checks `InterrogationProgress`. If the contact drifts more than 6° away, it
   re-locks without restarting the interrogation. If the contact disappears, it scans
   again. After 600 s it gives up.
4. **Land.** When progress reaches 1 and the lever is on, `Activate` 1 again calls the
   trader down. The trader just handled is skipped from then on and scanning restarts.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `SCAN_W` | `5000` | Dish power while scanning. More power means contacts are visible from further away (fewer misses), but uses more power |
| `MAX_W` | `10000` | Dish power while interrogating. Large and exotic traders may need more |
| (inline) `30` / `20` | | Scan steps for Horizontal and Vertical (`add r0 r0 30`, `add r1 r1 20`) |
| (inline) `2` | | Lock accuracy in degrees (`ble r3 2 locked`) |
| (inline) `6` | | Drift that triggers a re-lock during interrogation |
| (inline) `600` | | Interrogation give-up time in seconds |

## Status (IC Housing `Setting`)

`phase × 100 + ContactTypeId`. For example, `203` means "locking onto a type-3 trader".

| Phase | Meaning |
| --- | --- |
| `1xx` | scanning |
| `2xx` | locking on |
| `3xx` | interrogating |
| `4xx` | interrogated, not called (lever off or not connected) |
| `5xx` | called down |
| `900` | dish missing |

To learn which dial value to use for each trader, watch the last two digits while a
trader is locked.

## Setup

1. Build the dish with power and data. Put the IC Housing on the same network.
2. Set `d0` to the dish. Optionally set `d1` to a Dial, `d2` to a Lever and `d3` to an LED Display.
3. Set up your landing pad as usual (see the trading guide in-game).
4. Paste `trader_dish_auto_land.ic10` into the chip and run it.

## What still needs an in-game check

This was designed from community write-ups of the current (2026) trading system and tested
against a simulated dish. These points are assumptions:

- **SignalStrength is degrees to the contact, smaller is better, `-1` when nothing is
  visible.** Older wiki text says "negative, larger is better", which is the pre-2026
  behaviour. If the LED shows negative numbers while a trader is in view, this assumption
  is wrong and the script needs changing. Please report what you see.
- **Vertical 0 is straight up, 90 is the horizon.**
- **`Activate` 1 after interrogation calls the trader down.** Two older community scripts do
  this. If nothing lands, use the comms computer's Land button and report it.
- **`ContactTypeId` values** for each trader type are unknown. The status number shows them.
- **Power.** `MAX_W` 10,000 W may not be enough for large or exotic traders. One write-up
  quotes up to 8,000 W for 600 s. Raise it if interrogation never progresses.

## Change history

- 2026-11-21: new single-chip design. It replaces the four-chip system, which treated
  SignalStrength as "negative, larger is better" and so steered away from contacts.

## Status

Experimental (new design, not yet run in-game).
