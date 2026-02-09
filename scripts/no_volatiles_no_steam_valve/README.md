# no_volatiles_no_steam_valve

Opens a **Pipe Digital Valve** only when the connected **Pipe Analyzer** reports **no Volatiles** and **no Steam**.

## Purpose

Useful as a “clean-gas only” gate: if either Volatiles or Steam is present in the pipe, the valve stays closed.

## Devices

Required:

- 1× Pipe Analyzer
- 1× Pipe Digital Valve
- 1× IC Housing + IC10 chip (or equivalent)

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Pipe Digital Valve

## How it works

Every tick it reads:

- `RatioVolatiles` (from the Pipe Analyzer)
- `RatioSteam` (from the Pipe Analyzer)
- `Pressure` (from the Pipe Analyzer, in kPa)

Then it sets the valve:

- `On = 1` if both ratios are $\le \text{EPS}$ **and** `Pressure > MIN_PRESSURE`
- `On = 0` otherwise

`EPS` is a tiny tolerance to avoid floating-point “almost zero” values keeping the valve closed.

## Tuning

In `no_volatiles_no_steam_valve.ic10`:

- `EPS` (default `0.000001`)
  - Increase if you see tiny non-zero readings when the pipe is “effectively clean”.
  - Decrease if you need stricter filtering.

- `MIN_PRESSURE` (default `1.0` kPa)
  - Increase if you only want the valve to open when the line is more “pressurized”.
  - Decrease if you just want to block opening on near-vacuum / empty pipe.

## Status

Functional
