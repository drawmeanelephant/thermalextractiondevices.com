"""Storage-layer tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ingest.storage import ArtifactStore, sha256_file


def _store(tmp: str) -> ArtifactStore:
    return ArtifactStore(state="massachusetts",
                         working_root=Path(tmp) / "var",
                         durable_root=Path(tmp) / "data")


class StorageTestCase(unittest.TestCase):
    def test_snapshot_paths_are_immutable_by_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = _store(tmp)
            a = store.raw_snapshot_path("licenses", "abc123", ".csv")
            b = store.raw_snapshot_path("licenses", "abc123", ".csv")
            c = store.raw_snapshot_path("licenses", "def456", ".csv")
            self.assertEqual(a, b)
            self.assertNotEqual(a, c)
            self.assertIn("abc123", a.name)

    def test_manifest_roundtrip_preserves_prior_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = _store(tmp)
            store.record_snapshot(
                "licenses", "https://example.org/lic.csv",
                raw_sha256="sha1", raw_path=store.raw_snapshot_path("licenses", "sha1"),
                content_type="text/csv", size_bytes=10, retrieved_at="2026-01-01T00:00:00Z",
                row_count=5,
            )
            store.record_snapshot(
                "licenses", "https://example.org/lic.csv",
                raw_sha256="sha2", raw_path=store.raw_snapshot_path("licenses", "sha2"),
                content_type="text/csv", size_bytes=12, retrieved_at="2026-02-01T00:00:00Z",
                row_count=6,
            )
            manifest = store.read_manifest()
            entries = manifest["datasets"]["licenses"]
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[1]["prior_snapshot_checksum"], "sha1")
            latest = store.latest_snapshot("licenses")
            self.assertEqual(latest["raw_sha256"], "sha2")

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.bin"
            path.write_bytes(b"hello")
            self.assertEqual(
                sha256_file(path),
                "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
            )

    def test_durable_json_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = _store(tmp)
            path = store.write_durable_json("source-catalog.json", {"a": 1})
            self.assertTrue(path.is_file())
            self.assertEqual(json.loads(path.read_text())["a"], 1)


if __name__ == "__main__":
    unittest.main()
