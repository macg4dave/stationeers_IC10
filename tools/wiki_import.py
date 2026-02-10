"""Import Stationeers wiki device IO tables into the local catalog.

Goal
- Given a Stationeers wiki URL (e.g. https://stationeers-wiki.com/Pipe_Analyzer),
  extract the Data Network Properties tables:
  - "Data Parameters" (writable)
  - "Data Outputs" (readable)
- Write a JSON file to catalog/devices/<WikiTitle>.json and update catalog/index.json.

Design constraints
- No external dependencies (stdlib only).
- Best-effort parsing: the wiki is community-maintained and not perfectly consistent.

Usage
  python tools/wiki_import.py https://stationeers-wiki.com/Pipe_Analyzer

"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import parse_qs, urldefrag, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
DEVICES_DIR = CATALOG_DIR / "devices"
INDEX_PATH = CATALOG_DIR / "index.json"


@dataclass
class IoField:
    name: str
    type: str
    description: str


@dataclass
class DeviceCatalogEntry:
    source: dict
    identity: dict
    io: dict


def _parse_wiki_url(url: str) -> tuple[str, str, Optional[str]]:
    """Parse a stationeers-wiki URL.

    Supports:
      - https://stationeers-wiki.com/Pipe_Analyzer
      - https://stationeers-wiki.com/index.php?title=Pipe_Analyzer
      - Section import from multi-device pages:
          https://stationeers-wiki.com/Sensors#Gas_Sensor

    Returns:
      - wiki_title: used for output filename and index entry
      - fetch_url: URL without fragment (what we actually download)
      - fragment: section anchor id (or None)
    """

    parsed = urlparse(url)
    if "stationeers-wiki.com" not in parsed.netloc:
        raise ValueError(f"Unsupported wiki URL host: {url}")

    fetch_url, fragment = urldefrag(url)
    fragment = fragment or None

    # Determine page title from either /<Title> or index.php?title=<Title>
    page_title: Optional[str] = None
    path = (parsed.path or "/").lstrip("/")
    if not path:
        page_title = None
    elif path.lower() == "index.php":
        qs = parse_qs(parsed.query)
        title_vals = qs.get("title")
        if title_vals:
            page_title = title_vals[0]
    else:
        # First segment is the page title
        page_title = path.split("/")[0]

    if not page_title:
        raise ValueError(f"Unsupported wiki URL format: {url}")

    # If the URL includes a fragment, treat that as the logical "device title".
    wiki_title = fragment or page_title
    return wiki_title, fetch_url, fragment


def _normalize_type(type_str: str) -> str:
    t = type_str.strip().lower()
    # wiki sometimes uses bool/boolean or integer/int
    t = {"bool": "boolean", "int": "integer"}.get(t, t)
    return t


def _normalize_field_name(field_name: str) -> str:
    """Normalize known wiki inconsistencies/typos for IO field names."""

    name = field_name.strip()
    # Common typo seen in some Data Network templates.
    if name == "Referenceld":
        return "ReferenceId"
    return name


def _dedupe_fields(fields: List[IoField]) -> List[IoField]:
    """Deduplicate fields by (name,type).

    Some wiki tables include both a high-level row and a 0/1 enumerated row for
    the same parameter (e.g. Idle). We keep the earliest occurrence and fill an
    empty description from later duplicates.
    """

    out: List[IoField] = []
    seen: dict[tuple[str, str], int] = {}
    for f in fields:
        key = (f.name, f.type)
        if key not in seen:
            seen[key] = len(out)
            out.append(f)
            continue

        i = seen[key]
        if (not out[i].description) and f.description:
            out[i] = IoField(name=out[i].name, type=out[i].type, description=f.description)

    return out


def _infer_type_from_name(field_name: str) -> Optional[str]:
    """Best-effort fallback for pages where the Data Type column is blank.

    Some wiki tables render the type as an icon (img alt/title) or omit it.
    We try not to guess unless the name is very common and unambiguous.
    """

    key = re.sub(r"[^a-z0-9]+", "", field_name.strip().lower())
    mapping = {
        # Common boilerplate flags
        "on": "boolean",
        "power": "boolean",
        "error": "boolean",
        "lock": "boolean",
        # Common numeric fields
        "ratio": "float",
        "maximum": "integer",
        "requiredpower": "integer",
        # "Setting" is usually a numeric setpoint, even when the wiki marks it as unused.
        "setting": "integer",
    }
    return mapping.get(key)


class _TableTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_tr = False
        self._in_td_or_th = False
        self._cell_buf: List[str] = []
        self._row: List[str] = []
        self.rows: List[List[str]] = []

    def handle_starttag(self, tag: str, attrs):
        if tag == "tr":
            self._in_tr = True
            self._row = []
        elif self._in_tr and tag in ("td", "th"):
            self._in_td_or_th = True
            self._cell_buf = []
        elif self._in_tr and self._in_td_or_th and tag == "img":
            # The wiki often uses icons for data types; those appear as <img alt="Boolean">.
            attr_map = {k.lower(): v for (k, v) in attrs}
            alt = (attr_map.get("alt") or "").strip()
            title = (attr_map.get("title") or "").strip()
            text = alt or title
            if text:
                self._cell_buf.append(" " + text + " ")
        elif self._in_tr and self._in_td_or_th and tag == "br":
            self._cell_buf.append(" ")

    def handle_endtag(self, tag: str):
        if tag == "tr" and self._in_tr:
            self._in_tr = False
            if any(cell.strip() for cell in self._row):
                self.rows.append([cell.strip() for cell in self._row])
        elif self._in_tr and tag in ("td", "th") and self._in_td_or_th:
            self._in_td_or_th = False
            cell_text = unescape("".join(self._cell_buf))
            # Collapse whitespace
            cell_text = re.sub(r"\s+", " ", cell_text).strip()
            self._row.append(cell_text)

    def handle_data(self, data: str):
        if self._in_tr and self._in_td_or_th:
            self._cell_buf.append(data)


def _extract_first_table_after_anchor(html: str, anchor_id: str) -> Optional[str]:
    """Return the raw HTML for the first <table> after a heading anchor id."""
    anchor_pos = html.find(f'id="{anchor_id}"')
    if anchor_pos == -1:
        return None
    table_start = html.find("<table", anchor_pos)
    if table_start == -1:
        return None
    table_end = html.find("</table>", table_start)
    if table_end == -1:
        return None
    return html[table_start : table_end + len("</table>")]


def _find_anchor_pos(html: str, anchor_id: str, *, start_pos: int = 0) -> Optional[int]:
    m = re.search(rf"id=[\"']{re.escape(anchor_id)}[\"']", html[start_pos:])
    if not m:
        return None
    return start_pos + m.start()


def _extract_first_table_after_anchor_prefix(
    html: str,
    anchor_prefix: str,
    *,
    start_pos: int = 0,
) -> Optional[str]:
    """Return the raw HTML for the first <table> after an anchor id prefix.

    This is useful for pages where the same section repeats, and MediaWiki
    disambiguates anchors with suffixes like Data_Parameters_3.
    """

    m = re.search(
        rf"id=[\"']{re.escape(anchor_prefix)}(?:_[0-9]+)?[\"']",
        html[start_pos:],
    )
    if not m:
        return None
    anchor_pos = start_pos + m.start()
    table_start = html.find("<table", anchor_pos)
    if table_start == -1:
        return None
    table_end = html.find("</table>", table_start)
    if table_end == -1:
        return None
    return html[table_start : table_end + len("</table>")]


def _extract_first_table_after_any_anchor_prefix(
    html: str,
    anchor_prefixes: Iterable[str],
    *,
    start_pos: int = 0,
) -> Optional[str]:
    """Try multiple anchor prefixes and return the first matching table."""

    for prefix in anchor_prefixes:
        table = _extract_first_table_after_anchor_prefix(html, prefix, start_pos=start_pos)
        if table:
            return table
    return None


def _parse_io_table(table_html: str) -> List[IoField]:
    parser = _TableTextExtractor()
    parser.feed(table_html)
    rows = parser.rows
    if not rows:
        return []

    # Header row can be th-based or td-based; accept both.
    header = [c.lower() for c in rows[0]]

    def col_index(*candidates: str) -> Optional[int]:
        for cand in candidates:
            if cand.lower() in header:
                return header.index(cand.lower())
        return None

    name_i = col_index("parameter name", "output name", "name")
    type_i = col_index("data type", "type")
    access_i = col_index("access")
    desc_i = col_index("description", "desc")

    if name_i is None or type_i is None:
        # Can't reliably parse.
        return []

    # Some pages (via Template:Data_Parameters) include enumerated/value rows such as:
    #   | 0 | Off |
    #   | 1 | On |
    # These are not IO fields; skip them.
    # Also skip rows where the parsed type isn't a known primitive.
    allowed_types = {"boolean", "integer", "float", "double", "string"}

    fields: List[IoField] = []
    for r in rows[1:]:
        if name_i >= len(r) or type_i >= len(r):
            continue
        name = r[name_i].strip()
        if not name:
            continue
        if re.fullmatch(r"[0-9]+", name):
            continue

        name = _normalize_field_name(name)

        t = _normalize_type(r[type_i])
        if t not in allowed_types:
            inferred = _infer_type_from_name(name) if not t else None
            if inferred and inferred in allowed_types:
                t = inferred
            else:
                continue

        desc = r[desc_i].strip() if desc_i is not None and desc_i < len(r) else ""
        fields.append(IoField(name=name, type=t, description=desc))

    return fields


def _parse_data_parameters_table(table_html: str) -> tuple[List[IoField], List[IoField]]:
    """Parse a 'Data Parameters' table.

    If an Access column exists (Read / Write / Read Write), split fields into:
      - parameters: writable
      - outputs: readable
    Otherwise, return all fields as parameters.
    """

    parser = _TableTextExtractor()
    parser.feed(table_html)
    rows = parser.rows
    if not rows:
        return [], []

    header = [c.lower() for c in rows[0]]

    def col_index(*candidates: str) -> Optional[int]:
        for cand in candidates:
            if cand.lower() in header:
                return header.index(cand.lower())
        return None

    name_i = col_index("parameter name", "name")
    type_i = col_index("data type", "type")
    access_i = col_index("access")
    desc_i = col_index("description", "desc")

    if name_i is None or type_i is None:
        return [], []

    allowed_types = {"boolean", "integer", "float", "double", "string"}
    params: List[IoField] = []
    outs: List[IoField] = []

    for r in rows[1:]:
        if name_i >= len(r) or type_i >= len(r):
            continue
        name = r[name_i].strip()
        if not name or re.fullmatch(r"[0-9]+", name):
            continue

        name = _normalize_field_name(name)

        t = _normalize_type(r[type_i])
        if t not in allowed_types:
            inferred = _infer_type_from_name(name) if not t else None
            if inferred and inferred in allowed_types:
                t = inferred
            else:
                continue

        desc = r[desc_i].strip() if desc_i is not None and desc_i < len(r) else ""
        field = IoField(name=name, type=t, description=desc)

        if access_i is None or access_i >= len(r):
            # No access column: treat as writable parameters.
            params.append(field)
            continue

        access = r[access_i].strip().lower()
        is_read = "read" in access
        is_write = "write" in access
        if is_write:
            params.append(field)
        if is_read:
            outs.append(field)

    return params, outs


def _extract_identity(
    html: str,
    *,
    start_pos: int = 0,
    end_pos: Optional[int] = None,
    prefer_name: Optional[str] = None,
) -> tuple[Optional[str], Optional[int]]:
    """Extract Item/Prefab Name+Hash from a page (or a page subsection).

    MediaWiki markup varies; matching against tag structure is fragile.
    Instead we strip to visible text and regex that.

    If Item Name/Hash are not present, fall back to Prefab Name/Hash.
    """

    class _TextOnly(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.parts: List[str] = []

        def handle_data(self, data: str) -> None:
            if data:
                self.parts.append(data)

    snippet = html[start_pos:end_pos]

    p = _TextOnly()
    p.feed(snippet)
    text = unescape(" ".join(p.parts))
    text = re.sub(r"\s+", " ", text)

    item_name: Optional[str] = None
    item_hash: Optional[int] = None

    def last_int(pattern: str) -> Optional[int]:
        ms = list(re.finditer(pattern, text, re.IGNORECASE))
        if not ms:
            return None
        try:
            return int(ms[-1].group(1))
        except ValueError:
            return None

    def last_str(pattern: str) -> Optional[str]:
        ms = list(re.finditer(pattern, text, re.IGNORECASE))
        if not ms:
            return None
        return ms[-1].group(1)

    # If the caller knows the exact prefab/item name we should be extracting,
    # try to bind the corresponding hash/name pair first.
    if prefer_name:
        # Prefer prefab identity; many structure pages list Prefab Name/Hash.
        # On multi-device pages (e.g., Sensors) multiple infobox tables can sit
        # back-to-back, so we anchor on the specific "Prefab Name <prefer_name>"
        # occurrence and then pick the nearest preceding Prefab Hash.
        pref_name_pat = re.compile(
            rf"\bPrefab\s+Name\b\s+{re.escape(prefer_name)}\b",
            re.IGNORECASE,
        )
        pref_hash_pat = re.compile(r"\bPrefab\s+Hash\b\s+([0-9-]+)\b", re.IGNORECASE)

        best_hash: Optional[int] = None
        best_distance: Optional[int] = None
        for m_name in pref_name_pat.finditer(text):
            pos = m_name.start()
            lookback = text[max(0, pos - 1500) : pos]
            hashes = list(pref_hash_pat.finditer(lookback))
            if not hashes:
                continue
            m_hash = hashes[-1]
            try:
                h = int(m_hash.group(1))
            except ValueError:
                h = None
            # Distance from the hash label to the name label; smaller is better.
            dist = pos - (max(0, pos - 1500) + m_hash.start())
            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_hash = h

        if best_distance is not None:
            return prefer_name, best_hash

        # Some pages use Item Name/Hash instead.
        item_name_pat = re.compile(
            rf"\bItem\s+Name\b\s+{re.escape(prefer_name)}\b",
            re.IGNORECASE,
        )
        item_hash_pat = re.compile(r"\bItem\s+Hash\b\s+([0-9-]+)\b", re.IGNORECASE)

        best_hash = None
        best_distance = None
        for m_name in item_name_pat.finditer(text):
            pos = m_name.start()
            lookback = text[max(0, pos - 1500) : pos]
            hashes = list(item_hash_pat.finditer(lookback))
            if not hashes:
                continue
            m_hash = hashes[-1]
            try:
                h = int(m_hash.group(1))
            except ValueError:
                h = None
            dist = pos - (max(0, pos - 1500) + m_hash.start())
            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_hash = h

        if best_distance is not None:
            return prefer_name, best_hash

    # The Pipe_Analyzer page (and similar) typically contains:
    #   "Item Hash 435685051" and "Item Name StructurePipeAnalysizer"
    item_hash = last_int(r"\bItem\s+Hash\b\s+([0-9-]+)\b")
    item_name = last_str(r"\bItem\s+Name\b\s+([A-Za-z0-9_]+)\b")

    if item_name is None and item_hash is None:
        # Multi-device pages sometimes only list Prefab Name/Hash.
        item_hash = last_int(r"\bPrefab\s+Hash\b\s+([0-9-]+)\b")
        item_name = last_str(r"\bPrefab\s+Name\b\s+([A-Za-z0-9_]+)\b")

    return item_name, item_hash


def fetch_html(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "stationeers_IC10-wiki-import/0.1 (text-based IC10 IDE tooling)"
        },
    )
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
    # Let Python guess; MediaWiki is typically UTF-8.
    return raw.decode("utf-8", errors="replace")


def _with_query(url: str, *, query: str) -> str:
    """Return url with the given query string.

    If the URL already contains a query, it will be replaced.
    """

    parsed = urlparse(url)
    return parsed._replace(query=query).geturl()


def _extract_transcluded_data_network_title(edit_html: str) -> Optional[str]:
    """Try to find a transcluded */Data_Network page title from edit view HTML.

    Many device pages don't embed the IO tables directly; instead they include a
    collapsible transclusion like:
      {{:Kit_(Satellite_Dish)/Data_Network}}

    This function is intentionally permissive and only returns the first match.
    """

    # The edit page HTML contains the raw wikitext inside the form.
    # Look for a transclusion that ends with /Data_Network.
    m = re.search(r"\{\{\s*:\s*([^\}|\n]+?/Data_Network)\s*\}\}", edit_html)
    if not m:
        return None
    return m.group(1).strip()


def upsert_index(entry: dict) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INDEX_PATH.exists():
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "devices": []}

    devices = data.setdefault("devices", [])
    # Replace by wikiTitle
    devices = [d for d in devices if d.get("wikiTitle") != entry.get("wikiTitle")]
    devices.append(entry)
    devices.sort(key=lambda d: d.get("wikiTitle", ""))
    data["devices"] = devices

    INDEX_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python tools/wiki_import.py <stationeers-wiki device URL>")
        print("  Tip: for multi-device pages, you can import a specific section:")
        print("    python tools/wiki_import.py https://stationeers-wiki.com/Sensors#Gas_Sensor")
        return 2

    url = argv[1]
    wiki_title, fetch_url, fragment = _parse_wiki_url(url)

    html = fetch_html(fetch_url)

    section_start_pos: Optional[int] = None
    if fragment:
        section_start_pos = _find_anchor_pos(html, fragment)

    if section_start_pos is not None:
        parameters_table = _extract_first_table_after_anchor_prefix(
            html, "Data_Parameters", start_pos=section_start_pos
        )
        outputs_table = _extract_first_table_after_anchor_prefix(
            html, "Data_Outputs", start_pos=section_start_pos
        )
    else:
        parameters_table = _extract_first_table_after_anchor(html, "Data_Parameters")
        outputs_table = _extract_first_table_after_anchor(html, "Data_Outputs")

    params: List[IoField] = []
    outs: List[IoField] = []

    if parameters_table:
        p, o = _parse_data_parameters_table(parameters_table)
        params.extend(p)
        outs.extend(o)

    # If a page also has a separate Data Outputs table, merge it in.
    if outputs_table:
        outs.extend(_parse_io_table(outputs_table))

    # Some pages (e.g. Satellite Dish variants) do not use the Data_Parameters /
    # Data_Outputs anchors. Instead they render IO under:
    #   "Input Data (Write)" and "Output Data (Read)"
    # Often this content is transcluded from a */Data_Network page.
    if not params and not outs:
        # MediaWiki encodes parentheses in ids as .28 and .29.
        input_table = _extract_first_table_after_any_anchor_prefix(
            html,
            ["Input_Data_(Write)", "Input_Data_.28Write.29"],
        )
        output_table = _extract_first_table_after_any_anchor_prefix(
            html,
            ["Output_Data_(Read)", "Output_Data_.28Read.29"],
        )
        if input_table:
            params.extend(_parse_io_table(input_table))
        if output_table:
            outs.extend(_parse_io_table(output_table))

    if not params and not outs:
        # Attempt to follow a transclusion to */Data_Network by grabbing the edit view.
        try:
            edit_html = fetch_html(_with_query(fetch_url, query="action=edit"))
        except Exception:
            edit_html = ""

        dn_title = _extract_transcluded_data_network_title(edit_html) if edit_html else None
        if dn_title:
            # Fetch the transcluded page and parse its Input/Output tables.
            dn_url = f"https://stationeers-wiki.com/{dn_title}"
            dn_html = fetch_html(dn_url)
            input_table = _extract_first_table_after_any_anchor_prefix(
                dn_html,
                ["Input_Data_(Write)", "Input_Data_.28Write.29"],
            )
            output_table = _extract_first_table_after_any_anchor_prefix(
                dn_html,
                ["Output_Data_(Read)", "Output_Data_.28Read.29"],
            )
            if input_table:
                params.extend(_parse_io_table(input_table))
            if output_table:
                outs.extend(_parse_io_table(output_table))

    if section_start_pos is not None:
        # For multi-device pages (e.g., Sensors), we can usually derive the Prefab Name.
        # Example: "Gas_Sensor" section corresponds to prefab "StructureGasSensor".
        expected_prefab = "Structure" + fragment.replace("_", "") if fragment else None

        # Try the whole page first so we catch identity fields in the infobox area.
        item_name, item_hash = _extract_identity(html, prefer_name=expected_prefab)

        # Fallback: scan a window around the section anchor.
        if item_name is None and item_hash is None:
            item_name, item_hash = _extract_identity(
                html,
                start_pos=max(0, section_start_pos - 250_000),
                end_pos=section_start_pos + 250_000,
                prefer_name=expected_prefab,
            )
    else:
        item_name, item_hash = _extract_identity(html)

    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    device = DeviceCatalogEntry(
        source={
            "wikiUrl": url,
            "wikiTitle": wiki_title,
            "retrievedAt": retrieved_at,
        },
        identity={
            "itemName": item_name,
            "itemHash": item_hash,
        },
        io={
            "parameters": [asdict(f) for f in _dedupe_fields(params)],
            "outputs": [asdict(f) for f in _dedupe_fields(outs)],
        },
    )

    DEVICES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DEVICES_DIR / f"{wiki_title}.json"
    out_path.write_text(json.dumps(asdict(device), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    upsert_index(
        {
            "wikiTitle": wiki_title,
            "file": f"devices/{wiki_title}.json",
            "itemName": item_name,
            "itemHash": item_hash,
        }
    )

    print(f"Wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
