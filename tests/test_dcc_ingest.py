"""Tests for deterministic DCC organization relation generation."""

from __future__ import annotations

import unittest

from scripts.dcc_ingest import build_organization_relations


class OrganizationRelationTests(unittest.TestCase):
    def test_unique_license_matches_add_lab_and_recall_edges(self):
        organizations = [{"name": "Lab Org", "license_number": "C8-0001"}]
        laboratories = [{"license_number": "C8-0001"}]
        recall_index = [{"id": "recall-1"}]
        recall_details = [{
            "id": "recall-1",
            "fields": {"Legal Business License Number": "C8-0001"},
        }]

        relations = build_organization_relations(
            organizations,
            laboratories,
            {"C8-0001": "TSTL-0001"},
            recall_index,
            recall_details,
            {"recall-1": "TRCL-0001"},
        )

        self.assertEqual(
            relations["Lab Org"],
            [
                "relates_to=recalls/TRCL-0001",
                "relates_to=testing-laboratories/TSTL-0001",
            ],
        )

    def test_ambiguous_license_matches_are_suppressed(self):
        organizations = [
            {"name": "First Org", "license_number": "C8-0002"},
            {"name": "Second Org", "license_number": "C8-0002"},
        ]
        laboratories = [{"license_number": "C8-0002"}]

        relations = build_organization_relations(
            organizations,
            laboratories,
            {"C8-0002": "TSTL-0002"},
            [],
            [],
            {},
        )

        self.assertEqual(relations["First Org"], [])
        self.assertEqual(relations["Second Org"], [])


if __name__ == "__main__":
    unittest.main()
