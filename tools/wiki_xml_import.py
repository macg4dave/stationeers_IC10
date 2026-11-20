"""Import device IO tables from a Stationeers wiki Special:Export XML dump.

Why
- stationeers-wiki.com sits behind a Cloudflare browser challenge, so
  tools/wiki_import.py can no longer fetch pages directly.
- A player can export pages from their own browser via
  https://stationeers-wiki.com/Special:Export ("Include templates" ticked)
  and save the .xml into the repo (e.g. temp/).

What it reads (wikitext, not rendered HTML)
- New style:  {{Data Parameters| {{Data Parameters/row|Name|Type|Desc|r=0|w=0|multiple=N|v|label...}} }}
- Old style:  {{Data Parameters}} / {{Data Outputs}} followed by a plain {| wikitable |}
- "Mode Values" tables -> io.modeValues
- Structurebox / Itembox prefab name + hash -> identity

Usage
  python tools/wiki_xml_import.py temp/export.xml            # compare only (default)
  python tools/wiki_xml_import.py temp/export.xml --write    # update catalog/devices/*.json

Merge policy (the game is Early Access and the wiki lags behind it)
- Additive only: new fields / Mode values are added; existing catalog fields are
  never removed. Fields the wiki lacks are reported as "not on wiki (kept)".
- Known in-game renames are applied to wiki names before comparing
  (the game replaced Volatiles with Methane; many wiki tables are stale).
- Identity is only taken from a Structurebox whose name matches the device,
  or the page's single Structurebox; otherwise the catalog identity is kept.
- Curated fields (source.kind/notes, settingInterpretation text) are preserved.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DEVICES_DIR = ROOT / "catalog" / "devices"
INDEX_PATH = ROOT / "catalog" / "index.json"

# Wiki name -> current in-game LogicType name (wiki tables are often stale).
RENAMES = {
    "RatioVolatiles": "RatioMethane",
    "RatioLiquidVolatiles": "RatioLiquidMethane",
    "RatioVolatilesInput": "RatioMethaneInput",
    "RatioVolatilesInput2": "RatioMethaneInput2",
    "RatioVolatilesOutput": "RatioMethaneOutput",
    "RatioVolatilesOutput2": "RatioMethaneOutput2",
    "RatioLiquidVolatilesInput": "RatioLiquidMethaneInput",
    "RatioLiquidVolatilesInput2": "RatioLiquidMethaneInput2",
    "RatioLiquidVolatilesOutput": "RatioLiquidMethaneOutput",
    "RatioLiquidVolatilesOutput2": "RatioLiquidMethaneOutput2",
}


# --------------------------------------------------------------------------- XML


def load_export(path: Path) -> Dict[str, Tuple[str, str]]:
    """Return {page title: (revision timestamp, wikitext)}."""
    root = ET.parse(path).getroot()
    ns = {"m": root.tag.split("}")[0][1:]} if root.tag.startswith("{") else {"m": ""}
    pages: Dict[str, Tuple[str, str]] = {}
    for page in root.findall("m:page", ns):
        title = page.find("m:title", ns).text or ""
        rev = page.find("m:revision", ns)
        ts = rev.find("m:timestamp", ns).text or ""
        text = rev.find("m:text", ns).text or ""
        pages[title] = (ts, text)
    return pages


# ---------------------------------------------------------------- wikitext utils


def find_templates(text: str, name: str) -> List[Tuple[int, int, str]]:
    """Find {{name ...}} with brace matching. Returns (start, end, inner)."""
    out = []
    pat = re.compile(r"\{\{\s*" + re.escape(name) + r"\s*(?=[|}\n])", re.I)
    for m in pat.finditer(text):
        depth, i = 0, m.start()
        while i < len(text) - 1:
            two = text[i : i + 2]
            if two == "{{":
                depth += 1
                i += 2
                continue
            if two == "}}":
                depth -= 1
                i += 2
                if depth == 0:
                    out.append((m.start(), i, text[m.start() + 2 : i - 2]))
                    break
                continue
            i += 1
    return out


def split_params(inner: str) -> Tuple[List[str], Dict[str, str]]:
    """Split template body on top-level '|'. Returns (positional, named)."""
    parts, buf, depth_c, depth_s, i = [], [], 0, 0, 0
    while i < len(inner):
        two = inner[i : i + 2]
        if two == "{{":
            depth_c += 1; buf.append(two); i += 2; continue
        if two == "}}":
            depth_c -= 1; buf.append(two); i += 2; continue
        if two == "[[":
            depth_s += 1; buf.append(two); i += 2; continue
        if two == "]]":
            depth_s -= 1; buf.append(two); i += 2; continue
        ch = inner[i]
        if ch == "|" and depth_c == 0 and depth_s == 0:
            parts.append("".join(buf)); buf = []
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    parts = parts[1:]  # drop template name
    pos, named = [], {}
    for p in parts:
        m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_ ]*?)\s*=(.*)\Z", p, re.S)
        if m:
            named[m.group(1).strip()] = m.group(2).strip()
        else:
            pos.append(p.strip())
    return pos, named


def clean(s: str) -> str:
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", s)
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"</?[a-zA-Z][^>]*>", "", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = s.replace("'''", "").replace("''", "")
    s = s.replace("&#176;", "°").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def first_table_after(text: str, pos: int) -> Optional[str]:
    start = text.find("{|", pos)
    if start < 0:
        return None
    # do not run past the next heading/template block that clearly starts a new section
    nxt = re.search(r"\{\{\s*Data (Parameters|Outputs)\s*\}\}", text[pos + 5 : start])
    if nxt:
        return None
    end = text.find("\n|}", start)
    if end < 0:
        end = text.find("|}", start)
    return text[start : end + 3] if end >= 0 else None


def table_rows(table: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for chunk in re.split(r"\n\s*\|-[^\n]*", table):
        cells: List[str] = []
        for line in chunk.split("\n"):
            line = line.strip()
            if not line or line.startswith("{|") or line.startswith("|}") or line.startswith("!"):
                continue
            if line.startswith("|"):
                cells.extend(c.strip() for c in line[1:].split("||"))
            elif cells:
                cells[-1] += " " + line
        if cells:
            rows.append(cells)
    return rows


# --------------------------------------------------------------------- sections


def section_text(text: str, fragment: str) -> Optional[str]:
    """Slice a multi-device page to the heading matching a URL fragment."""
    want = unquote(fragment).replace("_", " ").lower()
    heads = list(re.finditer(r"^(=+)\s*(.+?)\s*\1\s*$", text, re.M))
    for i, h in enumerate(heads):
        label = clean(h.group(2)).lower()
        if want == label or want in label:
            lvl = len(h.group(1))
            end = len(text)
            for h2 in heads[i + 1 :]:
                if len(h2.group(1)) <= lvl:
                    end = h2.start()
                    break
            return text[h.start() : end]
    return None


# ------------------------------------------------------------------- extraction


def norm_type(t: str) -> str:
    t = clean(t).lower()
    return {"bool": "boolean", "int": "integer"}.get(t, t)


def extract(text: str) -> dict:
    params: List[dict] = []
    outs: List[dict] = []
    modes: List[dict] = []

    # New style row templates.
    for _, _, inner in find_templates(text, "Data Parameters/row"):
        pos, named = split_params(inner)
        if not pos:
            continue
        name = clean(pos[0])
        typ = norm_type(pos[1]) if len(pos) > 1 else ""
        desc = clean(pos[2]) if len(pos) > 2 else ""
        field = {"name": name, "type": typ, "description": desc}
        if named.get("w", "") != "0":
            params.append(field)
        if named.get("r", "") != "0":
            outs.append(dict(field))
        if name == "Mode" and named.get("multiple"):
            pairs = pos[3:]
            for v, lab in zip(pairs[0::2], pairs[1::2]):
                try:
                    val = int(clean(v))
                except ValueError:
                    continue
                modes.append({"value": val, "meaning": clean(lab)})

    # Old style: {{Data Parameters}} + table, {{Data Outputs}} + table.
    for m in re.finditer(r"\{\{\s*Data Parameters\s*\}\}", text):
        tbl = first_table_after(text, m.end())
        for cells in table_rows(tbl or ""):
            if len(cells) >= 2:
                params.append({"name": clean(cells[0]), "type": norm_type(cells[1]),
                               "description": clean(cells[2]) if len(cells) > 2 else ""})
    for m in re.finditer(r"\{\{\s*Data Outputs\s*\}\}", text):
        tbl = first_table_after(text, m.end())
        for cells in table_rows(tbl or ""):
            if len(cells) >= 2:
                outs.append({"name": clean(cells[0]), "type": norm_type(cells[1]),
                             "description": clean(cells[2]) if len(cells) > 2 else ""})

    # Explicit Mode Values table beats the row-template enum (richer meanings).
    mv = re.search(r"^=+\s*Mode Values\s*=+\s*$", text, re.M)
    if mv:
        tbl = first_table_after(text, mv.end())
        table_modes = []
        for cells in table_rows(tbl or ""):
            try:
                mode = {"value": int(clean(cells[0])), "meaning": clean(cells[1])}
            except (ValueError, IndexError):
                continue
            if len(cells) > 2 and clean(cells[2]):
                mode["settingInterpretation"] = clean(cells[2])
            table_modes.append(mode)
        if table_modes:
            modes = table_modes

    return {"parameters": dedupe(params), "outputs": dedupe(outs), "modeValues": modes}


def dedupe(fields: List[dict]) -> List[dict]:
    seen, out = set(), []
    for f in fields:
        f["name"] = RENAMES.get(f["name"], f["name"])
        if f["name"] and f["name"] not in seen:
            seen.add(f["name"])
            out.append(f)
    return out


def identity(text: str, prefer: str) -> Tuple[Optional[str], Optional[int]]:
    """Structure prefab name/hash for the device, or (None, None) if unsure.

    IC10 batch ops target the placed structure, so Itembox (kit) hashes are
    ignored. A Structurebox is used only if its name matches `prefer`, or it is
    the only Structurebox on the page.
    """
    boxes = []
    for _, _, inner in find_templates(text, "Structurebox"):
        _, named = split_params(inner)
        phash = named.get("prefab_hash") or named.get("prefabhash")
        try:
            h = int(clean(phash)) if phash else None
        except ValueError:
            h = None
        pname = clean(named.get("prefab_name") or named.get("prefabname") or "") or None
        boxes.append((clean(named.get("name", "")).lower(), pname, h))
    want = prefer.lower().replace("kit (", "").rstrip(")")
    match = [b for b in boxes if b[0] in (prefer.lower(), want)]
    pick = match[0] if match else (boxes[0] if len(boxes) == 1 else None)
    if not pick or pick[2] is None:
        return None, None
    return pick[1], pick[2]


# ---------------------------------------------------------------------- mapping


def page_for(entry: dict, pages: dict) -> Tuple[Optional[str], Optional[str]]:
    src = entry.get("source", {})
    url = src.get("wikiUrl") or ""
    title = (src.get("wikiTitle") or "").replace("_", " ")
    m = re.search(r"stationeers-wiki\.com/(?:index\.php\?title=)?([^#?]+)(?:#(.+))?", url)
    if m:
        page = unquote(m.group(1)).replace("_", " ")
        frag = m.group(2)
        if title in pages and title != page and not frag:
            return title, None
        return page, frag
    if title in pages:
        return title, None
    return None, None


def names(fields: List[dict]) -> List[str]:
    return [f["name"] for f in fields]


def key(name: str) -> str:
    return name.lower().replace(" ", "")


def diff_names(old: List[str], new: List[str]) -> Tuple[List[str], List[str]]:
    lo = {key(n): n for n in old}
    ln = {key(n): n for n in new}
    added = [ln[k] for k in ln if k not in lo]
    removed = [lo[k] for k in lo if k not in ln]
    return added, removed


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("xml", type=Path)
    ap.add_argument("--write", action="store_true", help="update catalog files")
    args = ap.parse_args(argv)

    pages = load_export(args.xml)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    changed = 0

    for fp in sorted(DEVICES_DIR.glob("*.json")):
        entry = json.loads(fp.read_text(encoding="utf-8"))
        page, frag = page_for(entry, pages)
        tag = fp.stem
        if not page or page not in pages:
            print(f"[missing ] {tag}  (page {page!r} not in export)")
            continue
        ts, text = pages[page]
        if not frag:
            # Multi-device pages (e.g. Console + LED Display): use the top-level
            # "= ... =" section that names this device, if there is one.
            title = page.lower()
            for h in re.finditer(r"^=\s*([^=\n]+?)\s*=\s*$", text, re.M):
                if title in clean(h.group(1)).lower():
                    frag = clean(h.group(1))
                    break
        body = section_text(text, frag) if frag else text
        if body is None:
            print(f"[nosect  ] {tag}  (section #{frag} not found in {page!r})")
            continue
        new = extract(body)
        if not new["parameters"] and not new["outputs"]:
            print(f"[no-io   ] {tag}  ({page}{'#' + frag if frag else ''}, wiki edited {ts[:10]})")
            continue

        io = entry.get("io", {})
        stale = [f["name"] for k in ("parameters", "outputs") for f in io.get(k, [])
                 if f["name"] in RENAMES]
        io["parameters"] = renamed(io.get("parameters", []))
        io["outputs"] = renamed(io.get("outputs", []))
        kind = entry.get("source", {}).get("kind", "wiki_import")
        pa, pr = diff_names(names(io.get("parameters", [])), names(new["parameters"]))
        oa, orr = diff_names(names(io.get("outputs", [])), names(new["outputs"]))
        prefer = frag.replace("_", " ") if frag else page
        if kind == "best_guess" and (src_title := entry["source"].get("wikiTitle", "")):
            prefer = src_title.replace("_", " ")
        iname, ihash = identity(body, prefer=prefer)
        old_id = entry.get("identity", {})
        # itemName/itemHash keep their existing meaning (often the kit); the
        # placed structure's prefab, which IC10 batch ops need, is stored beside it.
        id_change = (ihash is not None and ihash != old_id.get("itemHash")
                     and ihash != old_id.get("structureHash"))
        old_modes = {m["value"] for m in io.get("modeValues", [])}
        add_modes = [m for m in new["modeValues"] if m["value"] not in old_modes]

        any_change = pa or oa or id_change or add_modes or stale
        status = "CHANGED " if any_change else "same    "
        print(f"[{status}] {tag}  ({page}{'#' + frag if frag else ''}, wiki edited {ts[:10]}"
              f"{', ' + kind if kind != 'wiki_import' else ''})")
        if stale: print(f"      renamed (Volatiles->Methane): {', '.join(stale)}")
        if pa: print(f"      + write: {', '.join(pa)}")
        if oa: print(f"      + read : {', '.join(oa)}")
        if id_change:
            print(f"      + structure: {iname} {ihash}  (item stays {old_id.get('itemName')} "
                  f"{old_id.get('itemHash')})")
        if add_modes:
            print("      + modes: " + ", ".join(f"{m['value']}={m['meaning']}" for m in add_modes))
        if pr: print(f"      ~ write not on wiki (kept): {', '.join(pr)}")
        if orr: print(f"      ~ read  not on wiki (kept): {', '.join(orr)}")

        if args.write and any_change:
            changed += 1
            src = entry.setdefault("source", {})
            src["retrievedAt"] = now
            src["exportRevision"] = ts
            if id_change:
                entry.setdefault("identity", {}).update(
                    {"structureName": iname, "structureHash": ihash})
            io["parameters"] = merge(io.get("parameters", []), new["parameters"])
            io["outputs"] = merge(io.get("outputs", []), new["outputs"])
            if add_modes:
                io["modeValues"] = sorted(io.get("modeValues", []) + add_modes,
                                          key=lambda m: m["value"])
            # keep modeValues first, as in existing files
            entry["io"] = {k: io[k] for k in ("modeValues", "parameters", "outputs") if k in io}
            fp.write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")

    if args.write:
        print(f"\nUpdated {changed} catalog file(s).")
    return 0


def renamed(fields: List[dict]) -> List[dict]:
    """Apply known in-game renames to existing catalog fields (drop dup results)."""
    out, seen = [], set()
    for f in fields:
        f = {**f, "name": RENAMES.get(f["name"], f["name"])}
        if f["name"].lower() not in seen:
            seen.add(f["name"].lower())
            out.append(f)
    return out


def merge(old: List[dict], new: List[dict]) -> List[dict]:
    """Keep every existing field; append wiki fields not already present."""
    old = renamed(old)
    have = {key(f["name"]) for f in old}
    return old + [f for f in new if key(f["name"]) not in have]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
