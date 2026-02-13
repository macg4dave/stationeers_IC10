"""Setup contract checker for modular scripts.

Checks each `modular scripts/<feature>/Setup.md` against feature IC10 files:
- Required sections exist (`## Name contract`, `## Setup steps`)
- `Name contract` includes IC Housing entries (end-user setup clarity)
- Names referenced by `HASH("name")` in IC10 appear in Setup.md as code spans
- Shared channel tokens (`cmd_token`, `cmd_type`, `slotN`, `dataN`) seen in IC10
  appear in Setup.md as code spans
- Non-deprecated IC10 filenames are mentioned in Setup.md

Exit codes:
  0 - all checks passed
  1 - one or more issues found
  2 - usage/input error
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HASH_RE = re.compile(r'HASH\("([^"]+)"\)')
CHANNEL_RE = re.compile(r'\b(?:cmd_token|cmd_type|slot\d+|data\d+)\b')
HOUSING_RE = re.compile(r'^\s*-\s*IC Housing:\s*`([^`]+)`', re.MULTILINE)
SECTION_NAME = "## Name contract"
SECTION_STEPS = "## Setup steps"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _feature_dirs(modular_root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(modular_root.iterdir()):
        if not p.is_dir():
            continue
        if p.name.startswith("_"):
            continue
        if (p / "Setup.md").exists():
            out.append(p)
    return out


def _is_deprecated_ic10(script_path: Path) -> bool:
    try:
        head = "\n".join(_read_text(script_path).splitlines()[:5]).lower()
    except OSError:
        return False
    return "deprecated placeholder" in head


def _collect_feature_requirements(feature_dir: Path) -> tuple[set[str], set[str], list[str]]:
    hash_names: set[str] = set()
    channels: set[str] = set()
    script_files: list[str] = []

    for script in sorted(feature_dir.glob("*.ic10")):
        if _is_deprecated_ic10(script):
            continue
        script_files.append(script.name)
        text = _read_text(script)
        hash_names.update(HASH_RE.findall(text))
        channels.update(CHANNEL_RE.findall(text))

    return hash_names, channels, script_files


def _as_code_span(token: str) -> str:
    return f"`{token}`"


def run(modular_dir: Path) -> int:
    if not modular_dir.exists() or not modular_dir.is_dir():
        print(f"ERROR: modular scripts dir not found: {modular_dir}")
        return 2

    errors: list[str] = []
    features = _feature_dirs(modular_dir)
    if not features:
        print(f"ERROR: no feature folders with Setup.md found under {modular_dir}")
        return 2

    for feature in features:
        setup = feature / "Setup.md"
        setup_text = _read_text(setup)

        if SECTION_NAME not in setup_text:
            errors.append(f"{setup}: missing section '{SECTION_NAME}'")
        if SECTION_STEPS not in setup_text:
            errors.append(f"{setup}: missing section '{SECTION_STEPS}'")

        hash_names, channels, script_files = _collect_feature_requirements(feature)
        housing_names = sorted(set(HOUSING_RE.findall(setup_text)))

        if not housing_names:
            errors.append(
                f"{setup}: Name contract must include at least one 'IC Housing: `name`' entry"
            )
        elif len(housing_names) < len(script_files):
            errors.append(
                f"{setup}: IC Housing entries ({len(housing_names)}) fewer than "
                f"non-deprecated feature scripts ({len(script_files)}); list all chip housings"
            )

        for name in sorted(hash_names):
            if _as_code_span(name) not in setup_text:
                errors.append(
                    f"{setup}: missing name contract token {_as_code_span(name)} "
                    f"(referenced in feature IC10 HASH())"
                )

        for channel in sorted(channels):
            if _as_code_span(channel) not in setup_text:
                errors.append(
                    f"{setup}: missing shared-channel token {_as_code_span(channel)} "
                    f"(referenced in feature IC10)"
                )

        for filename in script_files:
            if filename not in setup_text:
                errors.append(
                    f"{setup}: missing script path/name reference '{filename}'"
                )

    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"FAILED: setup contract check found {len(errors)} issue(s)")
        return 1

    print(f"OK: setup contract check passed ({len(features)} feature(s))")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate modular Setup.md contract consistency")
    parser.add_argument(
        "--modular-dir",
        default="modular scripts",
        help='Path to modular scripts root (default: "modular scripts")',
    )
    args = parser.parse_args()

    modular_dir = (ROOT / args.modular_dir).resolve()
    return run(modular_dir)


if __name__ == "__main__":
    raise SystemExit(main())
