"""Read-only tests for the Massachusetts CCC package walk-through.

The walk-through maps one verbatim CCC fixture package through the existing
adapter without publishing or altering anything. These tests pin the
non-negotiable properties: the record stays unverified with a provisional id,
explicit zeros stay zero, and --write is refused (Massachusetts publication is
blocked by design).
"""

from __future__ import annotations

import unittest

from scripts.coa_model import RecordKind, ResultState
from scripts.ma_ccc_walkthrough import walk


class MassachusettsCccWalkthroughTest(unittest.TestCase):
    def test_package_maps_to_unverified_provisional_record(self):
        raw, normalized, rec = walk()
        self.assertEqual(len(raw), 4)
        self.assertEqual(len(normalized), 4)
        self.assertEqual(rec.batch.record_kind, RecordKind.UNVERIFIED)
        self.assertTrue(rec.report.report_id.startswith("ma-ccc:"))
        self.assertTrue(rec.batch.metrc_tag)

    def test_explicit_zeros_stay_zero_never_nd(self):
        raw, _, rec = walk()
        by_name = {m.compound_name: m for m in rec.measurements}
        for name in ("Lead", "Arsenic", "Total Yeast and Mold"):
            m = by_name[name]
            self.assertIs(m.state, ResultState.ZERO, name)
            self.assertEqual(m.value, 0.0, name)
        self.assertIs(by_name["THC"].state, ResultState.NUMERIC)

    def test_mixed_units_preserved(self):
        _, _, rec = walk()
        units = {m.unit for m in rec.measurements}
        self.assertIn("% w/w", units)
        self.assertIn("ppm", units)
        self.assertIn("CFU/g", units)

    def test_write_is_refused(self):
        from scripts.ma_ccc_walkthrough import MA_BLOCK_NOTICE, main
        # main() with no args runs the read-only walk and returns 0.
        self.assertEqual(main([]), 0)
        # --write must exit 2 (Massachusetts publication blocked), never write.
        self.assertEqual(main(["--write"]), 2)
        self.assertIn("BLOCKED", MA_BLOCK_NOTICE)
        self.assertIn("No content page was written", MA_BLOCK_NOTICE)


if __name__ == "__main__":
    unittest.main()
