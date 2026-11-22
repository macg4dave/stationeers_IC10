# trader_dish_auto_land

One chip that drives a **Satellite Dish** to find a trader, lock on, interrogate it and
call it down to your landing pad. Switch the lever on to stop the call-down. Press the
button to skip the trader it is working on.

*Replaces the four-chip `SatTraderTrack` multi-chip system, which never worked in-game. That system was removed on 2026-11-21; it is still in git history.*

## Pins

The IC Housing shows these names on its pins once the script is running.

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `dish` | Satellite Dish (Large recommended; Medium should work) |
| `d1` | `skip` | (optional) Logic Button: press to drop the current trader and scan for the next one |
| `d2` | `lever` | (optional) Lever: on (`Open` 1) = interrogate only, do not call down. Off or not connected = call down |
| `d3` | `led` | (optional) LED Display: last SignalStrength read (degrees to the contact, `-1` = none) |

## What it does

1. **Scan.** The script points the dish across the sky: a full turn in 30° Horizontal
   steps, then the next Vertical row, 20° further down from straight up (rows 0, 20, 40,
   60, 80, then back to 0). That is 60 positions. At each one it waits for the dish's
   `Idle`, waits 1 s more, then reads `SignalStrength`. `-1` means nothing is in view.
2. **Lock.** A contact is in view and it is not the last trader handled (`SignalID`).
   The script locks the dish onto it
   with `BestContactFilter` and raises power to `MAX_W`. It stops searching as soon as
   `WattsReachingContact` ≥ `MinimumWattsToContact`, which is what the trader needs before
   interrogation can start. Until then it steps Horizontal/Vertical one direction at a
   time and keeps any move that makes `SignalStrength` smaller. The first step is half
   the starting signal, and the step halves whenever no direction helps. Horizontal steps
   are made larger near straight up (up to 5×), where a degree of Horizontal moves the
   dish very little. It also stops when the dish is within 2°, or when the step is below
   0.5°. Steps can go "over the top" (past straight up). Vertical never goes below 90
   (the horizon).
3. **Interrogate.** If the dish's `Activate` reads 0, the script
   writes `Activate` 1 to start interrogation and starts the give-up timer. Every tick
   it checks `InterrogationProgress`. If the contact drifts more than 6° away, it
   re-locks (status `200`) without restarting the interrogation. If the contact
   disappears, it goes back to scanning. After 600 s of checks (re-locks not counted) it
   gives up.
4. **Land.** When progress reaches 1, `Activate` 1 again calls the trader down, unless
   the lever is on. The result stays on the status for 5 s. Then scanning resumes from where
   the dish is pointing, with power back at `SCAN_W`.

**Skip button.** A press while locking on or interrogating drops that trader: the
status holds for 5 s, then scanning resumes. A button reads `1` only briefly, so the
script checks it every tick while the dish turns and while interrogating. It does not
check during the 1 s settle after each move or the 5 s result pause, so a press in
those moments can be missed. Press again if the status does not change.

The script remembers **one** trader: the last one it finished with (called, not called,
timed out or skipped). It skips that trader until it finishes with a different one.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `SCAN_W` | `5000` | Dish power while scanning. More power means contacts are visible from further away (fewer misses), but uses more power |
| `MAX_W` | `10000` | Dish power while locking on and interrogating. Large and exotic traders may need more |
| (inline) `30` / `20` | | Scan steps for Horizontal and Vertical (`add r0 r0 30`, `add r1 r1 20`) |
| (inline) `2` | | Lock accuracy in degrees (`ble r3 2 locked`) |
| (inline) `0.5` | | Smallest lock step in degrees (`blt r4 0.5 locked`) |
| (inline) `6` | | Drift that triggers a re-lock during interrogation (`bgt r2 6 lock`) |
| (inline) `1200` | | Interrogation give-up, in ticks (1200 = 600 s) (`move r13 1200`) |
| (inline) `5` | | Seconds the result stays on the status before scanning again (`sleep 5`) |

## Status (IC Housing `Setting`)

| Status | Meaning |
| --- | --- |
| `100` | scanning |
| `200` | locking on (also re-locking during interrogation) |
| `3xx` | interrogating, `xx` = `InterrogationProgress` in % (`342` = 42%). Holds for 5 s after the give-up timer runs out or a skip |
| `400` | interrogated, not called (lever on) |
| `500` | called down |
| `900` | dish missing |

While interrogating, `300` that never climbs means progress is stuck at 0. If the
status shows values far above `400` (e.g. `5300`), `InterrogationProgress` runs 0 to
100, not 0 to 1. Please report which one you see.

## Setup

1. Build the dish with power and data. Put the IC Housing on the same network.
2. Set `d0` to the dish. Optionally set `d1` to a Logic Button, `d2` to a Lever and `d3`
   to an LED Display.
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
- **Skipping during interrogation** only stops the script. It does not tell the dish to
  stop interrogating, because what writing `Activate` does at that point is unknown
  (the wiki says it may stop interrogation). If the dish keeps interrogating the
  skipped trader, the next lock-on may find `Activate` still at 1 (see below).
- **Power.** `MAX_W` 10,000 W may not be enough for large or exotic traders. One write-up
  quotes up to 8,000 W for 600 s. Raise it if interrogation never progresses.
- **`Activate` going back to 0.** The script assumes `Activate` reads 0 when the dish is
  not interrogating. If it stays 1 (for example after a call-down), the script will not
  press it again and the give-up timer is not reset. Watch it on a Logic Reader. If the
  status goes from `3xx` back to `100` after about a second, this is the cause.
- **`InterrogationProgress` runs 0 to 1.** The catalog (from the wiki) calls it a
  percentage. If it runs 0 to 100, the script treats 1% as finished and calls down too
  early. If the status jumps from `3xx` to `500` within seconds, this is the cause.
- **First in-game run (2026-11-22):** contacts were found and the LED changed, but the
  status stayed at `200`: the lock-on search never finished, so interrogation never
  started. In the simulator a dish that turns 8°/s takes 1½–3 minutes to lock on, and a
  slower dish or a moving trader takes longer. The script now stops searching once
  `WattsReachingContact` ≥ `MinimumWattsToContact`.
- **`WattsReachingContact` and `MinimumWattsToContact`** are taken from the wiki's dish
  page and have not been read in-game. If the chip shows an error on those lines, the
  game does not have them under these names. If the status still stays at `200`, watch
  both values on a Logic Reader and report them.
- **Second in-game run (2026-11-22):** the status reached `300` but nothing was called
  down. Once it showed `5441220`: `ContactTypeId` is a large ID (about 5.44 million),
  not a small type number, so the old `phase × 100 + ContactTypeId` status hid the
  phase. Whether interrogation progressed is not known yet. The status now shows the
  progress %, so the next run will tell. If it stays at `300`, check
  `WattsReachingContact` against `MinimumWattsToContact` and try a higher `MAX_W`.

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
- 2026-11-22: **lock-on ends once enough power reaches the trader.** In-game, the status
  stayed at `200` and the trader was never interrogated. Lock-on now runs at `MAX_W`
  and stops when `WattsReachingContact` ≥ `MinimumWattsToContact`, as well as at 2°.
  To stay within 128 lines, three labels became relative branches (`brlt`, `brgez`,
  `brdns`), and after a failed search round the script no longer resets its stored
  position (the dish was not moved back anyway).
- 2026-11-22: **dial removed, skip button added on `d1` (owner's request).** The dial
  filter never worked in-game (`ContactTypeId` read 0). `d1` is now a Logic Button,
  checked every tick, that drops the current trader. The interrogation loop no longer
  sleeps 1 s per check, so the give-up timer is now 1200 ticks, a true 600 s. If you
  had a dial on `d1`, replace it with a button.
- 2026-11-22: **status codes changed.** In-game the status read `5441220` because
  `ContactTypeId` is a large ID. The status is now `phase × 100` only (`100`, `200`,
  `400`, `500`, `900`), and while interrogating it is `300` + progress %. The phase is
  now set before the first status write, so the chip no longer shows `0` at start.

## Status

Functional (author's label). This design has been simulated, not yet run in-game.
