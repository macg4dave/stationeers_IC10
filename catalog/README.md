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
- `catalog/recipes/index.json`
  - Index of producer-specific recipe catalogs.
- `catalog/recipes/<Producer>/recipes.json`
  - One JSON file per recipe-producing device page (starting with fabricators such as `Autolathe`).

## Schema (v1)

Each device JSON is shaped like:

- `source`
  - `kind` (optional): `"wiki_import"` (default) or `"best_guess"` for manually curated entries when wiki data is unavailable
  - `wikiUrl`: string
  - `wikiTitle`: string
  - `retrievedAt`: ISO-8601 string
  - `notes` (optional): short provenance note (recommended for `best_guess`)
- `identity`
  - `itemName`: string | null (wiki “Item Name”, when present)
  - `itemHash`: number | null (wiki “Item Hash”, when present)
- `io`
  - `modeValues` (optional): array of `{ value, meaning, settingInterpretation }` for devices that document an enum-like `Mode` table
  - `parameters`: array of `{ name, type, description }`  (intended “write”)
  - `outputs`: array of `{ name, type, description }`     (intended “read”)

## Recipe catalog schema (v1)

Recipe catalogs are kept separate from device IO catalogs so existing consumers of
`catalog/index.json` do not need to learn a second schema just to keep working.

- `catalog/recipes/index.json`
  - `version`: number
  - `producers`: array of
    - `wikiTitle`: producer/device title, such as `Autolathe`
    - `pageTitle`: source wiki page title, such as `Autolathe/Recipes`
    - `file`: relative path to the producer recipe catalog
    - `recipeCount`: number of parsed recipes

- `catalog/recipes/<Producer>/recipes.json`
  - `source`
    - `kind`: currently `wiki_import`
    - `wikiUrl`: source page URL
    - `wikiTitle`: source page title
    - `retrievedAt`: ISO-8601 timestamp
  - `producer`
    - `wikiTitle`: producer/device title
    - `itemName`: string | null (copied from the device catalog when available)
    - `itemHash`: number | null (copied from the device catalog when available)
  - `recipes`: array of
    - `item`: `{ wikiTitle, displayName, itemName, itemHash }`
    - `tier`: string
    - `time`: number
    - `energy`: number
    - `inputs`: array of `{ wikiTitle, displayName, quantity }`

### Recipe normalization notes

- The importer preserves wiki link targets such as `Ingot_(Iron)` so later tooling can match exact page titles.
- The importer also stores human-readable labels via `displayName`.
- For each recipe output item, the importer also looks up the linked wiki page and stores the in-game `itemName` and `itemHash` when the page exposes them.
- Decimal commas from the wiki, such as `0,5`, are normalized to JSON numbers like `0.5`.
- Recipe output data is currently represented by the recipe item itself; individual output stack counts are not inferred beyond what the page explicitly shows.

### Type normalization

The importer lowercases wiki types (e.g. `Float`/`float` -> `float`).

### Notes on wiki inconsistencies

The wiki sometimes varies capitalization/spelling (example: `Requiredpower`). The catalog stores the name **as written on the page**.

### Best-guess entries

If a device does not have complete wiki Data Network info yet, mark it as:

- `source.kind: "best_guess"`
- include a brief `source.notes` describing what was inferred and why

This keeps estimated entries explicit and easy to review later.

## Hash guidance for script authors

When writing batch/network IC10 (`lb/sb/lbn/sbn`), be explicit about which hash you are using:

- **Name hash**: `HASH("...")` of the in-game renamed device label (exact, case-sensitive).
- **Type/prefab hash**: use an authoritative device prefab hash value when available.

For many devices, a prefab hash is documented in the `io.outputs` entry named `Prefab Hash`.

Practical recommendation:

1. use prefab hash to target device type
2. optionally combine with exact name hash to target a subset
3. document both values/expectations in script README setup steps
