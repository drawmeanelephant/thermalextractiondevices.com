import json
import tempfile
import unittest
from pathlib import Path

from scripts.name_rag_bundle import create_named_bundle


class NameRagBundleTests(unittest.TestCase):
    def test_names_packs_by_corpus_and_content_range(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "working"
            target = root / "upload"
            source.mkdir()
            (source / "working-1.md").write_text("pack one\n", encoding="utf-8")
            (source / "working-2.md").write_text("pack two\n", encoding="utf-8")
            manifest = {
                "format": "boris-rag",
                "schema_version": 2,
                "boris_version": "0.8.1",
                "mode": "working",
                "scope": "",
                "upload_files": [
                    {"path": "working-1.md", "bytes": 9, "documents": 2},
                    {"path": "working-2.md", "bytes": 9, "documents": 2},
                ],
                "documents": [
                    {"source": "devices.md", "pack": "working-1.md"},
                    {"source": "devices/TED-0001.md", "pack": "working-1.md"},
                    {"source": "guides.md", "pack": "working-2.md"},
                    {"source": "reference/TREF-0001.md", "pack": "working-2.md"},
                ],
            }
            (source / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            filenames = create_named_bundle(
                source, target, "Thermal Extraction Devices / Archive"
            )

            self.assertEqual(
                filenames,
                [
                    "thermal-extraction-devices-archive-working-context-01-of-02-devices.md",
                    "thermal-extraction-devices-archive-working-context-02-of-02-guides-to-reference.md",
                ],
            )
            self.assertEqual(
                (target / filenames[0]).read_text(encoding="utf-8"), "pack one\n"
            )
            rewritten = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [entry["path"] for entry in rewritten["upload_files"]], filenames
            )
            self.assertEqual(
                {document["pack"] for document in rewritten["documents"]},
                set(filenames),
            )

    def test_rejects_complete_corpus_and_path_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "working"
            target = root / "upload"
            source.mkdir()
            (source / "manifest.json").write_text(
                json.dumps(
                    {
                        "mode": "complete",
                        "upload_files": [{"path": "working-1.md"}],
                        "documents": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "working-mode"):
                create_named_bundle(source, target, "ted")

            (source / "manifest.json").write_text(
                json.dumps(
                    {
                        "mode": "working",
                        "upload_files": [{"path": "../working-1.md"}],
                        "documents": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "escapes"):
                create_named_bundle(source, target, "ted")


if __name__ == "__main__":
    unittest.main()
