"""Check that path-like references in docs exist.

This intentionally focuses on inline backticked paths in markdown docs.
It ignores placeholders/wildcards/URLs and command snippets.

Two kinds of reference are checked:
- repo-rooted paths (`scripts/...`, `docs/...`, `tools/...`, ...)
- doc-relative entries such as `pipe_valves_open_when_cold/` or `active_vent.md`, resolved
  against the folder of the doc that mentions them (this is how the script and
  playbook indexes list their entries)

Exit codes:
  0 - checks passed
  1 - one or more missing paths
  2 - usage/input error
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_GLOBS = (
    "README.md", "AGENTS.md", ".github/*.md", "catalog/README.md",
    "scripts/README.md", "scripts/*/README.md",
    "modular scripts/README.md", "modular scripts/*/*.md",
    "docs/**/*.md",
)
_RELATIVE_RE = re.compile(r"^[A-Za-z0-9_.()-]+(/|\.md)$")


def _relative_candidate(token: str) -> str | None:
    """A bare `name/` or `name.md` entry, checked relative to the doc's folder."""
    token = token.strip().rstrip(".,:;")
    if token in {"README.md", "Setup.md", "AGENTS.md"}:
        return None   # generic names: usually "the README", not a specific file
    return token if _RELATIVE_RE.match(token) else None


def _normalize_candidate(token: str) -> str | None:
    token = token.strip().strip('"').strip("'").rstrip(".,:;")
    if not token:
        return None

    # Ignore non-path patterns.
    if any(x in token for x in ("<", ">", "*", "...")):
        return None
    if token.startswith(("http://", "https://", "#")):
        return None
    if token.lower() in {"lb/sb/lbn/sbn", "sbn/lbn"}:
        return None

    # Ignore command snippets.
    lowered = token.lower()
    if lowered.startswith(("python ", "bash ", "pwsh ", "powershell ", "git ")):
        return None
    if " --" in token:
        return None

    # Heuristic: only check repo-local path prefixes used in this repo.
    prefixes = (
        ".github/",
        ".vscode/",
        "catalog/",
        "docs/",
        "modular scripts/",
        "scripts/",
        "tools/",
        "README.md",
        "AGENTS.md",
    )
    if not token.startswith(prefixes):
        return None

    return token


def _iter_doc_files(root: Path, globs: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for pat in globs:
        out.extend(root.glob(pat))
    return sorted({p.resolve() for p in out if p.is_file()})


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate path-like references in docs")
    parser.add_argument(
        "--root",
        default=".",
        help="Repo root (default: current repo root)",
    )
    args = parser.parse_args()

    root = (ROOT / args.root).resolve()
    if not root.exists():
        print(f"ERROR: root not found: {root}")
        return 2

    docs = _iter_doc_files(root, DOC_GLOBS)
    if not docs:
        print("ERROR: no docs found to scan")
        return 2

    missing: list[str] = []
    pattern = re.compile(r"`([^`]+)`")

    for doc in docs:
        rel_doc = doc.relative_to(root)
        for line_no, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
            for m in pattern.finditer(line):
                token = m.group(1)
                candidate = _normalize_candidate(token)
                if candidate:
                    if not (root / candidate).resolve().exists():
                        missing.append(f"{rel_doc}:{line_no}: {candidate}")
                    continue
                rel = _relative_candidate(token)
                if rel and not (doc.parent / rel).exists() and not (root / rel).exists():
                    missing.append(f"{rel_doc}:{line_no}: {rel} (relative to {rel_doc.parent})")

    if missing:
        for msg in missing:
            print(f"ERROR: missing path reference: {msg}")
        print(f"FAILED: {len(missing)} missing path reference(s)")
        return 1

    print(f"OK: doc path check passed ({len(docs)} doc files scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
