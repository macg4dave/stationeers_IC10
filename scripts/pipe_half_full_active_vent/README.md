# pipe_half_full_active_vent

**Purpose:** Turns an **Active Vent** on when the connected **Pipe Analyzer** reports the pipe network is less than *half full of air (gas)*, relative to a target pressure.

## Devices

Required:

- Pipe Analyzer
- Active Vent

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Active Vent

## How it works

The Pipe Analyzer exposes:

- `Volume` — the pipe network volume
- `Temperature` — gas temperature (Kelvin)
- `TotalMoles` — total gas amount in the network

For gas networks, “volume full” is not meaningful (gas always occupies the whole volume). Instead, this script estimates a **target number of moles** for the network using the ideal gas law:

$$n = \frac{P \cdot V}{R \cdot T}$$

Then it uses hysteresis around a “half full” point:

- Vent turns **ON** when `TotalMoles < targetMoles * FULLNESS_RATIO` (needs more air)
- Vent turns **OFF** when `TotalMoles > targetMoles * (FULLNESS_RATIO + HYSTERESIS_BAND)`
- Otherwise, it keeps the previous vent state (prevents rapid flicker)

If the analyzer reports `Error = 1`, the vent is forced **OFF**.

## Setup

1. Place an IC Housing (or Advanced IC Housing) on the same data network as the devices.
2. Insert an IC10 chip and paste in `pipe_half_full_active_vent.ic10`.
3. In the IC editor, set:
   - `d0` to the Pipe Analyzer
   - `d1` to the Active Vent
4. Configure the Active Vent settings **in-game** (Mode, pressure settings, etc.). The script only toggles `On`.

## Tuning

In `pipe_half_full_active_vent.ic10`:

- `TARGET_PRESSURE_KPA` (default `100`) — what “100% full” means
- `FULLNESS_RATIO` (default `0.5`) — desired fullness (as a fraction of target moles)
- `HYSTERESIS_BAND` (default `0.05`) — extra margin above `FULLNESS_RATIO` to switch OFF

Notes:

- The script uses $R = 8.314462618$ in units of $(\text{kPa}*\text{L})/(\text{mol}*\text{K})$, which assumes the analyzer `Volume` is in liters.

## Status

Functional
