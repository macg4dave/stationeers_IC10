# Modular wiring/setup playbook (master + workers)

Use this when setting up any feature under `modular scripts/<feature>/`.

## Goal

Make modular systems predictable for both players and AI by using one consistent
wiring order and setup flow.

## Wiring order rule (required)

If chips are wired to other chips (direct IC housing links) or shared channels
(Logic Memory command/data), map those links **first** starting at `d0` and
then descending: `d0`, `d1`, `d2`, ...

Only after chip-link wiring is assigned, map:

1. user input controls (buttons/levers/switches)
2. feature devices (dish/vents/analyzers/etc.)

### Why this helps

- Faster setup: users always wire the same priority first.
- Fewer mistakes: no mixed "buttons first" vs "workers first" layouts.
- Better AI output: generated READMEs/scripts follow one shared convention.

## Recommended mapping pattern

### Master chip (example)

- `d0` = worker A link (housing or command/data channel)
- `d1` = worker B link
- `d2` = shared command token memory
- `d3` = shared command type memory
- `d4` = user control 1
- `d5` = user control 2

### Worker chip (example)

- `d0` = shared command token memory
- `d1` = shared command type memory
- `d2` = worker input/output channel 1
- `d3` = worker input/output channel 2
- `d4` = feature device A
- `d5` = feature device B

Use fewer registers when possible; this is a priority model, not a requirement
that all `d0..d5` must be used.

## End-user setup checklist

1. Place all IC housings/chips for the modular feature.
2. Label chips physically/in-game (Master, Worker A, Worker B, ...).
3. Wire chip-link channels first (`d0` downward) on every involved chip.
4. Wire controls and feature devices after link channels.
5. Paste scripts into the correct chips.
6. Confirm each chip reports status via `db Setting` (per feature README).
7. Run first command/test action and verify expected status transitions.

## Troubleshooting quick checks

If the system does nothing:

- Confirm each chip has the correct script (master vs worker).
- Re-check that shared channel devices are on the intended `d` slots.
- Confirm command token channel is shared by all required chips.
- Confirm worker chips are enabled (`On`) if master controls worker power.
- Check each chip's `db Setting` status code against the feature README.

## Author checklist (for new modular features)

In `modular scripts/<feature>/README.md`, always include:

- full per-chip `d0..d5` map
- explicit line stating links start at `d0` and descend
- shared-memory contract (writer/reader for each channel)
- status code table for every chip

