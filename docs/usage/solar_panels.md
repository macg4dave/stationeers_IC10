# Solar panels (batch control) setup checklist

## What scripts usually write

- `Horizontal`
- `Vertical`

## Minimum to work

- Panels connected to the same data network as the IC Housing
- Panels are the correct device type(s) expected by the script (many scripts batch by `PrefabHash`)

## Common gotchas

- Batch writes only reach devices on the data network.
- If a script supports "per-panel offsets by label/name", the labels must match exactly:
  - Name hashes are exact; no substrings.

## Common patterns that scripts use

- Many trackers set a "morning park" position at night (example: horizontal = -90 / East) and resume tracking during the day.
