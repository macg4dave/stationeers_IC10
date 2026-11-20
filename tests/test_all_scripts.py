"""Repo-wide checks for every shipped .ic10 file.

- static analysis finds no errors (paste limits, jumps, operands, identifiers)
- the script runs 300 ticks against permissive stub devices without the chip
  halting (catches jumps out of the program, stack misuse, bad aliases)
"""

import unittest

from helpers import ROOT, Chip, ChipError, Device
from ic10_engine import analyse, known_logic_types, load

SCRIPTS = sorted(list((ROOT / "scripts").rglob("*.ic10")) +
                 list((ROOT / "modular scripts").rglob("*.ic10")))
# Files with a known lint error, each tied to an audit defect id.
KNOWN_LINT_ERRORS: dict = {}


def stub() -> Device:
    return Device({}, permissive=True)


class EveryScript(unittest.TestCase):
    def test_inventory_is_not_empty(self):
        self.assertGreater(len(SCRIPTS), 40)

    def test_no_lint_errors(self):
        types = known_logic_types()
        for path in SCRIPTS:
            with self.subTest(script=str(path.relative_to(ROOT))):
                errors = [f for f in analyse(load(path), types) if f.level == "error"]
                if path.name in KNOWN_LINT_ERRORS:
                    self.assertTrue(errors, "known defect fixed: drop it from KNOWN_LINT_ERRORS")
                    continue
                self.assertEqual([f.format(path.name) for f in errors], [])

    def test_runs_without_halting(self):
        for path in SCRIPTS:
            with self.subTest(script=str(path.relative_to(ROOT))):
                pins = {f"d{i}": stub() for i in range(6)}
                chip = Chip(load(path), pins=pins, housing=stub())
                try:
                    chip.run(300)
                except ChipError as e:
                    self.fail(f"halted at tick {chip.tick}: {e}")


if __name__ == "__main__":
    unittest.main()
