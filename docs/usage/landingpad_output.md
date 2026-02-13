# Landingpad Output setup checklist

Use this when scripting against landingpad output devices.

## 1) Pick the correct device variant first

- Gas script -> use `Landingpad_Gas_Output` fields (example: `RatioVolatiles`).
- Liquid script -> use `Landingpad_Liquid_Output` fields (example: `RatioLiquidVolatiles`).

If these are mixed, scripts can compile but never actuate correctly.

## 2) Match ratio field to the chosen variant

- Gas output: read `RatioVolatiles`.
- Liquid output: read `RatioLiquidVolatiles`.

## 3) Pressure cutoff source should be explicit

If using pressure as a safety cutoff, document exactly where it comes from.

Recommended: a dedicated `Pipe Analyzer` readout only (in kPa), so behavior is deterministic.

## 4) Do not assume every field is safe on every landingpad output

- Some inferred/assumed fields may differ from in-game behavior.
- If a line faults at runtime, remove that field access first (common candidate: `Lock`).

## 5) Add simple status codes for fast in-game debugging

Use IC housing `db Setting` to expose branch decisions, for example:

- condition met (request ON)
- condition not met (request OFF)
- safety cutoff active (forced OFF)

This avoids guessing when setup looks correct but behavior is wrong.

## 6) Thresholds should tolerate real-world readout jitter

A strict `0.999999` can miss practical "full" readings.
Start with a robust threshold (example: `0.999`) and tune from there.
