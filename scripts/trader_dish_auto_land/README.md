# trader_dish_auto_land

One chip that drives a **Satellite Dish** to find a trader, lock on, interrogate it and
call it down to your landing pad. Switch the lever on to stop the call-down. Press the
button to skip the trader it is working on. With the landing pad connected, the dish
turns off while a ship is on the pad.

*Replaces the four-chip `SatTraderTrack` multi-chip system, which never worked in-game. That system was removed on 2026-11-21; it is still in git history.*

## Pins

The IC Housing shows these names on its pins once the script is running.

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `dish` | Satellite Dish (Large recommended; Medium should work) |
| `d1` | `skip` | (optional) Logic Button: press to drop the current trader and scan for the next one |
| `d2` | `lever` | (optional) Lever: on (`Open` 1) = interrogate only, do not call down. Off or not connected = call down |
| `d3` | `led` | (optional) LED Display: last SignalStrength read (degrees to the contact, `-1` = none) |
| `d4` | `pad` | (optional) Landing Pad: while its `Mode` is above 1 (ship on the pad), the dish is turned off |

## What it does

0. **Pad check.** Before each scan move, if `pad` is connected and its `Mode` is above 1,
   the script writes the dish `On` 0, shows `600` and waits. When `Mode` is 0 or 1
   again, it writes `On` 1 and scans on. Without a pad it never turns the dish off. The
   pad is only checked while scanning, not during lock-on or interrogation.
1. **Scan.** Each move steps the dish 30° in Horizontal and 20° in Vertical (Vertical
   rows 0, 20, 40, 60, 80 from straight up, then back to 0). That visits all 60
   positions in 60 moves. At each one it waits for the dish's `Idle`, then reads
   `SignalStrength`. If `SignalID` shows a contact but `SignalStrength` is still -1, the
   signal is resolving, so it waits up to 9 s for it. Medium, Large and Exotic traders
   take up to 8.5 s. `SignalID` -1 means nothing is in view.
2. **Lock.** A contact is in view and it is not the last trader handled (`SignalID`).
   The script locks the dish onto it
   with `BestContactFilter` and raises power to `MAX_W`. It stops searching as soon as
   `WattsReachingContact` ≥ `MinimumWattsToContact`, which is what the trader needs before
   interrogation can start. Until then it steps Horizontal/Vertical one direction at a
   time and keeps any move that makes `SignalStrength` smaller. The first step is half
   the starting signal, and the step halves whenever no direction helps. Horizontal steps
   are made larger near straight up (up to 5×), where a degree of Horizontal moves the
   dish very little. It also stops when the dish is within 2°, or when the step is below
   0.5°. Vertical stays between 0 (straight up) and 90 (the horizon).
3. **Interrogate.** Every tick the script writes `Activate` 1 (held at 1 while
   interrogating) and reads `InterrogationProgress` (0 to 1). If the contact drifts more
   than 6° away, it re-locks (status `200`) without restarting the interrogation. If
   `SignalID` goes to -1 (the trader has gone), it goes back to scanning. A
   `SignalStrength` of -1 alone only means the dish is still resolving the signal, so
   it is not treated as a loss. There is no give-up timer: it runs until progress
   reaches 1, the trader leaves, or you press the skip button.
4. **Land.** When progress reaches 1, the script calls the trader down with a fresh
   press: `Activate` 0, 1, 0, one tick apart. The lever on skips this. The result stays
   on the status for 5 s. Then the script writes `Activate` 0 and scanning resumes from
   where the dish is pointing, with power back at `SCAN_W`.

**Skip button.** A press while locking on or interrogating drops that trader: the
status holds for 5 s, then the script writes `Activate` 0 (stopping any interrogation)
and scanning resumes. A button reads `1` only briefly, so the script checks it every
tick while the dish turns, while a signal resolves and while interrogating. A press
during the 5 s result pause is missed; press again if the status does not change.

The script remembers **one** trader: the last one it finished with (called, not called
or skipped). It skips that trader until it finishes with a different one.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `SCAN_W` | `5000` | Dish power while scanning. More power means contacts are visible from further away (fewer misses), but uses more power |
| `MAX_W` | `10000` | Dish power while locking on and interrogating. Large and exotic traders may need more; a working 2026 script uses up to 50,000 W |
| (inline) `30` / `20` | | Scan steps for Horizontal and Vertical (`add r0 r0 30`, `add r1 r1 20`) |
| (inline) `2` | | Lock accuracy in degrees (`ble r3 2 interrogate`) |
| (inline) `0.5` | | Smallest lock step in degrees (`blt r4 0.5 interrogate`) |
| (inline) `6` | | Drift that triggers a re-lock during interrogation (`bgt r2 6 lock`) |
| (inline) `18` | | Ticks to wait for a seen contact's signal to resolve (18 = 9 s) (`move r14 18`) |
| (inline) `5` | | Seconds the result stays on the status before scanning again (`sleep 5`) |

## Status (IC Housing `Setting`)

| Status | Meaning |
| --- | --- |
| `100` | scanning |
| `200` | locking on (also re-locking during interrogation) |
| `3xx` | interrogating, `xx` = `InterrogationProgress` in % (`342` = 42%). Holds for 5 s after a skip |
| `400` | interrogated, not called (lever on) |
| `500` | called down |
| `600` | ship on the landing pad: dish off, waiting |
| `900` | dish missing |

While interrogating, `300` that never climbs means progress is stuck at 0. If the
status shows values far above `400` (e.g. `5300`), `InterrogationProgress` runs 0 to
100, not 0 to 1. Please report which one you see.

## Setup

1. Build the dish with power and data. Put the IC Housing on the same network.
2. Set `d0` to the dish. Optionally set `d1` to a Logic Button, `d2` to a Lever, `d3`
   to an LED Display and `d4` to the landing pad.
3. Set up your landing pad: powered, with its **Landing Pad Data and Power** on the
   **same data network as the dish**. The dish can only call a trader down to a pad on
   its own network. Use only one landing pad on that network. The pad must be big
   enough for the trader; the comms computer shows the size each trader needs.
4. Paste `trader_dish_auto_land.ic10` into the chip and run it.

Traders cannot land during a weather event.

## What still needs an in-game check

This was designed from community write-ups of the current (2026) trading system and tested
against a simulated dish. The interrogate and call-down sequence follows a working 2026
system, the `trade_dispatch.ic10` script in
[stationeering-systems/moon-normal-standard](https://github.com/stationeering-systems/moon-normal-standard/tree/main/trade).
That script holds `Activate` 1 until `InterrogationProgress` ≥ 1, then calls down by
writing `Activate` 1 then 0 on a dish on the pad's network. It locks at
SignalStrength ≤ 2 and reads the trader type from `ContactSlotIndex` (0 Utility,
1 Basic, 2 Medium, 3 Large, 4 Exotic). These points are still assumptions:

- **SignalStrength is degrees to the contact, smaller is better, `-1` when nothing is
  visible.** Older wiki text says "negative, larger is better", which is the pre-2026
  behaviour. If the LED shows negative numbers while a trader is in view, this assumption
  is wrong and the script needs changing. Please report what you see.
- **Vertical 0 is straight up, 90 is the horizon.**
- **The interrogating dish can also call the trader down.** The working script uses a
  second dish on the pad's network for that. Its author's guide also says "the dish used
  to interrogate traders can also initiate landing". If the status reaches `500` and
  nothing lands, check the Setup step 3 network first, then use the comms computer's
  Land button and report it.
- **Writing `Activate` 0 stops interrogation** (wiki). The script relies on this when
  you skip a trader and when it resets.
- **Power.** `MAX_W` 10,000 W may not be enough for large or exotic traders. Raise it if
  the status stays at `300` (progress 0%).
- **`InterrogationProgress` runs 0 to 1.** The working script checks `≥ 1`, so 0 to 1 is
  likely. If the status shows values far above `400`, it runs 0 to 100.
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
- **Third in-game run (2026-11-22):** still no call-down. A working 2026 script showed
  why: `Activate` keeps the value written, so the old "write 1 again" after
  interrogation was not a new press. Fixed; see the change history.
- **Fourth in-game run (2026-11-22): one ship was called down and landed** (first
  confirmed call-down). After that the status stayed at `100`. The 1 s wait after each
  move is too short for slower signals: the working tracker waits up to 8.5 s for
  Medium, Large and Exotic traders. The script now waits while `SignalID` shows a
  contact and `SignalStrength` is still -1. If it still stays at `100` with traders
  listed on the comms computer, try a higher `SCAN_W`: the working tracker scans Utility
  and Basic traders at 50,000 W.

- **Landing pad `Mode` (2026-11-23).** The pad check copies the working 2026
  `trade_pad_res.ic10`, which treats pad `Mode` above 1 as "not available". Which
  value means "on approach" and which "landed" is not known, nor which pad piece the
  pin must point at (the reference just says "Landing Pad"). Please read the pad's
  `Mode` on a Logic Reader when it is empty, while a ship comes down and while one is
  landed. If the status shows `600` with the pad empty, or the ship turns back when the
  dish goes off, report it.

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
- 2026-11-22: **call-down fixed to match a working 2026 script.** In-game nothing was
  ever called down. `Activate` keeps the value written, so writing 1 again after
  interrogation was not a press. The script now:
  - holds `Activate` 1 while interrogating
  - calls down with `Activate` 0, 1, 0
  - writes `Activate` 0 on every reset and skip
  - treats only `SignalID` -1 as "trader gone"; `SignalStrength` -1 means still resolving

  The simulated dish now latches `Activate` and acts only on a 0 → 1 change. With it,
  the old script fails 4 of the 7 scenarios.
- 2026-11-22: **wait for slow signals to resolve.** In-game one ship landed, then the
  status stayed at `100`. After each move the script now waits up to 9 s while
  `SignalID` shows a contact but `SignalStrength` is still -1. It no longer reads once
  after a fixed 1 s. To fit, the 600 s give-up timer was removed (interrogation ends
  when the trader leaves, or with the skip button). Each scan move now steps both axes,
  and Vertical is clamped at 0 instead of stepping over the top. The simulated dish now
  resolves slowly when asked; the old script never found such a trader.

- 2026-11-23: **dish off while a ship is on the pad (owner's request).** New optional
  `pad` pin on `d4`. Each scan move now goes through `reset`, so the pad is checked
  before every move. To stay within 128 lines, the two header comments were removed
  (the status codes are in this README) and the lock-on step code was rewritten
  without branches (same steps). Simulated only.

## Status

Functional (author's label). This design has been simulated, not yet run in-game.
