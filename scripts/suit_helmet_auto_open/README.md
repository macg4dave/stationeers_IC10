# suit_helmet_auto_open

Opens your **Hardsuit Helmet** in safe air and closes it the moment the air is not safe. If you close it yourself, it stays closed. It also closes the helmet in a fire or in air that would harm you. It never touches the suit's own air settings.

*Previously called `hardsuit_helmet_temp_pressure_open`.*

## Pins

| Pin | Device |
| --- | --- |
| `db` | Hardsuit (the chip goes in the suit) |
| `d0` | Hardsuit Helmet |

## What it does

- Safe = outside 4–45 °C **and** 80–150 kPa.
- Safe: opens the helmet once.
- If you close it after it opened, it stays closed until the air goes unsafe and safe again, or you open it yourself.
- Unsafe: closes immediately.
- **Fire:** if the suit or the helmet reports `Combustion`, the helmet closes. When the
  fire is out (and the air is otherwise safe) it opens again.
- **Bad air (visor open only):** the helmet's own readings then show the air you are
  breathing. If oxygen is below `O2_MIN_KPA`, CO₂ above `CO2_MAX_KPA` or pollutant
  above `POL_MAX_KPA` (partial pressures: ratio × helmet `Pressure`), the helmet closes
  and **stays closed** until you open it yourself, so it does not open and shut every
  second. Open it into bad air again and it closes again. Air that would not harm you
  leaves it open. If the open helmet reads below `MIN_KPA` itself (no reading), the
  check is skipped; the outside pressure check still closes it in thin air.
- The suit's filters and air release are left to you.
- Checks once a second.

## Settings

Edit the `define` lines at the top of `suit_helmet_auto_open.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `MIN_C` | `4` |  |
| `MAX_C` | `45` |  |
| `MIN_KPA` | `80` |  |
| `MAX_KPA` | `150` |  |
| `O2_MIN_KPA` | `16` | Close if the air has less oxygen than this (kPa) |
| `CO2_MAX_KPA` | `2` | Close if the air has more CO₂ than this (kPa) |
| `POL_MAX_KPA` | `0.1` | Close if the air has more pollutant than this (kPa) |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. Put an IC10 chip in the device's own IC slot.
3. Paste `suit_helmet_auto_open.ic10` into the chip and run it.

## Notes

- No status number: `db` is the suit.
- **Harm thresholds are not confirmed.** The wiki gives only the total pressure humans
  tolerate (11 to ~250 kPa), not per-gas limits. `O2_MIN_KPA`, `CO2_MAX_KPA` and
  `POL_MAX_KPA` are cautious guesses: too cautious only closes the helmet. If it closes
  in air you know is fine, raise them.
- The air check assumes the open helmet's `Pressure` and ratios show the room's air
  (wiki: "inside the Hardsuit Helmet"). Not yet checked in-game.
- **Do not write the suit's `AirRelease` or `Filtration`.** In-game (2026-11-23), writing
  `AirRelease` 0 at normal pressure turned the suit's air off, and switching
  `Filtration` made a ticking sound. If the script ever turned your air release off,
  switch it back on by hand: the suit keeps the value.
- If the open helmet always reads 0 kPa in-game, the bad-air check never runs (it is
  skipped without a reading) and only the fire and outside checks protect you.
- Field names (`Combustion`, helmet `Pressure` and ratios) are from the
  wiki's Hardsuit and Hardsuit Helmet pages.

## Change history

- 2026-11-23: closes the helmet in a fire and, while the visor is open, in air that
  would harm you (low O₂, CO₂, pollutant; held closed until you reopen it)
  (owner's request). Simulated only.
- 2026-11-23: **fix, same day.** In-game the script turned the suit's air off and the
  helmet did not stay open. The `AirRelease` over-pressure control (it wrote 0 at
  normal pressure) is removed, as is the earlier `Filtration` switch (ticking sound).
  The bad-air check is skipped when the open helmet reads below `MIN_KPA`: an open
  helmet probably reads 0 kPa, which looked like no oxygen and closed it.
- 2026-11-21: remade and renamed. Rewritten to be shorter; only unlocks the helmet when it needs to move it. Behaviour unchanged.

## Status

Functional (author's label from before the remake; re-test in-game).
