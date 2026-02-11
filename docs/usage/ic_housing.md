# IC Housing / IC chip status checklist

Some scripts use the IC Housing itself (`db`) as a tiny "status display" or scratch storage.

## What scripts usually write

- `db Setting` as a status code / last-known value
  - Examples: "scan found ID", "config error code", etc.

## Common gotchas

- `db Error` is read-only.
  - Some scripts intentionally write `db Error` to force the IC into an error state so you notice it.
- If a script uses `db Setting` for status, watch it while debugging:
  - It often tells you why the script is doing nothing (missing device, invalid config, etc.).

