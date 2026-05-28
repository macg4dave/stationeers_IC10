"""Emit AutolatheVendStock IC10 worker variants from a curated profile.

Usage:
  python tools/autolathe_profile_emit.py free_ingots
  python tools/autolathe_profile_emit.py --all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_INDEX_PATH = ROOT / "catalog" / "recipes" / "Autolathe" / "profiles" / "index.json"
MODULE_DIR = ROOT / "modular scripts" / "AutolatheVendStock"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_profiles() -> dict[str, dict[str, Any]]:
    index = _load_json(PROFILE_INDEX_PATH)
    profiles: dict[str, dict[str, Any]] = {}
    for entry in index.get("profiles", []):
        rel_file = entry["file"]
        path = ROOT / "catalog" / rel_file
        data = _load_json(path)
        profiles[data["id"]] = data
    return profiles


def _emit_stock_worker(profile: dict[str, Any]) -> str:
    tracked = profile["build"]["stockWorker"]["trackedItems"]
    if not tracked:
        raise ValueError(f"profile {profile['id']} has no trackedItems")

    lines = [
        f"# profile: {profile['id']}",
        "alias vend d0",
        "alias n1 d1",
        "alias n2 d2",
        "alias n3 d3",
        "alias n4 d4",
        "alias n5 d5",
        "alias idx r0",
        "alias slot r1",
        "alias want r2",
        "alias occ r3",
        "alias item r4",
        "alias found r5",
        "alias token r6",
        "alias cond r7",
        "alias house r9",
        "",
        'define MEMH HASH("StructureLogicMemory")',
        'define CTOK HASH("cmd_token")',
        'define CTYPE HASH("cmd_type")',
        'define SLOT0 HASH("slot0")',
        'define SLOT1 HASH("slot1")',
        'define SLOT4 HASH("slot4")',
        "",
        "auto:",
        "l house db PrefabHash",
        "move idx 0",
        "move slot 2",
        "move found 0",
        "s db Setting 500",
        "",
        "main:",
        "yield",
        "bdns d0 no_vend",
        f"move want {tracked[0]['itemHash']}",
    ]

    for i, item in enumerate(tracked[1:], start=1):
        lines.append(f"seq cond idx {i}")
        lines.append(f"select want cond {item['itemHash']} want")

    lines.extend(
        [
            "ls occ vend slot Occupied",
            "beqz occ next_slot",
            "ls item vend slot OccupantHash",
            "sne cond item want",
            "bnez cond next_slot",
            "move found 1",
            "next_slot:",
            "add slot slot 1",
            "slt cond slot 102",
            "bnez cond publish",
            "move slot 2",
            "bnez found next_hash",
            "lbn cond MEMH SLOT4 Setting Maximum",
            "bnez cond missing",
            "lbn token MEMH CTOK Setting Maximum",
            "add token token 1",
            "sbn MEMH SLOT0 Setting want",
            "sbn MEMH SLOT1 Setting 1",
            "sbn MEMH CTYPE Setting 1",
            "sbn MEMH CTOK Setting token",
            "missing:",
            "s db Setting want",
            "j main",
            "next_hash:",
            "move found 0",
            "add idx idx 1",
            f"slt cond idx {len(tracked)}",
            "bnez cond publish",
            "move idx 0",
            "publish:",
            "s db Setting 500",
            "j main",
            "no_vend:",
            "s db Setting 540",
            "j main",
        ]
    )

    return "\n".join(lines) + "\n"


def _emit_logistics_worker(profile: dict[str, Any]) -> str:
    logistics = profile["build"]["logisticsWorker"]
    base_targets = logistics["baseContentsTargets"]
    required_targets = logistics["recipeRequiredTargets"]
    if not base_targets:
        raise ValueError(f"profile {profile['id']} has no baseContentsTargets")

    lines = [
        f"# profile: {profile['id']}",
        "alias n0 d0",
        "alias n1 d1",
        "alias mach d2",
        "alias n3 d3",
        "alias n4 d4",
        "alias n5 d5",
        "alias need r0",
        "alias tmp r1",
        "alias oldimp r2",
        "alias level r3",
        'define MEMH HASH("StructureLogicMemory")',
        'define SLOT2 HASH("slot2")',
        "define CLEAR_REQ -1",
        f"define LOW_REAGENT {logistics['lowReagent']}",
        f"define TARGET_REAGENT {logistics['targetReagent']}",
    ]

    for target in base_targets + required_targets:
        lines.append(f"define {target['reagentDefine']} {target['reagentHash']}")
    for target in base_targets + required_targets:
        lines.append(f"define {target['ingotDefine']} {target['ingotHash']}")

    lines.extend(
        [
            "auto:",
            "move need CLEAR_REQ",
            "move oldimp 0",
            "s db Setting 200",
            "main:",
            "yield",
            "bdns d2 no_mach",
            "check_arrive:",
            "l tmp mach ImportCount",
            "ble tmp oldimp check_need",
            "move oldimp tmp",
            "move need CLEAR_REQ",
            "check_need:",
            "bne need CLEAR_REQ track_need",
            "scan_need:",
        ]
    )

    for target in base_targets:
        lines.append(f"lr tmp mach Contents {target['reagentDefine']}")
        lines.append("slt tmp tmp LOW_REAGENT")
        lines.append("seq level need CLEAR_REQ")
        lines.append("and tmp tmp level")
        lines.append(f"select need tmp {target['ingotDefine']} need")

    for target in required_targets:
        lines.append(f"lr tmp mach Required {target['reagentDefine']}")
        lines.append("sgt tmp tmp 0")
        lines.append("and tmp tmp level")
        lines.append(f"select need tmp {target['ingotDefine']} need")

    lines.extend(
        [
            "j publish",
            "track_need:",
        ]
    )

    for i, target in enumerate(required_targets):
        lines.append(f"seq tmp need {target['ingotDefine']}")
        lines.append(f"bnez tmp track_required_{i}")

    lines.extend(
        [
            "j common_need",
        ]
    )

    for i, target in enumerate(required_targets):
        lines.extend(
            [
                f"track_required_{i}:",
                f"lr tmp mach Required {target['reagentDefine']}",
                "bgtz tmp publish",
                "move need CLEAR_REQ",
                "j publish",
            ]
        )

    lines.extend(
        [
            "common_need:",
            f"move level {base_targets[-1]['reagentDefine']}",
        ]
    )

    for target in base_targets:
        lines.append(f"seq tmp need {target['ingotDefine']}")
        lines.append(f"select level tmp {target['reagentDefine']} level")

    lines.extend(
        [
            "lr level mach Contents level",
            "slt tmp level TARGET_REAGENT",
            "bnez tmp publish",
            "move need CLEAR_REQ",
            "j scan_need",
            "publish:",
            "bne need CLEAR_REQ active",
            "s db Setting 200",
            "sbn MEMH SLOT2 Setting 0",
            "j main",
            "active:",
            "s db Setting need",
            "sbn MEMH SLOT2 Setting need",
            "j main",
            "no_mach:",
            "s db Setting 243",
            "j main",
        ]
    )

    return "\n".join(lines) + "\n"


def emit_profile(profile: dict[str, Any]) -> list[Path]:
    profile_id = profile["id"]
    stock_path = MODULE_DIR / f"autolathe_vend_stock_worker_stock.{profile_id}.ic10"
    logistics_path = MODULE_DIR / f"autolathe_vend_stock_worker_logistics.{profile_id}.ic10"
    stock_path.write_text(_emit_stock_worker(profile), encoding="utf-8")
    logistics_path.write_text(_emit_logistics_worker(profile), encoding="utf-8")
    return [stock_path, logistics_path]


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit AutolatheVendStock worker variants")
    parser.add_argument("profile_ids", nargs="*", help="Profile id(s) to emit, e.g. free_ingots")
    parser.add_argument("--all", action="store_true", help="Emit worker variants for all profiles")
    args = parser.parse_args()

    if not args.all and not args.profile_ids:
        parser.error("provide one or more profile ids or use --all")

    profiles = _load_profiles()
    wanted = sorted(profiles) if args.all else args.profile_ids

    emitted: list[Path] = []
    for profile_id in wanted:
        if profile_id not in profiles:
            parser.error(f"unknown profile id: {profile_id}")
        emitted.extend(emit_profile(profiles[profile_id]))

    for path in emitted:
        print(f"Wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())