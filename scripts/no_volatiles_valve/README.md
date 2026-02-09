# no_volatiles_valve

Closes a **Pipe Digital Valve** when the connected **Pipe Analyzer** reports **no Volatiles**.

## Purpose

Acts as a “volatiles-present gate”:

- If Volatiles are present in the pipe, the valve is **open**.
- If Volatiles are not present (at or below a small tolerance), the valve is **closed**.

## Devices

Required:

- 1× Pipe Analyzer
- 1× Pipe Digital Valve
- 1× IC Housing + IC10 chip (or equivalent)

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Pipe Digital Valve

## How it works

Every tick it reads `RatioVolatiles` from the Pipe Analyzer.

Then it sets the valve:

- `On = 0` if `RatioVolatiles \le EPS`
- `On = 1` if `RatioVolatiles > EPS`

`EPS` is a tiny tolerance to avoid floating-point “almost zero” values.

## Tuning

In `no_volatiles_valve.ic10`:

- `EPS` (default `0.000001`)
  - Increase if you see tiny non-zero readings when the pipe is “effectively no volatiles”.
  - Decrease if you need stricter filtering.

## Status

Functional
