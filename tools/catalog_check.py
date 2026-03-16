"""Catalog consistency checker.

Checks:
- `catalog/index.json` references existing files
- no orphan JSON files in `catalog/devices/`
- minimal per-device schema sanity

Exit codes:
  0 - checks passed (warnings allowed)
  1 - one or more errors found
  2 - usage/input error
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_KINDS = {"wiki_import", "best_guess"}


def _is_int_like(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number_like(value: Any) -> bool:
    return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as e:
        return None, f"read error: {e}"
    except json.JSONDecodeError as e:
        return None, f"json parse error: {e}"


def _check_field_list(
    device_path: Path,
    container_name: str,
    fields: Any,
    errors: list[str],
) -> None:
    if not isinstance(fields, list):
        errors.append(f"{device_path}: io.{container_name} must be an array")
        return
    for i, field in enumerate(fields):
        where = f"{device_path}: io.{container_name}[{i}]"
        if not isinstance(field, dict):
            errors.append(f"{where} must be an object")
            continue
        for key in ("name", "type", "description"):
            if key not in field:
                errors.append(f"{where} missing '{key}'")
                continue
            if not isinstance(field[key], str):
                errors.append(f"{where}.{key} must be a string")


def _check_device_schema(
    device_path: Path,
    expected_wiki_title: str | None,
    *,
    errors: list[str],
    warnings: list[str],
) -> None:
    data, err = _load_json(device_path)
    if err:
        errors.append(f"{device_path}: {err}")
        return
    if not isinstance(data, dict):
        errors.append(f"{device_path}: top-level must be an object")
        return

    source = data.get("source")
    identity = data.get("identity")
    io = data.get("io")

    if not isinstance(source, dict):
        errors.append(f"{device_path}: missing/invalid source object")
    else:
        source_kind = source.get("kind", "wiki_import")
        if not isinstance(source_kind, str):
            errors.append(f"{device_path}: source.kind must be a string when present")
            source_kind = "wiki_import"
        elif source_kind not in SOURCE_KINDS:
            errors.append(
                f"{device_path}: source.kind must be one of "
                f"{sorted(SOURCE_KINDS)} (got '{source_kind}')"
            )

        for key in ("wikiUrl", "wikiTitle", "retrievedAt"):
            if key not in source:
                errors.append(f"{device_path}: source missing '{key}'")
                continue
            if not isinstance(source[key], str):
                errors.append(f"{device_path}: source.{key} must be a string")
        if isinstance(source.get("wikiTitle"), str) and expected_wiki_title:
            if source["wikiTitle"] != expected_wiki_title:
                errors.append(
                    f"{device_path}: source.wikiTitle '{source['wikiTitle']}' "
                    f"!= index wikiTitle '{expected_wiki_title}'"
                )
        if source_kind == "wiki_import":
            for key in ("wikiUrl", "retrievedAt"):
                if isinstance(source.get(key), str) and not source[key].strip():
                    warnings.append(f"{device_path}: source.{key} is empty")
        elif source_kind == "best_guess":
            if "notes" in source and not isinstance(source["notes"], str):
                errors.append(f"{device_path}: source.notes must be a string when present")

    if not isinstance(identity, dict):
        errors.append(f"{device_path}: missing/invalid identity object")
    else:
        if "itemName" not in identity:
            errors.append(f"{device_path}: identity missing 'itemName'")
        else:
            item_name = identity["itemName"]
            if item_name is not None and not isinstance(item_name, str):
                errors.append(f"{device_path}: identity.itemName must be string|null")
            elif isinstance(item_name, str) and not item_name.strip():
                warnings.append(f"{device_path}: identity.itemName is empty string (prefer null)")

        if "itemHash" not in identity:
            errors.append(f"{device_path}: identity missing 'itemHash'")
        else:
            item_hash = identity["itemHash"]
            if item_hash is not None and not _is_int_like(item_hash):
                errors.append(f"{device_path}: identity.itemHash must be integer|null")

    if not isinstance(io, dict):
        errors.append(f"{device_path}: missing/invalid io object")
    else:
        _check_field_list(device_path, "parameters", io.get("parameters"), errors)
        _check_field_list(device_path, "outputs", io.get("outputs"), errors)
        if "modeValues" in io and not isinstance(io["modeValues"], list):
            errors.append(f"{device_path}: io.modeValues must be an array when present")


def _check_recipe_material(
    recipe_path: Path,
    where: str,
    material: Any,
    errors: list[str],
) -> None:
    if not isinstance(material, dict):
        errors.append(f"{where} must be an object")
        return
    for key in ("wikiTitle", "displayName"):
        if key not in material:
            errors.append(f"{where} missing '{key}'")
            continue
        if not isinstance(material[key], str):
            errors.append(f"{where}.{key} must be a string")
    if "quantity" not in material:
        errors.append(f"{where} missing 'quantity'")
    elif not _is_number_like(material["quantity"]):
        errors.append(f"{where}.quantity must be a number")


def _check_recipe_catalog_schema(
    recipe_path: Path,
    expected_wiki_title: str | None,
    expected_page_title: str | None,
    expected_recipe_count: int | None,
    *,
    errors: list[str],
    warnings: list[str],
) -> None:
    data, err = _load_json(recipe_path)
    if err:
        errors.append(f"{recipe_path}: {err}")
        return
    if not isinstance(data, dict):
        errors.append(f"{recipe_path}: top-level must be an object")
        return

    source = data.get("source")
    producer = data.get("producer")
    recipes = data.get("recipes")

    if not isinstance(source, dict):
        errors.append(f"{recipe_path}: missing/invalid source object")
    else:
        source_kind = source.get("kind", "wiki_import")
        if not isinstance(source_kind, str):
            errors.append(f"{recipe_path}: source.kind must be a string when present")
            source_kind = "wiki_import"
        elif source_kind not in SOURCE_KINDS:
            errors.append(
                f"{recipe_path}: source.kind must be one of "
                f"{sorted(SOURCE_KINDS)} (got '{source_kind}')"
            )

        for key in ("wikiUrl", "wikiTitle", "retrievedAt"):
            if key not in source:
                errors.append(f"{recipe_path}: source missing '{key}'")
                continue
            if not isinstance(source[key], str):
                errors.append(f"{recipe_path}: source.{key} must be a string")

        if isinstance(source.get("wikiTitle"), str) and expected_page_title:
            if source["wikiTitle"] != expected_page_title:
                errors.append(
                    f"{recipe_path}: source.wikiTitle '{source['wikiTitle']}' "
                    f"!= index pageTitle '{expected_page_title}'"
                )

    if not isinstance(producer, dict):
        errors.append(f"{recipe_path}: missing/invalid producer object")
    else:
        wiki_title = producer.get("wikiTitle")
        if not isinstance(wiki_title, str):
            errors.append(f"{recipe_path}: producer.wikiTitle must be a string")
        elif expected_wiki_title and wiki_title != expected_wiki_title:
            errors.append(
                f"{recipe_path}: producer.wikiTitle '{wiki_title}' "
                f"!= index wikiTitle '{expected_wiki_title}'"
            )

        if "itemName" not in producer:
            errors.append(f"{recipe_path}: producer missing 'itemName'")
        elif producer["itemName"] is not None and not isinstance(producer["itemName"], str):
            errors.append(f"{recipe_path}: producer.itemName must be string|null")

        if "itemHash" not in producer:
            errors.append(f"{recipe_path}: producer missing 'itemHash'")
        elif producer["itemHash"] is not None and not _is_int_like(producer["itemHash"]):
            errors.append(f"{recipe_path}: producer.itemHash must be integer|null")

    if not isinstance(recipes, list):
        errors.append(f"{recipe_path}: recipes must be an array")
        return

    seen_items: set[str] = set()
    for i, recipe in enumerate(recipes):
        where = f"{recipe_path}: recipes[{i}]"
        if not isinstance(recipe, dict):
            errors.append(f"{where} must be an object")
            continue

        item = recipe.get("item")
        if not isinstance(item, dict):
            errors.append(f"{where}.item must be an object")
        else:
            for key in ("wikiTitle", "displayName"):
                if key not in item:
                    errors.append(f"{where}.item missing '{key}'")
                    continue
                if not isinstance(item[key], str):
                    errors.append(f"{where}.item.{key} must be a string")
            if "itemName" not in item:
                errors.append(f"{where}.item missing 'itemName'")
            elif item["itemName"] is not None and not isinstance(item["itemName"], str):
                errors.append(f"{where}.item.itemName must be string|null")
            if "itemHash" not in item:
                errors.append(f"{where}.item missing 'itemHash'")
            elif item["itemHash"] is not None and not _is_int_like(item["itemHash"]):
                errors.append(f"{where}.item.itemHash must be integer|null")
            item_wiki_title = item.get("wikiTitle")
            if isinstance(item_wiki_title, str):
                if item_wiki_title in seen_items:
                    errors.append(f"{where}.item.wikiTitle duplicated: {item_wiki_title}")
                seen_items.add(item_wiki_title)

        for key in ("tier",):
            if key not in recipe:
                errors.append(f"{where} missing '{key}'")
            elif not isinstance(recipe[key], str):
                errors.append(f"{where}.{key} must be a string")

        for key in ("time", "energy"):
            if key not in recipe:
                errors.append(f"{where} missing '{key}'")
            elif not _is_number_like(recipe[key]):
                errors.append(f"{where}.{key} must be a number")

        if "stackSize" in recipe:
            stack_size = recipe["stackSize"]
            if not _is_int_like(stack_size):
                errors.append(f"{where}.stackSize must be an integer when present")
            elif stack_size < 1:
                errors.append(f"{where}.stackSize must be >= 1")

        inputs = recipe.get("inputs")
        if not isinstance(inputs, list):
            errors.append(f"{where}.inputs must be an array")
            continue
        if not inputs:
            warnings.append(f"{where}.inputs is empty")
        for j, material in enumerate(inputs):
            _check_recipe_material(recipe_path, f"{where}.inputs[{j}]", material, errors)

    if expected_recipe_count is not None and len(recipes) != expected_recipe_count:
        errors.append(
            f"{recipe_path}: recipe count {len(recipes)} != index recipeCount {expected_recipe_count}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate catalog index and device JSON files")
    parser.add_argument(
        "--catalog-dir",
        default="catalog",
        help="Catalog root directory (default: catalog)",
    )
    args = parser.parse_args()

    catalog_dir = (ROOT / args.catalog_dir).resolve()
    index_path = catalog_dir / "index.json"
    devices_dir = catalog_dir / "devices"
    recipes_dir = catalog_dir / "recipes"
    recipes_index_path = recipes_dir / "index.json"

    if not index_path.exists():
        print(f"ERROR: index not found: {index_path}")
        return 2
    if not devices_dir.exists():
        print(f"ERROR: devices dir not found: {devices_dir}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    index, err = _load_json(index_path)
    if err:
        print(f"ERROR: {index_path}: {err}")
        return 1
    if not isinstance(index, dict):
        print(f"ERROR: {index_path}: top-level must be an object")
        return 1

    devices = index.get("devices")
    if not isinstance(devices, list):
        print(f"ERROR: {index_path}: 'devices' must be an array")
        return 1

    seen_titles: set[str] = set()
    seen_files: set[str] = set()
    referenced_files: set[str] = set()

    for i, entry in enumerate(devices):
        where = f"{index_path}: devices[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where} must be an object")
            continue

        wiki_title = entry.get("wikiTitle")
        rel_file = entry.get("file")
        if not isinstance(wiki_title, str) or not wiki_title.strip():
            errors.append(f"{where}.wikiTitle must be a non-empty string")
            wiki_title = None
        if not isinstance(rel_file, str) or not rel_file.strip():
            errors.append(f"{where}.file must be a non-empty string")
            continue

        rel_file = rel_file.replace("\\", "/")
        if not rel_file.startswith("devices/"):
            errors.append(f"{where}.file must be under devices/: {rel_file}")

        if wiki_title:
            if wiki_title in seen_titles:
                errors.append(f"{where}.wikiTitle duplicated: {wiki_title}")
            seen_titles.add(wiki_title)
        if rel_file in seen_files:
            errors.append(f"{where}.file duplicated: {rel_file}")
        seen_files.add(rel_file)
        referenced_files.add(rel_file)

        device_path = catalog_dir / rel_file
        if not device_path.exists():
            errors.append(f"{where}: missing file: {device_path}")
            continue

        _check_device_schema(
            device_path,
            wiki_title,
            errors=errors,
            warnings=warnings,
        )

    for p in sorted(devices_dir.glob("*.json")):
        rel = f"devices/{p.name}"
        if rel not in referenced_files:
            errors.append(f"{index_path}: orphan device file not indexed: {rel}")

    if recipes_dir.exists() or recipes_index_path.exists():
        if not recipes_index_path.exists():
            errors.append(f"{catalog_dir}: recipes dir exists but recipes/index.json is missing")
        elif not recipes_dir.exists():
            errors.append(f"{catalog_dir}: recipes/index.json exists but recipes dir is missing")
        else:
            recipes_index, err = _load_json(recipes_index_path)
            if err:
                errors.append(f"{recipes_index_path}: {err}")
            elif not isinstance(recipes_index, dict):
                errors.append(f"{recipes_index_path}: top-level must be an object")
            else:
                producers = recipes_index.get("producers")
                if not isinstance(producers, list):
                    errors.append(f"{recipes_index_path}: 'producers' must be an array")
                else:
                    seen_recipe_titles: set[str] = set()
                    seen_recipe_files: set[str] = set()
                    referenced_recipe_files: set[str] = set()

                    for i, entry in enumerate(producers):
                        where = f"{recipes_index_path}: producers[{i}]"
                        if not isinstance(entry, dict):
                            errors.append(f"{where} must be an object")
                            continue

                        wiki_title = entry.get("wikiTitle")
                        page_title = entry.get("pageTitle")
                        rel_file = entry.get("file")
                        recipe_count = entry.get("recipeCount")

                        if not isinstance(wiki_title, str) or not wiki_title.strip():
                            errors.append(f"{where}.wikiTitle must be a non-empty string")
                            wiki_title = None
                        if not isinstance(page_title, str) or not page_title.strip():
                            errors.append(f"{where}.pageTitle must be a non-empty string")
                            page_title = None
                        if not isinstance(rel_file, str) or not rel_file.strip():
                            errors.append(f"{where}.file must be a non-empty string")
                            continue
                        if not _is_int_like(recipe_count):
                            errors.append(f"{where}.recipeCount must be an integer")
                            recipe_count = None

                        rel_file = rel_file.replace("\\", "/")
                        if not rel_file.startswith("recipes/"):
                            errors.append(f"{where}.file must be under recipes/: {rel_file}")

                        if wiki_title:
                            if wiki_title in seen_recipe_titles:
                                errors.append(f"{where}.wikiTitle duplicated: {wiki_title}")
                            seen_recipe_titles.add(wiki_title)
                        if rel_file in seen_recipe_files:
                            errors.append(f"{where}.file duplicated: {rel_file}")
                        seen_recipe_files.add(rel_file)
                        referenced_recipe_files.add(rel_file)

                        recipe_path = catalog_dir / rel_file
                        if not recipe_path.exists():
                            errors.append(f"{where}: missing file: {recipe_path}")
                            continue

                        _check_recipe_catalog_schema(
                            recipe_path,
                            wiki_title,
                            page_title,
                            recipe_count,
                            errors=errors,
                            warnings=warnings,
                        )

                    for p in sorted(recipes_dir.rglob("*.json")):
                        rel = p.relative_to(catalog_dir).as_posix()
                        if rel == "recipes/index.json":
                            continue
                        if rel not in referenced_recipe_files:
                            errors.append(
                                f"{recipes_index_path}: orphan recipe file not indexed: {rel}"
                            )

    for msg in errors:
        print(f"ERROR: {msg}")
    for msg in warnings:
        print(f"WARN:  {msg}")

    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"OK: catalog check passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
