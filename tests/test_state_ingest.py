"""End-to-end fixture-only ingest tests (no network)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ingest.core import ChangeReport, IngestError
from scripts.ingest.fetch import FixtureFetcher
from scripts.ingest.ids import NaturalKeyRegistry
from scripts.ingest.storage import ArtifactStore
from scripts.ingest.states.massachusetts import (
    DATASETS,
    ID_COLLECTIONS,
    ID_PREFIXES,
    MassachusettsSync,
    PRIVACY_SPEC,
)
from scripts.ingest.validation import scan_directory, validate_relations

FIXTURES = Path(__file__).parent / "fixtures" / "massachusetts"
GENERATED_COLLECTIONS = [
    "jurisdictions", "licenses", "organizations", "testing-laboratories",
    "contaminants", "datasets", "requirements", "safety-advisories",
    "affected-products",
]


def run_fixture_sync(tmp: str) -> MassachusettsSync:
    base = Path(tmp)
    store = ArtifactStore("massachusetts", base / "var", base / "data")
    registry = NaturalKeyRegistry(base / "data" / "id-map.json", ID_PREFIXES, ID_COLLECTIONS)
    sync = MassachusettsSync(
        fetch=FixtureFetcher(FIXTURES), store=store, registry=registry,
        content_root=base / "content", fixtures_only=True,
        allow_fixture_content=True,
    )
    report = ChangeReport(state="massachusetts", run_id="test", started_at="x")
    for slug in DATASETS:
        sync.run_dataset(slug, report)
    self_ = None
    advisories = sync.discover_advisories()
    sync.generate_content(report, advisories)
    registry.save()
    return sync, report


class EndToEndTestCase(unittest.TestCase):
    def test_all_datasets_ingest_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync, report = run_fixture_sync(tmp)
            self.assertEqual(report.errors, [], report.errors)
            self.assertEqual(len(report.datasets), len(DATASETS))

    def test_content_generated_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync, report = run_fixture_sync(tmp)
            content = sync.content_root
            self.assertTrue((content / "jurisdictions.md").exists())
            self.assertTrue((content / "safety-advisories.md").exists())
            self.assertTrue((content / "jurisdictions" / "TJUR-0001.md").exists())
            lab_files = list((content / "testing-laboratories").glob("TTLB-*.md"))
            self.assertGreaterEqual(len(lab_files), 10)
            advisory_files = list((content / "safety-advisories").glob("TSAD-*.md"))
            self.assertEqual(len(advisory_files), 3)

    def test_id_map_persisted_and_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync, report = run_fixture_sync(tmp)
            path = Path(tmp) / "data" / "id-map.json"
            self.assertTrue(path.is_file())
            data = json.loads(path.read_text())
            self.assertGreater(len(data["mappings"]), 50)
            # Second run reuses the same IDs.
            base = Path(tmp)
            store = ArtifactStore("massachusetts", base / "var2", base / "data2")
            registry2 = NaturalKeyRegistry(path, ID_PREFIXES, ID_COLLECTIONS)
            sync2 = MassachusettsSync(
                fetch=FixtureFetcher(FIXTURES), store=store, registry=registry2,
                content_root=base / "content2", fixtures_only=True,
                allow_fixture_content=True,
            )
            report2 = ChangeReport(state="massachusetts", run_id="test2", started_at="x")
            for slug in DATASETS:
                sync2.run_dataset(slug, report2)
            advisories = sync2.discover_advisories()
            sync2.generate_content(report2, advisories)
            jid = registry2.entity_id("jurisdiction", "massachusetts")
            self.assertEqual(jid, "jurisdictions/TJUR-0001")

    def test_privacy_scan_clean_on_generated_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync, report = run_fixture_sync(tmp)
            findings = scan_directory(sync.content_root, PRIVACY_SPEC,
                                      only_collections=GENERATED_COLLECTIONS)
            self.assertEqual(findings, [],
                             [str(f) for f in findings[:5]])

    def test_relations_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync, report = run_fixture_sync(tmp)
            broken = validate_relations(sync.content_root)
            self.assertEqual(broken, [], broken[:5])

    def test_durable_artifacts_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync, report = run_fixture_sync(tmp)
            durable = Path(tmp) / "data"
            for name in ("manifest.json", "source-catalog.json", "schema-report.md",
                         "privacy-spec.md", "affected-packages.csv", "cultivar-candidates.csv"):
                self.assertTrue((durable / name).is_file(), name)
            manifest = json.loads((durable / "manifest.json").read_text())
            self.assertIn("licenses", manifest["datasets"])
            record = manifest["datasets"]["licenses"][-1]
            self.assertIn("raw_sha256", record)
            self.assertIn("official_source_url", record)
            self.assertIn("prior_snapshot_checksum", record)

    def test_fixture_content_guard_blocks_generation(self):
        """Fixture/synthetic records must not generate publishable content
        unless an explicit development flag is supplied."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            store = ArtifactStore("massachusetts", base / "var", base / "data")
            registry = NaturalKeyRegistry(base / "data" / "id-map.json", ID_PREFIXES, ID_COLLECTIONS)
            sync = MassachusettsSync(
                fetch=FixtureFetcher(FIXTURES), store=store, registry=registry,
                content_root=base / "content", fixtures_only=True,
            )
            report = ChangeReport(state="massachusetts", run_id="guard", started_at="x")
            # Snapshot/manifest writes are blocked in fixture mode.
            with self.assertRaises(IngestError):
                sync.run_dataset("licenses", report)
            # Content generation is blocked too.
            with self.assertRaises(IngestError):
                sync.generate_content(report, [])
            self.assertFalse((base / "content").exists())
            self.assertFalse(store.read_manifest()["datasets"])

    def test_manifest_keeps_prior_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            store = ArtifactStore("massachusetts", base / "var", base / "data")
            registry = NaturalKeyRegistry(base / "data" / "id-map.json", ID_PREFIXES, ID_COLLECTIONS)
            sync = MassachusettsSync(
                fetch=FixtureFetcher(FIXTURES), store=store, registry=registry,
                content_root=base / "content", fixtures_only=True,
                allow_fixture_content=True,
            )
            report = ChangeReport(state="massachusetts", run_id="r1", started_at="x")
            sync.run_dataset("licenses", report)
            # Second run: same checksum -> unchanged, no new snapshot record.
            report2 = ChangeReport(state="massachusetts", run_id="r2", started_at="x")
            sync.run_dataset("licenses", report2)
            entries = store.read_manifest()["datasets"]["licenses"]
            self.assertEqual(len(entries), 1)


if __name__ == "__main__":
    unittest.main()
