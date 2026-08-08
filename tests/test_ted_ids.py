"""Regression tests for scripts/ted_ids.py ID immutability (id-policy)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ted_ids import build_records, validate_records, write_map


def make_page(root: Path, rel: str, entity_id: str | None) -> Path:
    """Write a minimal Boris page with (optionally) a canonical frontmatter id."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    if entity_id:
        lines.append(f"id: {entity_id}")
    lines.append("title: Record")
    lines.append("---")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class TedIdsImmutabilityTests(unittest.TestCase):
    def test_pending_satellite_preserves_canonical_id(self):
        # A satellite whose frontmatter already carries a valid canonical form
        # ID (but whose filename is not form-prefixed) must keep that ID
        # instead of being renumbered by the allocator.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "content"
            make_page(root, "devices.md", "devices")
            make_page(root, "devices/e-nano-og.md", "devices/TED-0011")
            make_page(root, "devices/tinymight.md", "devices/TED-0008")

            records = build_records(root)
            validate_records(records)
            by_source = {str(r["source"]): str(r["id"]) for r in records}
            self.assertEqual(by_source["devices/e-nano-og.md"], "devices/TED-0011")
            self.assertEqual(by_source["devices/tinymight.md"], "devices/TED-0008")

    def test_inserting_files_never_renumbers_existing_satellites(self):
        # Inserting a new pending satellite that sorts earlier alphabetically
        # must not shift the canonical IDs of existing satellites: the new
        # record takes the next free number instead.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "content"
            make_page(root, "devices.md", "devices")
            make_page(root, "devices/a.md", "devices/TED-0001")
            make_page(root, "devices/z.md", "devices/TED-0002")

            records = build_records(root)
            validate_records(records)
            map_path = Path(tmp) / "id-map.jsonl"
            write_map(map_path, records)
            legacy_by_source = {str(r["source"]): str(r["legacy_id"]) for r in records}

            # New file sorts between a.md and z.md; it must take the next free
            # number (TED-0003) without renumbering a.md or z.md.
            make_page(root, "devices/m.md", None)
            records = build_records(root, legacy_by_source)
            validate_records(records)
            by_source = {str(r["source"]): str(r["id"]) for r in records}
            self.assertEqual(by_source["devices/a.md"], "devices/TED-0001")
            self.assertEqual(by_source["devices/z.md"], "devices/TED-0002")
            self.assertEqual(by_source["devices/m.md"], "devices/TED-0003")

    def test_preserved_id_not_colliding_with_form_named_file(self):
        # A preserved pending ID must not collide with a form-named file's
        # ID in the same collection; validation must still pass.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "content"
            make_page(root, "devices.md", "devices")
            make_page(root, "devices/TED-0005.md", "devices/TED-0005")
            make_page(root, "devices/e-nano-og.md", "devices/TED-0011")

            records = build_records(root)
            validate_records(records)
            ids = [str(r["id"]) for r in records]
            self.assertEqual(len(ids), len(set(ids)))
            by_source = {str(r["source"]): str(r["id"]) for r in records}
            self.assertEqual(by_source["devices/e-nano-og.md"], "devices/TED-0011")


if __name__ == "__main__":
    unittest.main()
