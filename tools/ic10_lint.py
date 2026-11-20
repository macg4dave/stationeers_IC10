"""Static checks for shipped IC10 scripts.

Checks (see tools/ic10_engine.py `analyse`):
  errors   - paste limits (E020-E022), unknown instruction (E001), operand
             count (E002), undefined jump target (E003), relative branch given a
             label (E004), duplicate label (E006), unknown identifier (E013),
             wrong operand kinds (E014-E017)
  warnings - absolute jump to a numeric line (W005), LogicType not in catalog
             (W007), unreachable code (W009), label shadowing a LogicType (W010),
             define that refers to another name (W012)
  info     - register read before first write (I008), device pin used without a
             bdns/bdse guard (I011)

Usage
  python tools/ic10_lint.py                      # all of scripts/ and modular scripts/
  python tools/ic10_lint.py path/to/file.ic10    # specific files or folders
  python tools/ic10_lint.py --info               # also print info findings

Exit codes: 0 = no errors, 1 = errors found, 2 = usage error.
Warnings never fail the run; they are prompts for a human to check.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ic10_engine import analyse, known_logic_types, load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = [ROOT / "scripts", ROOT / "modular scripts"]


def iter_scripts(paths):
    for p in paths:
        p = Path(p)
        if p.is_file():
            yield p
        elif p.is_dir():
            yield from sorted(p.rglob("*.ic10"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Static checks for IC10 scripts")
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--info", action="store_true", help="show info-level findings")
    args = ap.parse_args(argv)

    paths = args.paths or DEFAULT_PATHS
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        print(f"ERROR: path not found: {missing[0]}")
        return 2

    types = known_logic_types()
    errors = warnings = files = 0
    for script in iter_scripts(paths):
        files += 1
        try:
            rel = script.resolve().relative_to(ROOT)
        except ValueError:
            rel = script
        for f in analyse(load(script), types):
            if f.level == "info" and not args.info:
                continue
            errors += f.level == "error"
            warnings += f.level == "warning"
            print(f.format(str(rel)))
    status = "FAILED" if errors else "OK"
    print(f"{status}: ic10 lint checked {files} file(s): "
          f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
