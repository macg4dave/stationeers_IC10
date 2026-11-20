"""Run every repository check and report one summary.

    python tools/check_all.py

Runs, in order:
  1. paste limits        tools/ic10_size_check.py (scripts/ and modular scripts/)
  2. IC10 static lint    tools/ic10_lint.py
  3. setup contracts     tools/setup_contract_check.py
  4. catalog schema      tools/catalog_check.py
  5. doc path refs       tools/doc_path_check.py
  6. generated files     tools/autolathe_profile_emit.py --check
  7. behaviour tests     python -m unittest discover -s tests

Exit code 0 only if every step passes. What "pass" means:
  static checks passed  -> the files are paste-ready and structurally sound
  tests passed          -> simulated behaviour matches the documented scenarios
Neither proves in-game behaviour; see docs/engineering_audit.md for the
scripts that still need a human test in Stationeers.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

STEPS = [
    ("paste limits: scripts", [PY, "tools/ic10_size_check.py", "scripts/", "--ext", ".ic10"]),
    ("paste limits: modular", [PY, "tools/ic10_size_check.py", "modular scripts/", "--ext", ".ic10"]),
    ("ic10 lint", [PY, "tools/ic10_lint.py"]),
    ("setup contracts", [PY, "tools/setup_contract_check.py"]),
    ("catalog schema", [PY, "tools/catalog_check.py"]),
    ("doc path refs", [PY, "tools/doc_path_check.py"]),
    ("generated files", [PY, "tools/autolathe_profile_emit.py", "--all", "--check"]),
    ("behaviour tests", [PY, "-m", "unittest", "discover", "-s", "tests"]),
]


def main() -> int:
    failed = []
    for name, cmd in STEPS:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        ok = proc.returncode == 0
        tail = (proc.stdout + proc.stderr).strip().splitlines()
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {tail[-1] if tail else ''}")
        if not ok:
            failed.append(name)
            for line in tail[-15:]:
                print(f"       {line}")
    print("\nAll checks passed." if not failed else f"\nFailed: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
