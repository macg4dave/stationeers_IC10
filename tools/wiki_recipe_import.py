"""Import Stationeers wiki fabricator recipe tables into a local recipe catalog.

Goal
- Given a Stationeers wiki recipes URL (for example
  https://stationeers-wiki.com/Autolathe/Recipes), extract the recipe table and
  write a device-scoped recipe catalog under catalog/recipes/<Producer>/.

Design constraints
- No external dependencies (stdlib only).
- Best-effort parsing: the wiki is community-maintained and recipe tables are
  not guaranteed to stay perfectly uniform.

Usage
  python tools/wiki_recipe_import.py https://stationeers-wiki.com/Autolathe/Recipes
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

from wiki_import import _extract_identity, fetch_html


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
DEVICES_DIR = CATALOG_DIR / "devices"
RECIPES_DIR = CATALOG_DIR / "recipes"
RECIPES_INDEX_PATH = RECIPES_DIR / "index.json"


@dataclass
class RecipeMaterial:
    wikiTitle: str
    displayName: str
    quantity: int | float


@dataclass
class RecipeItem:
    wikiTitle: str
    displayName: str
    itemName: str | None
    itemHash: int | None


@dataclass
class ItemPageMetadata:
    itemName: str | None
    itemHash: int | None
    stackSize: int | None


@dataclass
class RecipeRecord:
    item: RecipeItem
    tier: str
    time: int | float
    energy: int | float
    inputs: list[RecipeMaterial]
    stackSize: int = 1


@dataclass
class RecipeCatalogEntry:
    source: dict[str, Any]
    producer: dict[str, Any]
    recipes: list[dict[str, Any]]


def _parse_recipe_url(url: str) -> tuple[str, str, str]:
    """Return (page_title, canonical_url, producer_title)."""

    parsed = urlparse(url)
    if "stationeers-wiki.com" not in parsed.netloc:
        raise ValueError(f"Unsupported wiki URL host: {url}")

    page_title: Optional[str] = None
    path = (parsed.path or "/").lstrip("/")
    if path.lower() == "index.php":
        qs = parse_qs(parsed.query)
        titles = qs.get("title")
        if titles:
            page_title = titles[0]
    elif path:
        page_title = path

    if not page_title:
        raise ValueError(f"Unsupported wiki URL format: {url}")

    canonical_url = f"https://stationeers-wiki.com/{page_title}"
    producer_title = page_title[:-len("/Recipes")] if page_title.endswith("/Recipes") else page_title
    return page_title, canonical_url, producer_title


def _build_action_url(page_title: str, action: str) -> str:
    return (
        "https://stationeers-wiki.com/index.php?title="
        f"{quote(page_title, safe='()/:_-')}&action={quote(action, safe='')}"
    )


def _fetch_text(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "stationeers_IC10-wiki-recipe-import/0.1 (text-based IC10 IDE tooling)"
        },
    )
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")


def _extract_textarea(html: str) -> Optional[str]:
    match = re.search(
        r"<textarea[^>]*?(?:id=\"wpTextbox1\"|name=\"wpTextbox1\")[^>]*>(.*?)</textarea>",
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    return unescape(match.group(1))


def fetch_wikitext(page_title: str) -> str:
    raw_url = _build_action_url(page_title, "raw")
    raw_text = _fetch_text(raw_url)
    if raw_text.lstrip().startswith("<!DOCTYPE html"):
        edit_text = _fetch_text(_build_action_url(page_title, "edit"))
        extracted = _extract_textarea(edit_text)
        if not extracted:
            raise RuntimeError(f"Could not extract wikitext from {page_title}")
        return extracted
    return raw_text


def _wiki_title_to_display(wiki_title: str) -> str:
    return wiki_title.replace("_", " ")


def _parse_number(raw_value: str) -> int | float:
    cleaned = raw_value.strip().replace(" ", "").replace(",", ".")
    value = float(cleaned)
    return int(value) if value.is_integer() else value


def _extract_recipe_table(wikitext: str) -> str:
    tables = re.findall(r"\{\|.*?\|\}", wikitext, re.DOTALL)
    for table in tables:
        if "'''Item'''" in table and "'''Tier'''" in table:
            return table
    raise RuntimeError("Could not locate recipe table in wiki source")


def _parse_recipe_item(cell_text: str) -> RecipeItem:
    match = re.search(
        r"'''\[\[(?P<link>[^\]|]+)(?:\|(?P<text>[^\]]+))?\]\]'''",
        cell_text,
    )
    if not match:
        raise RuntimeError(f"Could not parse recipe item cell: {cell_text[:120]!r}")

    wiki_title = match.group("link").strip()
    display_name = (match.group("text") or wiki_title).strip()
    return RecipeItem(wikiTitle=wiki_title, displayName=display_name, itemName=None, itemHash=None)


def _build_page_url(page_title: str) -> str:
    return f"https://stationeers-wiki.com/{quote(page_title, safe='()/:_-')}"


class _TextOnly(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)


def _last_match_int(text: str, pattern: str) -> Optional[int]:
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    if not matches:
        return None
    try:
        return int(matches[-1].group(1))
    except ValueError:
        return None


def _last_match_str(text: str, pattern: str) -> Optional[str]:
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    if not matches:
        return None
    return matches[-1].group(1)


def _parse_stack_size(raw_value: str) -> Optional[int]:
    match = re.search(r"([0-9]+)", raw_value)
    if not match:
        return None
    try:
        stack_size = int(match.group(1))
    except ValueError:
        return None
    return stack_size if stack_size > 0 else None


def _extract_stack_size_from_html(html: str) -> Optional[int]:
    match = re.search(
        r"<th[^>]*>\s*Stacks\s*</th>\s*<td[^>]*>(.*?)</td>",
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    text = re.sub(r"<[^>]+>", " ", match.group(1))
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return _parse_stack_size(text)


def _extract_metadata_from_wikitext(page_title: str, wikitext: str) -> ItemPageMetadata:
    """Fallback identity/stack extraction from raw wiki source for item pages."""

    blocks = re.findall(r"\{\{(?:Itembox|Structurebox).*?\}\}", wikitext, re.IGNORECASE | re.DOTALL)
    if blocks:
        expected_name = page_title.replace("_", " ")
        for block in blocks:
            name_match = re.search(r"\|\s*name\s*=\s*([^|}{\n]+)", block, re.IGNORECASE)
            if name_match and name_match.group(1).strip() != expected_name:
                continue

            item_name_match = re.search(r"\|\s*item_name\s*=\s*([A-Za-z0-9_]+)", block, re.IGNORECASE)
            item_hash_match = re.search(r"\|\s*item_hash\s*=\s*([0-9-]+)", block, re.IGNORECASE)
            prefab_name_match = re.search(r"\|\s*prefab_name\s*=\s*([A-Za-z0-9_]+)", block, re.IGNORECASE)
            prefab_hash_match = re.search(r"\|\s*prefab_hash\s*=\s*([0-9-]+)", block, re.IGNORECASE)
            stacks_match = re.search(r"\|\s*stacks\s*=\s*([^|}{\n]+)", block, re.IGNORECASE)

            item_name = item_name_match.group(1) if item_name_match else None
            prefab_name = prefab_name_match.group(1) if prefab_name_match else None
            stack_size = _parse_stack_size(stacks_match.group(1)) if stacks_match else None

            item_hash: Optional[int]
            prefab_hash: Optional[int]
            try:
                item_hash = int(item_hash_match.group(1)) if item_hash_match else None
            except ValueError:
                item_hash = None
            try:
                prefab_hash = int(prefab_hash_match.group(1)) if prefab_hash_match else None
            except ValueError:
                prefab_hash = None

            if item_name is not None or item_hash is not None:
                return ItemPageMetadata(item_name, item_hash, stack_size)
            if prefab_name is not None or prefab_hash is not None:
                return ItemPageMetadata(prefab_name, prefab_hash, stack_size)

    parser = _TextOnly()
    parser.feed(wikitext)
    text = unescape(" ".join(parser.parts))
    text = re.sub(r"\s+", " ", text)
    stack_size = _last_match_int(text, r"\bStacks\b\s*=?\s*([0-9]+)")

    item_name = _last_match_str(text, r"\bItem(?:_|\s+)Name\b\s*=?\s*([A-Za-z0-9_]+)\b")
    item_hash = _last_match_int(text, r"\bItem(?:_|\s+)Hash\b\s*=?\s*([0-9-]+)\b")
    if item_name is not None or item_hash is not None:
        return ItemPageMetadata(item_name, item_hash, stack_size)

    prefab_name = _last_match_str(text, r"\bPrefab(?:_|\s+)Name\b\s*=?\s*([A-Za-z0-9_]+)\b")
    prefab_hash = _last_match_int(text, r"\bPrefab(?:_|\s+)Hash\b\s*=?\s*([0-9-]+)\b")
    return ItemPageMetadata(prefab_name, prefab_hash, stack_size)


def _lookup_item_metadata(page_title: str, cache: dict[str, ItemPageMetadata]) -> ItemPageMetadata:
    if page_title in cache:
        return cache[page_title]

    page_url = _build_page_url(page_title)
    stack_size: Optional[int] = None
    try:
        html = fetch_html(page_url)
        item_name, item_hash = _extract_identity(html)
        stack_size = _extract_stack_size_from_html(html)
    except Exception:
        item_name, item_hash = None, None

    if item_name is None and item_hash is None or stack_size is None:
        try:
            wikitext = fetch_wikitext(page_title)
            meta = _extract_metadata_from_wikitext(page_title, wikitext)
            if item_name is None and item_hash is None:
                item_name, item_hash = meta.itemName, meta.itemHash
            if stack_size is None:
                stack_size = meta.stackSize
        except Exception:
            pass

    cache[page_title] = ItemPageMetadata(item_name, item_hash, stack_size)
    return cache[page_title]


_TOKEN_RE = re.compile(
    r"\[\[File:[^\]]+\|link=(?P<link>[^\]]+)\]\]\s*"
    r"<div class=\"stationeers-icon-text\">(?P<value>[^<]+)</div>",
    re.IGNORECASE,
)

_ROW_RE = re.compile(
    r"\|-\s*(?:!|\|)\s*(?P<item>.*?)\|\s*'''(?P<tier>Tier[^']+)'''\s*\|\s*(?P<details>.*?)(?=(?:\|-\s*(?:!|\|))|\|\})",
    re.DOTALL,
)


def parse_recipes(wikitext: str) -> list[RecipeRecord]:
    table = _extract_recipe_table(wikitext)
    recipes: list[RecipeRecord] = []
    identity_cache: dict[str, ItemPageMetadata] = {}

    for match in _ROW_RE.finditer(table):
        item = _parse_recipe_item(match.group("item"))
        meta = _lookup_item_metadata(item.wikiTitle, identity_cache)
        item.itemName = meta.itemName
        item.itemHash = meta.itemHash
        tier = re.sub(r"\s+", " ", match.group("tier")).strip()
        details = match.group("details")

        time_value: int | float | None = None
        energy_value: int | float | None = None
        inputs: list[RecipeMaterial] = []

        for token in _TOKEN_RE.finditer(details):
            wiki_title = token.group("link").strip()
            quantity = _parse_number(token.group("value"))
            if wiki_title == "Time":
                time_value = quantity
                continue
            if wiki_title == "Energy":
                energy_value = quantity
                continue
            inputs.append(
                RecipeMaterial(
                    wikiTitle=wiki_title,
                    displayName=_wiki_title_to_display(wiki_title),
                    quantity=quantity,
                )
            )

        if time_value is None or energy_value is None or not inputs:
            raise RuntimeError(
                f"Recipe row for {item.displayName!r} is missing time, energy, or inputs"
            )

        recipes.append(
            RecipeRecord(
                item=item,
                tier=tier,
                time=time_value,
                energy=energy_value,
                inputs=inputs,
                stackSize=meta.stackSize or 1,
            )
        )

    if not recipes:
        raise RuntimeError("No recipes found in wiki table")
    return recipes


def _load_device_identity(producer_title: str) -> tuple[Optional[str], Optional[int]]:
    device_path = DEVICES_DIR / f"{producer_title}.json"
    if not device_path.exists():
        return None, None

    try:
        data = json.loads(device_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, None

    identity = data.get("identity")
    if not isinstance(identity, dict):
        return None, None

    item_name = identity.get("itemName") if isinstance(identity.get("itemName"), str) else None
    item_hash = identity.get("itemHash") if isinstance(identity.get("itemHash"), int) else None
    return item_name, item_hash


def _load_existing_stack_sizes(out_path: Path) -> dict[str, int]:
    if not out_path.exists():
        return {}

    try:
        data = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        return {}

    stack_sizes: dict[str, int] = {}
    for recipe in recipes:
        if not isinstance(recipe, dict):
            continue
        item = recipe.get("item")
        if not isinstance(item, dict):
            continue
        wiki_title = item.get("wikiTitle")
        stack_size = recipe.get("stackSize")
        if isinstance(wiki_title, str) and isinstance(stack_size, int) and stack_size > 0:
            stack_sizes[wiki_title] = stack_size
    return stack_sizes


def upsert_recipe_index(entry: dict[str, Any]) -> None:
    RECIPES_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    if RECIPES_INDEX_PATH.exists():
        data = json.loads(RECIPES_INDEX_PATH.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "producers": []}

    producers = data.setdefault("producers", [])
    producers = [p for p in producers if p.get("wikiTitle") != entry.get("wikiTitle")]
    producers.append(entry)
    producers.sort(key=lambda producer: producer.get("wikiTitle", ""))
    data["producers"] = producers

    RECIPES_INDEX_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import Stationeers wiki recipe tables")
    parser.add_argument("url", help="Stationeers wiki recipes URL, e.g. https://stationeers-wiki.com/Autolathe/Recipes")
    args = parser.parse_args(argv)

    page_title, canonical_url, producer_title = _parse_recipe_url(args.url)
    wikitext = fetch_wikitext(page_title)
    recipes = parse_recipes(wikitext)
    item_name, item_hash = _load_device_identity(producer_title)
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out_dir = RECIPES_DIR / producer_title
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "recipes.json"
    existing_stack_sizes = _load_existing_stack_sizes(out_path)

    for recipe in recipes:
        existing_stack_size = existing_stack_sizes.get(recipe.item.wikiTitle)
        if existing_stack_size is not None and recipe.stackSize == 1:
            recipe.stackSize = existing_stack_size

    catalog = RecipeCatalogEntry(
        source={
            "kind": "wiki_import",
            "wikiUrl": canonical_url,
            "wikiTitle": page_title,
            "retrievedAt": retrieved_at,
        },
        producer={
            "wikiTitle": producer_title,
            "itemName": item_name,
            "itemHash": item_hash,
        },
        recipes=[asdict(recipe) for recipe in recipes],
    )

    out_path.write_text(
        json.dumps(asdict(catalog), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    upsert_recipe_index(
        {
            "wikiTitle": producer_title,
            "pageTitle": page_title,
            "file": f"recipes/{producer_title}/recipes.json",
            "recipeCount": len(recipes),
        }
    )

    print(f"Wrote {out_path.relative_to(ROOT)} ({len(recipes)} recipes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
