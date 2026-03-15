# Sorter setup checklist

Use this when an IC10 script writes `Mode` and `Output` on a **Sorter**.

## Logic-mode routing

- For per-item routing from IC10, set **`Mode = 2`** (**Logic**).
- In Logic mode, your script must write **`Output` for every item**.
- After the item leaves, the Sorter resets `Output` back to **`-1`**.

If a script writes `Output` but the Sorter seems to ignore it, check `Mode` first.
That is the usual gremlin.

## Output orientation

When **facing the Sorter outputs** with the **power switch on your right**:

- `Output = 0` exits **right**
- `Output = 1` exits **left**

Document this in script setup steps whenever the lane choice matters.

## Useful fields

- `Mode` — routing mode (`0` split, `1` filter, `2` logic)
- `Output` — target lane for the next released item in logic mode
- `ImportCount` / `ExportCount` — good for edge-detecting item movement
- slots `0`, `1`, `2` — import, export accept, export reject

## Sanity checks

- Sorter is powered and on the same data network as the IC
- `On = 1`
- `Mode = 2` when using IC-controlled routing
- Chute network matches the intended left/right outputs
