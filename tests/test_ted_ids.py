"""Regression tests for scripts/ted_ids.py ID immutability (id-policy)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ted_ids import (
    MigrationError,
    build_records,
    state_map_reservations,
    validate_records,
    validate_state_maps,
    write_map,
)


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


def make_state_map(path: Path, entity_type: str, natural_key: str, entity_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    collection = entity_id.split("/", 1)[0]
    path.write_text(json.dumps({
        "version": 1,
        "state": None,
        "mappings": [{
            "entity_type": entity_type,
            "natural_key": natural_key,
            "entity_id": entity_id,
            "label": "",
            "collection": collection,
        }],
    }) + "\n", encoding="utf-8")


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

    def test_global_allocator_skips_historical_state_reservation(self):
        """A state-map claim remains reserved even after its page disappears."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "content"
            make_page(root, "datasets.md", "datasets")
            make_page(root, "datasets/TDTS-0001.md", "datasets/TDTS-0001")
            state_map = base / "data" / "state-a" / "id-map.json"
            make_state_map(state_map, "dataset", "STATE-A:historical", "datasets/TDTS-0002")
            reservations = state_map_reservations([state_map])

            make_page(root, "datasets/new-dataset.md", None)
            records = build_records(root, reserved_form_ids=reservations)
            validate_records(records)
            by_source = {str(r["source"]): str(r["id"]) for r in records}
            self.assertEqual(by_source["datasets/new-dataset.md"], "datasets/TDTS-0003")

    def test_concurrent_state_allocations_are_rejected_as_a_collision(self):
        """Two agents seeing the same predecessor must not merge silently."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)

            def allocate_for(agent: str) -> tuple[list[dict[str, str | None]], Path]:
                root = base / agent / "content"
                make_page(root, "datasets.md", "datasets")
                make_page(root, "datasets/TDTS-0001.md", "datasets/TDTS-0001")
                make_page(root, f"datasets/{agent}.md", None)
                allocated = build_records(root)
                state_map = base / agent / "data" / "id-map.json"
                make_state_map(state_map, "dataset", f"{agent}:new", "datasets/TDTS-0002")
                return allocated, state_map

            first, first_map = allocate_for("agent-a")
            second, second_map = allocate_for("agent-b")
            first_id = next(str(r["id"]) for r in first if r["source"] == "datasets/agent-a.md")
            second_id = next(str(r["id"]) for r in second if r["source"] == "datasets/agent-b.md")
            self.assertEqual(first_id, "datasets/TDTS-0002")
            self.assertEqual(second_id, "datasets/TDTS-0002")

            with self.assertRaisesRegex(MigrationError, "state ID collision"):
                validate_state_maps([first_map, second_map])


if __name__ == "__main__":
    unittest.main()
