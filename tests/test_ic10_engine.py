"""Unit tests for the IC10 parser/simulator/analyser itself."""

import unittest

from helpers import Chip, ChipError, Device, ic10_hash
from ic10_engine import analyse, parse


def run(src: str, ticks: int = 1, **pins) -> Chip:
    return Chip(parse(src), pins=pins).run(ticks)


class HashTests(unittest.TestCase):
    def test_prefab_hashes_match_known_values(self):
        # Values that the repo's scripts hard-code and that are confirmed in-game.
        self.assertEqual(ic10_hash("StructureActiveVent"), -1129453144)
        self.assertEqual(ic10_hash("StructureDigitalValve"), -1280984102)
        self.assertEqual(ic10_hash("StructureGasSensor"), -1252983604)


class ExecutionTests(unittest.TestCase):
    def test_absolute_vs_relative_branch(self):
        src = "move r0 1\nbeqz 0 4\nmove r1 7\nyield\nmove r2 9\nyield"
        c = run(src)
        self.assertEqual((c.reg[1], c.reg[2]), (0, 9))        # jumped to line 4
        src = "move r0 1\nbreqz 0 2\nmove r1 7\nmove r2 9\nyield"
        c = run(src)
        self.assertEqual((c.reg[1], c.reg[2]), (0, 9))        # skipped one line

    def test_relative_branch_with_label_jumps_by_label_value(self):
        # brlt with a label adds the label's *line number* as an offset.
        src = "yield\nyield\nbrlt 0 1 target\ntarget:\nyield"   # 2 + 3 = line 5
        with self.assertRaises(ChipError):
            run(src, ticks=3)

    def test_yield_and_instruction_budget(self):
        # Labels, comments and blanks use an execution slot like instructions.
        c = run("main:\nadd r0 r0 1\nj main")
        self.assertEqual(c.reg[0], 43)                        # ceil(128 / 3)

    def test_sleep_ticks(self):
        c = Chip(parse("main:\nadd r0 r0 1\nsleep 1\nj main"))
        c.run(4)
        self.assertEqual(c.reg[0], 2)                         # 1 s = 2 ticks

    def test_runtime_alias_rebinding(self):
        a, b = Device({"Setting": 1}), Device({"Setting": 2})
        c = run("alias x d0\nl r0 x Setting\nalias x d1\nl r1 x Setting\nyield", d0=a, d1=b)
        self.assertEqual((c.reg[0], c.reg[1]), (1, 2))

    def test_unset_pin_raises(self):
        with self.assertRaises(ChipError):
            run("l r0 d0 On\nyield")

    def test_bitwise_and(self):
        c = run("move r0 19\nand r1 r0 16\nand r2 r0 4\nyield")
        self.assertEqual((c.reg[1], c.reg[2]), (16, 0))

    def test_batch_name_hash_is_exact(self):
        v1 = Device({"On": 0}, prefab="StructureActiveVent", name="IN")
        v2 = Device({"On": 0}, prefab="StructureActiveVent", name="IN_1")
        c = Chip(parse('sbn HASH("StructureActiveVent") HASH("IN") On 1\nyield'),
                 network=[v1, v2]).run()
        self.assertEqual((v1.fields["On"], v2.fields["On"]), (1, 0))
        self.assertEqual(c.tick, 1)


class AnalyserTests(unittest.TestCase):
    def codes(self, src):
        return [f.code for f in analyse(parse(src), logic_types={"On", "Setting"})]

    def test_flags_relative_branch_with_label(self):
        self.assertIn("E004", self.codes("x:\nbrlt r0 1 x"))

    def test_flags_absolute_numeric_jump(self):
        self.assertIn("W005", self.codes("beqz r0 2"))

    def test_flags_undefined_label_and_duplicates(self):
        self.assertIn("E003", self.codes("j nowhere"))
        self.assertIn("E006", self.codes("a:\na:\nj a"))

    def test_flags_read_before_write(self):
        self.assertIn("I008", self.codes("main:\nbnez r1 main\nl r1 d0 On\nj main"))

    def test_clean_program(self):
        self.assertEqual(self.codes("alias v d0\nw:\nyield\nbdns v w\nl r0 v On\nj w"), [])


if __name__ == "__main__":
    unittest.main()
