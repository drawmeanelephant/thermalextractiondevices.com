"""Smoke tests for the verified-COA walk-through (scripts/coa_verify_example.py).

The walk-through transcribes one real published COA (InfiniteCAL CA, batch
250410-37-002) into a verified CoaRecord and renders the lab-results page.
These tests pin the non-negotiable properties: verified kind, clean hard
validation, a complete provenance chain, and a Boris-safe rendered page.
"""

from __future__ import annotations

import re
import unittest

from pathlib import Path

from scripts.coa_model import RecordKind, coa_problems
from scripts.coa_verify_example import (
    DATASET_ID,
    DOCUMENT_HASH,
    ROOT,
    SNAPSHOT_PATH,
    record,
    render_dataset_page,
    render_page,
)


class CoaVerifyExampleTest(unittest.TestCase):
    def test_record_is_verified_and_valid(self):
        rec = record()
        self.assertEqual(rec.batch.record_kind, RecordKind.VERIFIED)
        self.assertEqual(rec.report.report_id, "lab-results/TLAB-0002")
        self.assertEqual(rec.report.laboratory.lab_id, "testing-laboratories/TSTL-0006")
        self.assertEqual(coa_problems(rec), [])
        self.assertGreaterEqual(len(rec.measurements), 30)

    def test_provenance_chain_complete(self):
        prov = record().report.provenance
        self.assertTrue(prov.source_url.startswith("https://"))
        self.assertEqual(prov.document_hash, DOCUMENT_HASH)
        self.assertEqual(len(DOCUMENT_HASH), 64)
        self.assertIsNotNone(prov.retrieval_date)
        self.assertTrue(prov.upstream_record_id)
        self.assertTrue(prov.parser_version)

    def test_state_mix_covers_censoring(self):
        states = {m.state for m in record().measurements}
        self.assertIn("numeric", {s.value for s in states})
        self.assertIn("nd", {s.value for s in states})
        self.assertIn("below_loq", {s.value for s in states})

    def test_calculated_totals_carry_formulas(self):
        calc = [m for m in record().measurements if m.calculation_formula]
        self.assertEqual(len(calc), 3)  # Total THC, Total CBD, Total Cannabinoids
        self.assertTrue(all("0.877" in f for f in (m.calculation_formula for m in calc)))

    def test_rendered_page_is_boris_safe_and_under_relation_cap(self):
        page = render_page(record())
        self.assertIn("lab-results/TLAB-0002", page)
        self.assertIn("## Provenance & Sources", page)
        self.assertIn(DOCUMENT_HASH, page)
        # Boris rejects raw "<LOQ" as an unclosed component tag; it must be escaped.
        self.assertNotIn("<LOQ", page)
        self.assertIn("&lt;LOQ", page)
        relations = re.findall(r"relates_to=", page)
        self.assertLessEqual(len(relations), 16)  # Boris max relation count

    def test_dataset_page_registers_snapshot(self):
        page = render_dataset_page(record())
        self.assertIn(DATASET_ID, page)
        self.assertIn(DOCUMENT_HASH, page)
        self.assertIn(SNAPSHOT_PATH.relative_to(ROOT).as_posix(), page)
        self.assertIn("var/ingest/coa-verify", page)
        relations = re.findall(r"relates_to=", page)
        self.assertLessEqual(len(relations), 16)

    def test_snapshot_path_lives_under_gitignored_var(self):
        rel = SNAPSHOT_PATH.relative_to(ROOT)
        self.assertEqual(rel.parts[0], "var")

    def test_durable_record_is_schema_shaped(self):
        payload = record().to_dict()
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["report"]["report_id"], "lab-results/TLAB-0002")
        self.assertEqual(payload["batch"]["record_kind"], "verified")
        self.assertGreaterEqual(len(payload["measurements"]), 30)

    def test_printed_units_and_calculated_limits_are_not_invented(self):
        measurements = {m.compound_name: m for m in record().measurements}
        self.assertEqual(measurements["CBD"].reported_value, "0.219")
        self.assertEqual(measurements["CBD"].reported_unit, "mg/pkg")
        self.assertEqual(measurements["Lead"].reported_value, "< LOQ")
        self.assertEqual(measurements["Lead"].reported_unit, "µg/g")
        self.assertEqual(measurements["Aflatoxin B1"].reported_unit, "µg/kg")
        self.assertEqual(measurements["Aflatoxin B1"].unit, "other")
        for name in ("Total THC", "Total CBD", "Total Cannabinoids"):
            self.assertIsNotNone(measurements[name].calculation_formula)
            self.assertIsNone(measurements[name].lod)
            self.assertIsNone(measurements[name].loq)

    def test_source_has_no_fabricated_missing_or_below_lod_rows(self):
        states = {m.state.value for m in record().measurements}
        self.assertEqual(states, {"numeric", "nd", "below_loq"})
        self.assertNotIn("missing", states)
        self.assertNotIn("below_lod", states)


if __name__ == "__main__":
    unittest.main()
