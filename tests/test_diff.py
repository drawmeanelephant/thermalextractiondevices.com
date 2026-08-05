"""Source-revision diff tests."""

from __future__ import annotations

import unittest

from scripts.ingest.diff import compare_snapshots


class DiffTestCase(unittest.TestCase):
    def test_unchanged(self):
        rows = [{"id": "1", "v": "x"}]
        result = compare_snapshots(rows, list(rows), ["id"])
        self.assertEqual(result.added, 0)
        self.assertEqual(result.removed, 0)
        self.assertEqual(result.changed, 0)
        self.assertIn("no change", result.summary)

    def test_added_removed(self):
        prior = [{"id": "1", "v": "x"}]
        current = [{"id": "1", "v": "x"}, {"id": "2", "v": "y"}]
        result = compare_snapshots(prior, current, ["id"])
        self.assertEqual(result.added, 1)
        self.assertEqual(result.removed, 0)

    def test_status_change_classified(self):
        prior = [{"id": "1", "status": "Active", "result": "5.0"}]
        current = [{"id": "1", "status": "Suspended", "result": "5.0"}]
        result = compare_snapshots(prior, current, ["id"],
                                   status_columns=["status"], numeric_columns=["result"])
        self.assertEqual(result.changed, 1)
        self.assertEqual(result.changed_status_only, 1)
        self.assertEqual(result.changed_numeric, 0)

    def test_numeric_change_classified(self):
        prior = [{"id": "1", "status": "Active", "result": "5.0"}]
        current = [{"id": "1", "status": "Active", "result": "6.5"}]
        result = compare_snapshots(prior, current, ["id"],
                                   status_columns=["status"], numeric_columns=["result"])
        self.assertEqual(result.changed, 1)
        self.assertEqual(result.changed_numeric, 1)

    def test_status_and_numeric_mixed(self):
        prior = [{"id": "1", "status": "Active", "result": "5.0"}]
        current = [{"id": "1", "status": "Suspended", "result": "6.5"}]
        result = compare_snapshots(prior, current, ["id"],
                                   status_columns=["status"], numeric_columns=["result"])
        self.assertEqual(result.changed, 1)
        self.assertEqual(result.changed_numeric, 1)
        self.assertEqual(result.changed_status_only, 0)


if __name__ == "__main__":
    unittest.main()
