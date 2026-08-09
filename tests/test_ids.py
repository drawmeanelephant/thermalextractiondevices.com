"""Stable ID registry tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ingest.core import IdCollisionError, IdMappingChangedError
from scripts.ingest.ids import NaturalKeyRegistry

PREFIXES = {"dataset": "TDAT", "license": "TLIC", "advisory": "TSAD"}
COLLECTIONS = {"dataset": "datasets", "license": "licenses", "advisory": "safety-advisories"}


class IdRegistryTestCase(unittest.TestCase):
    def test_deterministic_allocation_and_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            a = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            first = a.id_for("dataset", "licenses", label="License tracker")
            second = a.id_for("dataset", "testing", label="Testing")
            a.save()

            b = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            self.assertEqual(b.id_for("dataset", "licenses"), first)
            self.assertEqual(b.id_for("dataset", "testing"), second)
            self.assertEqual(first, "datasets/TDAT-0001")
            self.assertEqual(second, "datasets/TDAT-0002")

    def test_per_entity_type_numbering(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = NaturalKeyRegistry(Path(tmp) / "id-map.json", PREFIXES, COLLECTIONS)
            self.assertEqual(registry.id_for("license", "MA:1"), "licenses/TLIC-0001")
            self.assertEqual(registry.id_for("advisory", "MA:adv:x"), "safety-advisories/TSAD-0001")
            self.assertEqual(registry.id_for("license", "MA:2"), "licenses/TLIC-0002")

    def test_persisted_mapping_change_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            registry = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            registry.id_for("dataset", "licenses")
            registry.save()
            # Tamper: same natural key now maps to a different entity id.
            data = json.loads(path.read_text())
            for item in data["mappings"]:
                item["entity_id"] = "datasets/TDAT-0099"
            path.write_text(json.dumps(data))
            with self.assertRaises(IdMappingChangedError):
                NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)

    def test_allocated_id_collision_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            data = {"version": 1, "state": None, "mappings": [
                {"entity_type": "dataset", "natural_key": "a",
                 "entity_id": "datasets/TDAT-0001", "label": "", "collection": "datasets"},
            ]}
            path.write_text(json.dumps(data))
            registry = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            # TDAT-0001 is taken; next free is TDAT-0002, so no collision for key "b".
            self.assertEqual(registry.id_for("dataset", "b"), "datasets/TDAT-0002")

    def test_labels_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            registry = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            registry.id_for("dataset", "x", label="Human label")
            registry.save()
            reloaded = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            self.assertEqual(reloaded.label_for("dataset", "x"), "Human label")

    def test_seed_avoids_collision_with_existing_entities(self):
        """A second state sharing the collections must not reuse numeric IDs
        already taken by existing content (e.g. California's committed pages)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            registry = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            registry.seed_from_entity_ids([
                "datasets/TDAT-0001", "datasets/TDAT-0004",   # existing CA datasets
                "licenses/TLIC-0001",                          # existing CA license
                "jurisdictions/TJUR-0001",                     # existing CA jurisdiction
                "datasets",                                    # trunk; ignored
                "not-an-id",                                   # malformed; ignored
                "safety-advisories/TSAD-0009",                 # registered advisory type
            ])
            self.assertEqual(registry.id_for("dataset", "MA:licenses"), "datasets/TDAT-0005")
            self.assertEqual(registry.id_for("license", "MA:lic:x"), "licenses/TLIC-0002")
            # Registered types are bumped by seeding too.
            self.assertEqual(registry.id_for("advisory", "MA:adv:y"), "safety-advisories/TSAD-0010")

    def test_seed_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            registry = NaturalKeyRegistry(path, PREFIXES, COLLECTIONS)
            existing = ["datasets/TDAT-0001", "datasets/TDAT-0004"]
            registry.seed_from_entity_ids(existing)
            registry.seed_from_entity_ids(existing)
            self.assertEqual(registry.id_for("dataset", "x"), "datasets/TDAT-0005")


if __name__ == "__main__":
    unittest.main()
