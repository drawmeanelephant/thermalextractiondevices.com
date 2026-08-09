"""Validation-guard tests: privacy allowlist scan and relation targets."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ingest.core import PrivacyViolationError
from scripts.ingest.validation import (
    PrivacySpec,
    assert_clean,
    collect_entity_ids,
    scan_text,
    validate_relations,
)


def _spec() -> PrivacySpec:
    return PrivacySpec(state="test")


class PrivacyScanTestCase(unittest.TestCase):
    def test_ein_detected(self):
        findings = scan_text("EIN: 12-3456789", _spec())
        self.assertTrue(any(f.pattern == "ein/tin" for f in findings))

    def test_email_detected(self):
        findings = scan_text("contact joe@example.com today", _spec())
        self.assertTrue(any(f.pattern == "email" for f in findings))

    def test_phone_detected(self):
        findings = scan_text("call 617-555-0199 now", _spec())
        self.assertTrue(any(f.pattern == "phone" for f in findings))

    def test_street_address_detected(self):
        findings = scan_text("at 1006 Bennington Street Boston, MA 02128", _spec())
        self.assertTrue(any(f.pattern == "street-address" for f in findings))

    def test_field_marker_detected(self):
        findings = scan_text("The EIN_TIN column was excluded", _spec())
        self.assertTrue(any(f.pattern.startswith("field:") for f in findings))

    def test_clean_text_passes(self):
        findings = scan_text("MCR Labs, LLC · license IL281278 · Framingham", _spec())
        self.assertEqual(findings, [])
        assert_clean(findings)  # no raise

    def test_assert_clean_raises(self):
        findings = scan_text("EIN: 12-3456789", _spec())
        with self.assertRaises(PrivacyViolationError):
            assert_clean(findings)

    def test_judicial_court_not_street_address(self):
        # Regression: "2018 Constitutional Court ruling" / "overturned in
        # court" (legal prose) must not be flagged as a street address.
        findings = scan_text(
            "Following the 2018 Constitutional Court ruling, the measure was "
            "overturned in court.",
            _spec(),
        )
        self.assertFalse(any(f.pattern == "street-address" for f in findings))

    def test_court_street_still_detected(self):
        # "123 Court Street" is a real address and still matches via Street.
        findings = scan_text("licensed at 123 Court Street Boston", _spec())
        self.assertTrue(any(f.pattern == "street-address" for f in findings))

    def test_legal_citation_not_coordinate(self):
        # Regression: "MCL 333.27901 et seq." must not match coordinates via
        # a suffix of the number ("33.27901" inside "333.27901").
        findings = scan_text("Testing rules per MCL 333.27901 et seq.", _spec())
        self.assertFalse(any(f.pattern == "coordinates" for f in findings))

    def test_coordinate_pair_still_detected(self):
        findings = scan_text("grow site at 44.12345, -71.98765", _spec())
        self.assertTrue(any(f.pattern == "coordinates" for f in findings))


class RelationValidationTestCase(unittest.TestCase):
    def test_broken_relation_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text(
                "---\nid: a\nparent: x\nrelations: [relates_to=missing/TED-9999]\n---\n"
            )
            broken = validate_relations(root)
            self.assertTrue(any("missing/TED-9999" in b for b in broken))

    def test_valid_relations_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("---\nid: a\n---\n")
            (root / "b.md").write_text(
                "---\nid: b\nparent: x\nrelations: [relates_to=a]\n---\n"
            )
            self.assertEqual(validate_relations(root), [])
            self.assertIn("a", collect_entity_ids(root))


if __name__ == "__main__":
    unittest.main()
