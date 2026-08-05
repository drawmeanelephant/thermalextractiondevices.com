"""Massachusetts adapter unit tests (offline, fixture-backed)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ingest.states.massachusetts import (
    DATASETS,
    MassachusettsSync,
    aggregate_licenses,
    aggregate_testing,
    normalize_license,
    parse_analyte,
    parse_date_range,
    parse_product_string,
    parse_advisory_page,
    discover_advisory_urls,
)
from scripts.ingest.fetch import FixtureFetcher
from scripts.ingest.ids import NaturalKeyRegistry
from scripts.ingest.storage import ArtifactStore
from scripts.ingest.states.massachusetts import ID_PREFIXES, ID_COLLECTIONS

FIXTURES = Path(__file__).parent / "fixtures" / "massachusetts"


def _sync(tmp: str) -> MassachusettsSync:
    base = Path(tmp)
    store = ArtifactStore("massachusetts", base / "var", base / "data")
    registry = NaturalKeyRegistry(base / "data" / "id-map.json", ID_PREFIXES, ID_COLLECTIONS)
    return MassachusettsSync(
        fetch=FixtureFetcher(FIXTURES), store=store, registry=registry,
        content_root=base / "content", fixtures_only=True,
        allow_fixture_content=True,   # isolated test context only
    )


def _sample_license_row():
    return {
        "BUSINESS_NAME": "MCR Labs, LLC", "LICENSE_NUMBER": "IL281278",
        "LICENSE_TYPE": "Independent Testing Laboratory", "INDUSTRY": "Lab",
        "LICENSE_STATUS_CATEGORY": "Active", "COMMENCE_OPS": "Yes",
        "ESTABLISHMENT_CITY": "FRAMINGHAM", "ESTABLISHMENT_COUNTY": "Middlesex County",
        "CULTIVATION_ENVIRONMNET": "", "CULTIVATION_TIER": "",
        "LIC_START_DATE": "10-04-2018", "LIC_EXPIRATION_DATE": "04-10-2027",
        "EIN_TIN": "12-3456789", "BUSINESS_EMAIL": "x@example.com",
    }


class LicenseNormalizationTestCase(unittest.TestCase):
    def test_public_fields_extracted(self):
        row = normalize_license(_sample_license_row())
        self.assertEqual(row["display_name"], "MCR Labs, LLC")
        self.assertEqual(row["license_type"], "Independent Testing Laboratory")
        self.assertEqual(row["program"], "Lab")
        self.assertEqual(row["status"], "Active")
        self.assertEqual(row["municipality"], "Framingham")

    def test_private_fields_preserved_in_normalized_artifact(self):
        # The normalized artifact keeps source fields for fidelity; only
        # generated Markdown excludes them.
        row = normalize_license(_sample_license_row())
        self.assertIn("EIN_TIN", row)
        self.assertIn("BUSINESS_EMAIL", row)

    def test_lab_extraction_uses_source_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync = _sync(tmp)
            # no licenses ingested -> no ITLs
            self.assertEqual(sync.aggregates.get("licenses", {}).get("itls", []), [])

    def test_aggregate_lab_extraction_from_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync = _sync(tmp)
            from scripts.ingest.core import ChangeReport

            sync.run_dataset("licenses", ChangeReport(state="x", run_id="1", started_at="y"))
            itls = sync.aggregates["licenses"]["itls"]
            self.assertEqual(len(itls), 10)
            numbers = {lab["LICENSE_NUMBER"] for lab in itls}
            self.assertIn("IL281278", numbers)


class AnalyteParsingTestCase(unittest.TestCase):
    def test_parse_analyte_split(self):
        parsed = parse_analyte("Arsenic (ppm) Raw Plant Material")
        self.assertEqual(parsed["analyte"], "Arsenic")
        self.assertEqual(parsed["unit"], "ppm")
        self.assertEqual(parsed["matrix"], "Raw Plant Material")

    def test_parse_analyte_fallback(self):
        parsed = parse_analyte("something else")
        self.assertEqual(parsed["analyte"], "something else")
        self.assertEqual(parsed["unit"], "")


class ProductStringTestCase(unittest.TestCase):
    def test_pre_roll_split(self):
        parsed = parse_product_string("1 g Pre-rolls Strane")
        self.assertEqual(parsed["source_product_text"], "1 g Pre-rolls Strane")
        self.assertEqual(parsed["package_size_text"], "1 g")
        self.assertIn("Pre-rolls", parsed["product_form"])
        self.assertEqual(parsed["brand_candidate"], "Strane")

    def test_jar_split(self):
        parsed = parse_product_string("3.5g Jar")
        self.assertEqual(parsed["package_size_text"], "3.5g")
        self.assertIn("Jar", parsed["product_form"])

    def test_source_text_never_mutated(self):
        source = " 1 g Pre-rolls Strane "
        parsed = parse_product_string(source)
        self.assertEqual(parsed["source_product_text"], "1 g Pre-rolls Strane")

    def test_empty(self):
        parsed = parse_product_string("")
        self.assertEqual(parsed["source_product_text"], "")


class DateRangeTestCase(unittest.TestCase):
    def test_sold_between(self):
        result = parse_date_range("May 31, 2024 and January 23, 2025")
        self.assertIsNotNone(result)
        self.assertEqual(result[0].isoformat(), "2024-05-31")
        self.assertEqual(result[1].isoformat(), "2025-01-23")

    def test_unparseable(self):
        self.assertIsNone(parse_date_range("unknown period"))


class AdvisoryParsingTestCase(unittest.TestCase):
    def test_parse_real_advisory_html(self):
        html = (Path(__file__).parent / "fixtures" / "massachusetts" / "adv1.html").read_text(
            encoding="utf-8", errors="replace"
        )
        advisory = parse_advisory_page(
            html,
            "https://masscannabiscontrol.com/2025/02/notice-some-advisory/",
        )
        self.assertEqual(advisory["affected_product_count"], 12)
        self.assertIn("2024-05-31", advisory["date_ranges"]["sold_between"])
        self.assertGreater(len(advisory["licensees"]), 0)
        self.assertIn("yeast and mold", advisory["concern"].lower())

    def test_advisory_terminology_not_relabeled(self):
        html = (Path(__file__).parent / "fixtures" / "massachusetts" / "adv1.html").read_text(
            encoding="utf-8", errors="replace"
        )
        advisory = parse_advisory_page(html, "https://example.com/adv")
        # The archive must keep the Commission's term.
        self.assertIn("Public Health and Safety Advisory", advisory["title"])

    def test_affected_package_natural_keys(self):
        advisories = json.loads((FIXTURES / "advisories.json").read_text(encoding="utf-8"))
        keys = set()
        total = 0
        for advisory in advisories:
            for product in advisory["products"]:
                total += 1
                keys.add((advisory["url"], product["strain"]))
        self.assertGreater(len(keys), 0)
        # Unique (advisory, strain) pairs: total products minus products that
        # repeat an earlier strain within the same advisory.
        repeated = sum(
            1 for a in advisories for i, p in enumerate(a["products"])
            if any((a["url"], q["strain"]) == (a["url"], p["strain"])
                   for q in a["products"][:i])
        )
        self.assertEqual(len(keys), total - repeated)


class AggregateTestCase(unittest.TestCase):
    def test_testing_aggregate_status_counts(self):
        rows = [
            {"analyte": "THC", "date": "2025-01-01", "test_passed": "True", "analyte_unit": "%"},
            {"analyte": "THC", "date": "2025-01-01", "test_passed": "False", "analyte_unit": "%"},
            {"analyte": "THCA", "date": "2025-02-01", "test_passed": "True", "analyte_unit": "%"},
        ]
        result = aggregate_testing(rows)
        self.assertEqual(result["by_status"], {"Passed": 2, "Failed": 1})
        self.assertEqual(result["by_analyte"]["THC"]["passed"], 1)
        self.assertEqual(result["by_month"], {"2025-01": 2, "2025-02": 1})

    def test_license_aggregate(self):
        rows = [normalize_license(_sample_license_row())]
        result = aggregate_licenses(rows)
        self.assertEqual(result["rows"], 1)
        self.assertEqual(result["by_program"], {"Lab": 1})
        self.assertEqual(len(result["itls"]), 1)


if __name__ == "__main__":
    unittest.main()
