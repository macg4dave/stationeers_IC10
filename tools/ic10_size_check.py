"""IC10 script size checker.

Checks Stationeers IC10 chip constraints:
- Max 128 lines
- Max 90 characters per line

This repo has not yet standardized script file extensions.
If you pass a directory, use --ext to control which files are checked.

Examples
    python tools/ic10_size_check.py path/to/script.ic10
    python tools/ic10_size_check.py scripts/ --ext .ic10 --ext .txt

Exit codes
  0 - all files OK
  1 - one or more files violate constraints
  2 - usage / input error
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_MAX_LINES = 128
DEFAULT_MAX_COLS = 90


@dataclass(frozen=True)
class Violation:
    path: Path
    message: str


def _iter_candidate_files(path: Path, exts: list[str]) -> Iterable[Path]:
    if path.is_file():
        yield path
        return

    if not path.is_dir():
        return

    # If extensions are provided, use them. Otherwise, default to a conservative
    # set and require the user to extend/adjust once the repo decides a format.
    normalized_exts = [e if e.startswith(".") else f".{e}" for e in exts]

    for p in sorted(path.rglob("*")):
        if not p.is_file():
            continue
        if p.parts and any(part in {".git", "catalog", "tools"} for part in p.parts):
            continue
        if normalized_exts and p.suffix.lower() not in {e.lower() for e in normalized_exts}:
            continue
        yield p


def _check_text(text: str, max_lines: int, max_cols: int) -> tuple[int, list[int]]:
    """Return (line_count, offending_line_numbers_1_based)."""
    lines = text.splitlines()
    offending: list[int] = []
    for i, line in enumerate(lines, start=1):
        # splitlines() strips line endings; length is character count in the line.
        if len(line) > max_cols:
            offending.append(i)
    return len(lines), offending


def check_file(path: Path, max_lines: int, max_cols: int) -> list[Violation]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # IC10 scripts should be plain text; if decoding fails, report clearly.
        return [Violation(path=path, message="not valid UTF-8 text")]
    except OSError as e:
        return [Violation(path=path, message=f"read error: {e}")]

    line_count, too_long = _check_text(text, max_lines=max_lines, max_cols=max_cols)

    violations: list[Violation] = []

    if line_count > max_lines:
        violations.append(
            Violation(
                path=path,
                message=f"too many lines: {line_count} (max {max_lines})",
            )
        )

    if too_long:
        preview = ", ".join(str(n) for n in too_long[:10])
        more = "" if len(too_long) <= 10 else f" (+{len(too_long) - 10} more)"
        violations.append(
            Violation(
                path=path,
                message=f"line(s) exceed {max_cols} chars: {preview}{more}",
            )
        )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Check IC10 script size constraints")
    parser.add_argument("path", help="File or directory to check")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_MAX_LINES,
        help=f"Maximum allowed lines (default: {DEFAULT_MAX_LINES})",
    )
    parser.add_argument(
        "--max-cols",
        type=int,
        default=DEFAULT_MAX_COLS,
        help=f"Maximum allowed characters per line (default: {DEFAULT_MAX_COLS})",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        help="File extension(s) to include when checking a directory (repeatable). Example: --ext .ic10",
    )

    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Path not found: {path}")
        return 2

    exts = args.ext
    if path.is_dir() and not exts:
        # Avoid accidentally scanning everything (json, md, etc.) until the repo
        # settles on canonical script extensions.
        exts = [".ic10", ".ic"]

    all_violations: list[Violation] = []
    for f in _iter_candidate_files(path, exts=exts):
        all_violations.extend(check_file(f, max_lines=args.max_lines, max_cols=args.max_cols))

    if not all_violations:
        print("OK")
        return 0

    for v in all_violations:
        print(f"{v.path}: {v.message}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
