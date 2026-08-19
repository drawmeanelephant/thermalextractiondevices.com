"""Suppression matching is exact, and must stay exact.

`audit_common.is_suppressed` decides whether a finding is silenced. Getting it
wrong is expensive in both directions, but the directions are not symmetric:
too narrow and the gate nags about a file someone already reviewed; too wide and
a real leak disappears behind an entry written to cover something else.

So the contract is exact match only -- a bare code, or a `CODE:path` pair. No
prefix, glob, or directory form. A directory form was written and removed on
2026-08-13: one line would have pre-authorised every future file in a growing
generated directory, and the per-file config cost is the review signal.

These tests pin the negative direction harder than the positive one. Most of
them assert that something is NOT suppressed.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_common import Finding, SEVERITY_RANK, is_suppressed  # noqa: E402


def finding(code: str, path: str | None) -> Finding:
    return Finding(code=code, severity="medium", message="test", path=path)


class SuppressionMatching(unittest.TestCase):
    def test_unsuppressed_finding_is_reported(self):
        """Positive control: nothing configured means nothing silenced."""
        self.assertFalse(is_suppressed(finding("PII-007", "a/b.md"), {"suppressions": []}))

    def test_bare_code_suppresses_every_path(self):
        config = {"suppressions": ["PII-007"]}
        self.assertTrue(is_suppressed(finding("PII-007", "a/b.md"), config))
        self.assertTrue(is_suppressed(finding("PII-007", "z/q.json"), config))
        self.assertFalse(is_suppressed(finding("PII-005", "a/b.md"), config))

    def test_exact_pair_suppresses_only_that_path(self):
        config = {"suppressions": ["PII-007:data/spec.md"]}
        self.assertTrue(is_suppressed(finding("PII-007", "data/spec.md"), config))
        self.assertFalse(is_suppressed(finding("PII-007", "data/other.md"), config))
        self.assertFalse(is_suppressed(finding("PII-005", "data/spec.md"), config))

    def test_directory_entry_does_not_cover_its_contents(self):
        """The headline contract. A directory-shaped entry silences nothing."""
        for entry in ("PII-007:data/sync-reports", "PII-007:data/sync-reports/"):
            with self.subTest(entry=entry):
                config = {"suppressions": [entry]}
                self.assertFalse(is_suppressed(finding("PII-007", "data/sync-reports/a.md"), config))
                self.assertFalse(
                    is_suppressed(finding("PII-007", "data/sync-reports/nested/b.md"), config)
                )

    def test_entry_is_not_matched_as_a_substring_of_the_path(self):
        """`data/x.md` must not be silenced by an entry naming a longer or nested path."""
        config = {"suppressions": ["PII-007:vendor/data/x.md"]}
        self.assertFalse(is_suppressed(finding("PII-007", "data/x.md"), config))
        config = {"suppressions": ["PII-007:data/x.md"]}
        self.assertFalse(is_suppressed(finding("PII-007", "vendor/data/x.md"), config))

    def test_code_prefix_collision_does_not_match(self):
        """`PII-00` must not silence `PII-005`, and `PII-0075` must not either."""
        self.assertFalse(is_suppressed(finding("PII-005", "a.md"), {"suppressions": ["PII-00"]}))
        self.assertFalse(is_suppressed(finding("PII-005", "a.md"), {"suppressions": ["PII-0075"]}))

    def test_suppressions_written_as_a_bare_string_cannot_match_by_substring(self):
        """A config typo -- a string where a list belongs -- must fail closed.

        `"PII-007" in "PII-0071"` is True for strings, so a bare-string config
        would silence unrelated codes by substring. It must not.
        """
        config = {"suppressions": "PII-0071"}
        self.assertFalse(is_suppressed(finding("PII-007", "a.md"), config))

    def test_non_string_entries_are_ignored(self):
        """A malformed entry must not raise; it simply matches nothing."""
        config = {"suppressions": [None, 17, ["PII-007:data/x.md"], "PII-007:data/x.md"]}
        self.assertTrue(is_suppressed(finding("PII-007", "data/x.md"), config))
        self.assertFalse(is_suppressed(finding("PII-005", "data/x.md"), config))


class ShippedConfigIsReviewable(unittest.TestCase):
    """Guard the config a release actually runs with, not just the matcher."""

    def setUp(self):
        self.config = json.loads((REPO_ROOT / "docs" / "audit-config.json").read_text("utf-8"))
        self.entries = [e for e in self.config.get("suppressions", []) if isinstance(e, str)]

    def test_every_suppression_names_an_exact_existing_file(self):
        """A suppression that names no file is either a typo or stale rot.

        It also catches the directory form by construction: a directory is not a
        file, so `PII-007:data/sync-reports/` fails here even if someone later
        re-adds prefix matching to the matcher.
        """
        for entry in self.entries:
            if ":" not in entry:
                continue
            _, _, path = entry.partition(":")
            with self.subTest(entry=entry):
                self.assertTrue(
                    (REPO_ROOT / path).is_file(),
                    "suppression {!r} does not name an existing file".format(entry),
                )

    def test_no_bare_code_suppression_can_reach_the_fail_threshold(self):
        """A bare code silences a whole rule everywhere. Never for a blocking one."""
        threshold = SEVERITY_RANK.get(str(self.config.get("fail_threshold", "high")), 0)
        blocking = {"SEC-001", "PII-001", "PII-002", "PII-003", "PII-004", "PII-006"}
        for entry in self.entries:
            if ":" in entry:
                continue
            with self.subTest(entry=entry):
                self.assertNotIn(
                    entry,
                    blocking,
                    "bare suppression {!r} silences a rule that can block the "
                    "release gate at threshold rank {}".format(entry, threshold),
                )


if __name__ == "__main__":
    unittest.main()
