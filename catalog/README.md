# Device IO catalog

This folder stores a **plain-text catalog** of Stationeers device IO flags (Logic I/O “variables”) that IC10 code can read/write.

## Where the data comes from

- Primary source: the Stationeers wiki device pages, especially the **Data Network Properties** tables:
  - “Data Parameters” (writable, often also readable)
  - “Data Outputs” (readable)

Example source page:

- <https://stationeers-wiki.com/Pipe_Analyzer>

## File layout

- `catalog/devices/<WikiTitle>.json`
  - One JSON file per device page.

## Schema (v1)

Each device JSON is shaped like:

- `source`
  - `wikiUrl`: string
  - `wikiTitle`: string
  - `retrievedAt`: ISO-8601 string
- `identity`
  - `itemName`: string | null (wiki “Item Name”, when present)
  - `itemHash`: number | null (wiki “Item Hash”, when present)
- `io`
  - `modeValues` (optional): array of `{ value, meaning, settingInterpretation }` for devices that document an enum-like `Mode` table
  - `parameters`: array of `{ name, type, description }`  (intended “write”)
  - `outputs`: array of `{ name, type, description }`     (intended “read”)

### Type normalization

The importer lowercases wiki types (e.g. `Float`/`float` -> `float`).

### Notes on wiki inconsistencies

The wiki sometimes varies capitalization/spelling (example: `Requiredpower`). The catalog stores the name **as written on the page**.

## Hash guidance for script authors

When writing batch/network IC10 (`lb/sb/lbn/sbn`), be explicit about which hash you are using:

- **Name hash**: `HASH("...")` of the in-game renamed device label (exact, case-sensitive).
- **Type/prefab hash**: use an authoritative device prefab hash value when available.

For many devices, a prefab hash is documented in the `io.outputs` entry named `Prefab Hash`.

Practical recommendation:

1. use prefab hash to target device type
2. optionally combine with exact name hash to target a subset
3. document both values/expectations in script README setup steps
