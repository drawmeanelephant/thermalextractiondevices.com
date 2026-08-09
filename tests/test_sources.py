"""Jurisdiction source manifest tests (scripts/ingest/sources.py)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ingest.sources import (
    SourceEntry,
    SourceManifest,
    build_stub_manifest,
    read_manifest,
    render_manifest_markdown,
    write_manifest,
)


class SourceManifestTestCase(unittest.TestCase):
    def test_valid_entry_passes(self):
        entry = SourceEntry(
            name="License registry", authority="Regulator",
            url="https://example.gov/licenses", source_class="licensing-registry",
            machine_readable=True, format="csv",
        )
        self.assertEqual(entry.validate(), [])

    def test_invalid_entry(self):
        entry = SourceEntry(name="", authority="", url="not-a-url",
                            source_class="bogus", retrieval_method="magic",
                            archival_strategy="nope")
        problems = entry.validate()
        self.assertTrue(any("name is required" in p for p in problems))
        self.assertTrue(any("authority is required" in p for p in problems))
        self.assertTrue(any("must be http(s)" in p for p in problems))
        self.assertTrue(any("unknown source_class" in p for p in problems))

    def test_stub_must_not_claim_sources(self):
        stub = build_stub_manifest("oregon")
        self.assertFalse(stub.researched)
        self.assertEqual(stub.sources, [])
        self.assertEqual(stub.validate(), [])

    def test_researched_manifest_requires_sources_and_date(self):
        manifest = SourceManifest(state="x", researched=True, sources=[])
        problems = manifest.validate()
        self.assertTrue(any("has no sources" in p for p in problems))
        manifest = SourceManifest(state="x", researched=True, updated_date="",
                                  sources=[SourceEntry(name="a", authority="b",
                                                       url="https://x.gov")])
        problems = manifest.validate()
        self.assertTrue(any("missing updated_date" in p for p in problems))

    def test_stub_with_sources_fails(self):
        manifest = SourceManifest(
            state="x", researched=False,
            sources=[SourceEntry(name="a", authority="b", url="https://x.gov")])
        self.assertTrue(any("must not list sources" in p
                            for p in manifest.validate()))

    def test_round_trip_json(self):
        manifest = SourceManifest(
            state="california", regulator_name="DCC", researched=True,
            updated_date="2026-08-09",
            sources=[SourceEntry(name="Registry", authority="DCC",
                                 url="https://search.example.gov",
                                 source_class="licensing-registry",
                                 machine_readable=True, format="api")],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ca.json"
            write_manifest(path, manifest)
            reloaded = read_manifest(path)
            self.assertEqual(reloaded.state, "california")
            self.assertEqual(reloaded.sources[0].name, "Registry")
            self.assertTrue(reloaded.sources[0].machine_readable)

    def test_render_markdown(self):
        manifest = SourceManifest(
            state="ma", researched=True, updated_date="2026-08-09",
            sources=[SourceEntry(name="A | B", authority="CCC",
                                 url="https://x.gov", source_class="recalls")],
        )
        text = render_manifest_markdown(manifest)
        self.assertIn("A \\| B", text)
        self.assertIn("Source Manifest — ma", text)


if __name__ == "__main__":
    unittest.main()
