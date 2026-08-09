"""Canonical evidence model tests (docs/jurisdiction-evidence-model.md)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ingest.core import IngestError
from scripts.ingest.evidence import (
    AnalyteResult,
    COARecord,
    assert_valid_coa_record,
    classify_result,
    normalize_analyte_name,
    read_coa_csv,
    validate_coa_record,
    write_coa_csv,
)


def _record() -> COARecord:
    return COARecord(
        jurisdiction="massachusetts",
        source_document="coa-1.pdf",
        source_url="https://example.test/coa-1.pdf",
        source_hash="abc123",
        source_retrieved_at="2026-08-09T00:00:00Z",
        lab_raw="Example Analytics",
        producer_raw="Example Cultivators",
        cultivar_raw="Blue Dream",
        batch_or_lot="B-2026-001",
        panel="MA mandatory panel",
        parser_method="coa/pdf/v1",
        parser_confidence=0.9,
        normalization_confidence=0.9,
        analytes=[
            AnalyteResult(analyte_raw="THCA", result_raw="24.2",
                          result_state="numeric", result_numeric=24.2,
                          unit_raw="%", unit_normalized="%"),
            AnalyteResult(analyte_raw="Arsenic", result_raw="<0.05",
                          result_state="below_lod", unit_raw="ppm"),
        ],
    )


class ClassifyResultTestCase(unittest.TestCase):
    def test_numeric(self):
        self.assertEqual(classify_result("1.23"), ("numeric", 1.23))
        self.assertEqual(classify_result("1,230"), ("numeric", 1230.0))

    def test_nd_never_becomes_zero(self):
        for raw in ("ND", "Not Detected", "none detected", "N/D"):
            state, numeric = classify_result(raw)
            self.assertEqual(state, "nd")
            self.assertIsNone(numeric, f"{raw!r} must not carry a numeric value")

    def test_below_limit_never_becomes_zero(self):
        for raw in ("<0.05", "< 0.10"):
            state, numeric = classify_result(raw)
            self.assertEqual(state, "below_lod")
            self.assertIsNone(numeric)

    def test_blank_and_qualitative(self):
        self.assertEqual(classify_result(None), ("blank", None))
        self.assertEqual(classify_result("—"), ("blank", None))
        self.assertEqual(classify_result("Pass"), ("qualitative", None))

    def test_unknown_preserved(self):
        state, numeric = classify_result("trace amounts")
        self.assertEqual(state, "unknown")
        self.assertIsNone(numeric)


class NormalizeAnalyteTestCase(unittest.TestCase):
    def test_unambiguous_mapping(self):
        slug, display, confidence = normalize_analyte_name("β-Myrcene")
        self.assertEqual(slug, "beta-myrcene")
        self.assertGreaterEqual(confidence, 0.9)

    def test_matrix_decoration_stripped(self):
        slug, _, confidence = normalize_analyte_name("Arsenic (ppm) Raw Plant Material")
        self.assertEqual(slug, "arsenic")
        self.assertGreaterEqual(confidence, 0.9)

    def test_unknown_preserved_not_discarded(self):
        slug, display, confidence = normalize_analyte_name("Mystery Analyte 77")
        self.assertEqual(slug, "mystery-analyte-77")
        self.assertLess(confidence, 0.3)
        self.assertEqual(display, "Mystery Analyte 77")


class ValidationTestCase(unittest.TestCase):
    def test_valid_record_passes(self):
        self.assertEqual(validate_coa_record(_record()), [])

    def test_missing_required_fields(self):
        record = COARecord(jurisdiction="", source_document="", source_hash="",
                           source_retrieved_at="", analytes=[AnalyteResult(
                               analyte_raw="", result_raw="")])
        problems = validate_coa_record(record)
        self.assertTrue(any("missing required" in p for p in problems))
        self.assertTrue(any("empty analyte_raw" in p for p in problems))

    def test_numeric_state_requires_numeric_value(self):
        record = _record()
        record.analytes[0].result_state = "numeric"
        record.analytes[0].result_numeric = None
        self.assertTrue(any("numeric state without result_numeric" in p
                            for p in validate_coa_record(record)))

    def test_nd_with_numeric_value_forbidden(self):
        record = _record()
        record.analytes[1].result_state = "nd"
        record.analytes[1].result_numeric = 0.0  # forbidden conversion
        self.assertTrue(any("must never carry a converted zero" in p
                            for p in validate_coa_record(record)))

    def test_assert_valid_raises(self):
        with self.assertRaises(IngestError):
            assert_valid_coa_record(COARecord(
                jurisdiction="x", source_document="d", source_hash="h",
                source_retrieved_at="t", parser_method="p",
                analytes=[AnalyteResult(analyte_raw="a", result_raw="r",
                                        result_state="nd", result_numeric=0.0)]))


class PersistenceTestCase(unittest.TestCase):
    def test_round_trip_preserves_raw_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coa.csv"
            write_coa_csv(path, [_record()])
            rows = read_coa_csv(path)
            self.assertEqual(len(rows), 2)
            by_analyte = {row.analyte_raw: row for row in rows}
            self.assertEqual(by_analyte["THCA"].result_raw, "24.2")
            self.assertEqual(by_analyte["THCA"].result_numeric, 24.2)
            self.assertEqual(by_analyte["Arsenic"].result_raw, "<0.05")
            self.assertEqual(by_analyte["Arsenic"].result_numeric, None)
            self.assertEqual(by_analyte["Arsenic"].cultivar_raw, "Blue Dream")
            self.assertEqual(by_analyte["THCA"].jurisdiction, "massachusetts")


if __name__ == "__main__":
    unittest.main()
