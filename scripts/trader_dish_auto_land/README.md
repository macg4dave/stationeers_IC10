# trader_dish_auto_land

One chip that drives a **Satellite Dish** to find a trader, lock on, interrogate it and
call it down to your landing pad. Switch the lever on to stop the call-down.

*Replaces the four-chip `SatTraderTrack` multi-chip system, which never worked in-game. That system was removed on 2026-11-21; it is still in git history.*

## Pins

The IC Housing shows these names on its pins once the script is running.

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `dish` | Satellite Dish (Large recommended; Medium should work) |
| `d1` | `dial` | (optional) Dial: trader type to accept (its `Setting`), `0` = any. See "Dial" below |
| `d2` | `lever` | (optional) Lever: on (`Open` 1) = interrogate only, do not call down. Off or not connected = call down |
| `d3` | `led` | (optional) LED Display: last SignalStrength read (degrees to the contact, `-1` = none) |

## What it does

1. **Scan.** The script points the dish across the sky: a full turn in 30° Horizontal
   steps, then the next Vertical row, 20° further down from straight up (rows 0, 20, 40,
   60, 80, then back to 0). That is 60 positions. At each one it waits for the dish's
   `Idle`, waits 1 s more, then reads `SignalStrength`. `-1` means nothing is in view.
2. **Lock.** A contact is in view and it is not the last trader handled (`SignalID`). If
   the dial is non-zero, `ContactTypeId` must match it. The script locks the dish onto it
   with `BestContactFilter`. It then steps Horizontal/Vertical one direction at a time and
   keeps any move that makes `SignalStrength` smaller. The first step is half the
   starting signal, and the step halves whenever no direction helps. Horizontal steps are
   made larger near straight up (up to 5×), where a degree of Horizontal moves the dish
   very little. It stops when the dish is within 2°, or when the step is below 0.5°.
   Steps can go "over the top" (past straight up). Vertical never goes below 90 (the horizon).
3. **Interrogate.** Power goes to `MAX_W`. If the dish's `Activate` reads 0, the script
   writes `Activate` 1 to start interrogation and starts the give-up timer. About every
   1.5 s it checks `InterrogationProgress`. If the contact drifts more than 6° away, it
   re-locks (status `2xx`) without restarting the interrogation. If the contact
   disappears, it goes back to scanning. After 600 checks (about 15 minutes, not counting
   re-locks) it gives up.
4. **Land.** When progress reaches 1, `Activate` 1 again calls the trader down, unless
   the lever is on. The result stays on the status for 5 s. Then scanning resumes from where
   the dish is pointing, with power back at `SCAN_W`.

The script remembers **one** trader: the last one it finished with (called, not called
or timed out). It skips that trader until it finishes with a different one.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `SCAN_W` | `5000` | Dish power while scanning. More power means contacts are visible from further away (fewer misses), but uses more power |
| `MAX_W` | `10000` | Dish power while interrogating. Large and exotic traders may need more |
| (inline) `30` / `20` | | Scan steps for Horizontal and Vertical (`add r0 r0 30`, `add r1 r1 20`) |
| (inline) `2` | | Lock accuracy in degrees (`ble r3 2 locked`) |
| (inline) `0.5` | | Smallest lock step in degrees (`blt r4 0.5 locked`) |
| (inline) `6` | | Drift that triggers a re-lock during interrogation (`bgt r2 6 lock`) |
| (inline) `600` | | Interrogation give-up, in checks of about 1.5 s each (`move r13 600`) |
| (inline) `5` | | Seconds the result stays on the status before scanning again (`sleep 5`) |

## Status (IC Housing `Setting`)

`phase × 100 + ContactTypeId`. For example, `203` means "locking onto a type-3 trader".

| Phase | Meaning |
| --- | --- |
| `1xx` | scanning |
| `2xx` | locking on (also re-locking during interrogation) |
| `3xx` | interrogating. Still `3xx` for 5 s after the give-up timer runs out |
| `4xx` | interrogated, not called (lever on) |
| `5xx` | called down |
| `900` | dish missing |

The last two digits are `0` while nothing is in view.

## Dial

- A Logic Dial's `Mode` is its number of steps and defaults to **1**, so out of the box
  the knob only goes 0 ↔ 1. Use a screwdriver on the dial to raise `Mode` before you
  turn the knob to higher values.
- To learn which dial value to use for each trader, leave the dial at `0` and watch
  the last two digits of the status while a trader is locked.
- If those digits stay `00` for every trader, `ContactTypeId` is reading `0` or `-1`.
  Any non-zero dial value then rejects every ship, so keep the dial at `0` (or
  disconnect it) until we know what the game reports.

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
- **`Activate` going back to 0.** The script assumes `Activate` reads 0 when the dish is
  not interrogating. If it stays 1 (for example after a call-down), the script will not
  press it again and the give-up timer is not reset. Watch it on a Logic Reader. If the
  status goes from `3xx` back to `1xx` after about a second, this is the cause.
- **`InterrogationProgress` runs 0 to 1.** The catalog (from the wiki) calls it a
  percentage. If it runs 0 to 100, the script treats 1% as finished and calls down too
  early. If the status jumps from `3xx` to `5xx` within seconds, this is the cause.
- **First in-game run (2026-11-22):** contacts are found, but the status stays at `200`
  (locking on, `ContactTypeId` 0). Interrogation has not been reached yet. The cause is
  not known yet: the dish may never report `Idle`, `SignalStrength` may not behave as
  degrees, or locking on may just be slow.

## Change history

- 2026-11-21: new single-chip design. It replaces the four-chip system, which treated
  SignalStrength as "negative, larger is better" and so steered away from contacts.
- 2026-11-22: README only, now matches the script: scan order, lock step sizes, the
  ~15 min give-up time, which trader is skipped, and the status after a timeout.
  Script unchanged.
- 2026-11-22: pins are now named with `alias` (`dish`, `dial`, `lever`, `led`) so the IC
  Housing labels them. Pin numbers are unchanged. To stay within 128 lines, two header
  comments were merged and an `add r0 r0 360` before `mod r0 r0 360` was dropped (IC10
  `mod` already returns a positive result).
- 2026-11-22: **lever meaning inverted (owner's request).** Auto-land is now the
  default: a trader is called down when there is no lever or the lever is off. Lever on
  = interrogate only. If your lever was on to allow landing, switch it off. The dial
  section now explains the dial's `Mode` (steps, default 1).

## Status

Functional (author's label). This design has been simulated, not yet run in-game.
