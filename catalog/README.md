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
  - `parameters`: array of `{ name, type, description }`  (intended “write”)
  - `outputs`: array of `{ name, type, description }`     (intended “read”)

### Type normalization

The importer lowercases wiki types (e.g. `Float`/`float` -> `float`).

### Notes on wiki inconsistencies

The wiki sometimes varies capitalization/spelling (example: `Requiredpower`). The catalog stores the name **as written on the page**.
