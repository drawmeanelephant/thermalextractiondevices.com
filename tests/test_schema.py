"""Schema-guard tests."""

from __future__ import annotations

import io
import unittest
from pathlib import Path

from scripts.ingest.core import (
    DateRegressionError,
    DuplicateKeyError,
    EmptyOutputError,
    IngestError,
    RowCollapseError,
    SchemaDriftError,
)
from scripts.ingest.schema import (
    SchemaSpec,
    check_date_regression,
    check_duplicate_keys,
    check_fully_duplicate_rows,
    check_row_collapse,
    check_source_staleness,
    parse_csv_bytes,
    stream_csv,
)


class SchemaTestCase(unittest.TestCase):
    def test_required_columns_disappear(self):
        spec = SchemaSpec(name="t", required=["A", "B"])
        with self.assertRaises(SchemaDriftError):
            spec.check_headers(["A", "C"])

    def test_required_columns_present(self):
        spec = SchemaSpec(name="t", required=["A", "B"])
        spec.check_headers(["A", "B", "C"])  # no raise

    def test_numeric_type_drift_fails(self):
        spec = SchemaSpec(name="t", column_types={"RESULT": "number"})
        # Numeric drift is a hard failure (raise), not a warning.
        with self.assertRaises(SchemaDriftError):
            spec.check_types([{"RESULT": "1.5"}, {"RESULT": "abc"}])
        with self.assertRaises(SchemaDriftError):
            spec.check_types([{"RESULT": "abc"}])

    def test_date_type_drift_warns(self):
        spec = SchemaSpec(name="t", column_types={"DATE": "date"})
        warnings = spec.check_types([{"DATE": "2025-06-24"}, {"DATE": "not-a-date"}])
        self.assertEqual(len(warnings), 1)

    def test_row_collapse_guard(self):
        spec = SchemaSpec(name="t", row_collapse_threshold=0.5)
        warnings = check_row_collapse(spec, current=100, prior=200)
        self.assertEqual(warnings, [])
        with self.assertRaises(RowCollapseError):
            check_row_collapse(spec, current=80, prior=200)

    def test_date_regression_warns_on_small_backward_move(self):
        warnings = check_date_regression("2026-06-01", "2026-05-20")
        self.assertEqual(len(warnings), 1)
        self.assertIn("backward", warnings[0])

    def test_date_regression_fails_without_clarification(self):
        with self.assertRaises(DateRegressionError):
            check_date_regression("2026-06-01", "2025-01-01")

    def test_date_regression_allowed_with_source_clarification(self):
        warnings = check_date_regression("2026-06-01", "2025-01-01",
                                         has_clarification=True)
        self.assertEqual(len(warnings), 1)

    def test_date_regression_forward_is_clean(self):
        self.assertEqual(check_date_regression("2025-01-01", "2026-06-01"), [])

    def test_source_staleness_forward_is_clean(self):
        warnings = check_source_staleness(
            "Fri, 10 Apr 2026 20:25:36 GMT", "Sat, 11 Apr 2026 00:00:00 GMT"
        )
        self.assertEqual(warnings, [])

    def test_source_staleness_older_copy_fails_closed(self):
        # An obsolete pre-correction release (older file date) must not
        # silently replace the corrected snapshot without a clarification.
        with self.assertRaises(DateRegressionError):
            check_source_staleness(
                "Fri, 10 Apr 2026 20:25:36 GMT", "Tue, 10 Mar 2026 12:00:00 GMT"
            )

    def test_source_staleness_allowed_with_clarification(self):
        # The 2025 testing dataset carries a recognized correction notice, so
        # a backward file date is tolerated as a non-blocking warning.
        warnings = check_source_staleness(
            "Fri, 10 Apr 2026 20:25:36 GMT", "Tue, 10 Mar 2026 12:00:00 GMT",
            has_clarification=True,
        )
        self.assertEqual(len(warnings), 1)
        self.assertIn("backward", warnings[0])

    def test_source_staleness_unparseable_dates_skip(self):
        self.assertEqual(check_source_staleness("2026-07 (per catalog)", None), [])

    def test_empty_output_guard(self):
        spec = SchemaSpec(name="t", min_rows=1)
        with self.assertRaises(EmptyOutputError):
            check_row_collapse(spec, current=0, prior=None)

    def test_duplicate_keys_guard(self):
        rows = [{"id": "a"}, {"id": "b"}, {"id": "a"}]
        with self.assertRaises(DuplicateKeyError):
            check_duplicate_keys(rows, ["id"], "t")

    def test_duplicate_keys_warn_policy(self):
        """Non-keyed large datasets (e.g. testing results) warn instead of
        failing on partial-key repeats while still rejecting full-row dups."""
        rows = [{"id": "a", "v": "1"}, {"id": "a", "v": "1"}]
        warnings = check_duplicate_keys(rows, ["id"], "t", policy="warn")
        self.assertEqual(len(warnings), 1)
        self.assertIn("duplicate", warnings[0])
        with self.assertRaises(DuplicateKeyError):
            check_fully_duplicate_rows(rows, "t")
        # Distinct keys are clean; full-row dup check also passes.
        rows2 = [{"id": "a", "v": "1"}, {"id": "b", "v": "2"}]
        self.assertEqual(check_duplicate_keys(rows2, ["id"], "t", policy="warn"), [])
        self.assertEqual(check_fully_duplicate_rows(rows2, "t"), [])

    def test_parse_csv_with_bom(self):
        data = b"\xef\xbb\xbfa,b\n1,2\n3,4\n"
        headers, rows = parse_csv_bytes(data)
        self.assertEqual(headers, ["a", "b"])
        self.assertEqual(len(rows), 2)

    def test_truncated_csv_rejected(self):
        data = b"a,b\n1,2\n3,4"  # no trailing newline
        with self.assertRaises(IngestError):
            parse_csv_bytes(data)

    def test_utf8_decode_failure(self):
        with self.assertRaises(IngestError):
            parse_csv_bytes(b"\xff\xfe\x00a,b\n")

    def test_stream_csv_yields_stripped_rows(self):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as handle:
            handle.write("a,b\r\n1, 2 \r\n")
            path = Path(handle.name)
        try:
            rows = list(stream_csv(path))
            self.assertEqual(rows, [{"a": "1", "b": "2"}])
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
