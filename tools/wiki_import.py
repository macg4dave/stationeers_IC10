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


def _slug_from_wiki_url(url: str) -> str:
    # stationeers-wiki.com/<Title>
    m = re.search(r"stationeers-wiki\.com/(?P<title>[^?#/]+)", url)
    if not m:
        raise ValueError(f"Unsupported wiki URL format: {url}")
    return m.group("title")


def _normalize_type(type_str: str) -> str:
    t = type_str.strip().lower()
    # wiki sometimes uses bool/boolean or integer/int
    t = {"bool": "boolean", "int": "integer"}.get(t, t)
    return t


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
    desc_i = col_index("description", "desc")

    if name_i is None or type_i is None:
        # Can't reliably parse.
        return []

    fields: List[IoField] = []
    for r in rows[1:]:
        if name_i >= len(r) or type_i >= len(r):
            continue
        name = r[name_i].strip()
        if not name:
            continue
        t = _normalize_type(r[type_i])
        desc = r[desc_i].strip() if desc_i is not None and desc_i < len(r) else ""
        fields.append(IoField(name=name, type=t, description=desc))

    return fields


def _extract_identity(html: str) -> tuple[Optional[str], Optional[int]]:
    """Extract Item Name/Item Hash from the page.

    MediaWiki markup varies; matching against tag structure is fragile.
    Instead we strip to visible text and regex that.
    """

    class _TextOnly(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.parts: List[str] = []

        def handle_data(self, data: str) -> None:
            if data:
                self.parts.append(data)

    p = _TextOnly()
    p.feed(html)
    text = unescape(" ".join(p.parts))
    text = re.sub(r"\s+", " ", text)

    item_name: Optional[str] = None
    item_hash: Optional[int] = None

    # The Pipe_Analyzer page (and similar) typically contains:
    #   "Item Hash 435685051" and "Item Name StructurePipeAnalysizer"
    m_hash = re.search(r"\bItem\s+Hash\b\s+([0-9-]+)\b", text, re.IGNORECASE)
    if m_hash:
        try:
            item_hash = int(m_hash.group(1))
        except ValueError:
            item_hash = None

    m_name = re.search(r"\bItem\s+Name\b\s+([A-Za-z0-9_]+)\b", text, re.IGNORECASE)
    if m_name:
        item_name = m_name.group(1)

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
        return 2

    url = argv[1]
    wiki_title = _slug_from_wiki_url(url)

    html = fetch_html(url)

    parameters_table = _extract_first_table_after_anchor(html, "Data_Parameters")
    outputs_table = _extract_first_table_after_anchor(html, "Data_Outputs")

    params = _parse_io_table(parameters_table) if parameters_table else []
    outs = _parse_io_table(outputs_table) if outputs_table else []

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
            "parameters": [asdict(f) for f in params],
            "outputs": [asdict(f) for f in outs],
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
