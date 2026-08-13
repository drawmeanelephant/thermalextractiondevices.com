"""Suppression matching: exact by default, prefix only when asked for explicitly.

`audit_common.is_suppressed` decides whether a finding is silenced. Getting it
wrong in either direction is expensive: too narrow and the gate nags forever
about generated files that will never stop declaring what they exclude; too
wide and a real leak disappears behind an entry that was written to cover one
file.

The rule under test is that only an entry ending in `/` matches by prefix. An
exact `CODE:path` entry must never widen into the directory it sits in, so
these tests pin the negative direction as hard as the positive one.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_common import Finding, is_suppressed  # noqa: E402


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

    def test_trailing_slash_entry_suppresses_the_whole_subtree(self):
        config = {"suppressions": ["PII-007:data/sync-reports/"]}
        self.assertTrue(is_suppressed(finding("PII-007", "data/sync-reports/a.md"), config))
        self.assertTrue(is_suppressed(finding("PII-007", "data/sync-reports/nested/b.md"), config))

    def test_prefix_entry_is_scoped_to_its_code(self):
        config = {"suppressions": ["PII-007:data/sync-reports/"]}
        self.assertFalse(is_suppressed(finding("PII-005", "data/sync-reports/a.md"), config))

    def test_prefix_entry_respects_the_directory_boundary(self):
        """`data/sync-reports/` must not swallow a sibling like `data/sync-reports-old/`."""
        config = {"suppressions": ["PII-007:data/sync-reports/"]}
        self.assertFalse(is_suppressed(finding("PII-007", "data/sync-reports-old/a.md"), config))

    def test_entry_without_trailing_slash_never_widens(self):
        """The anti-widening guarantee: an exact directory-shaped entry stays exact."""
        config = {"suppressions": ["PII-007:data/sync-reports"]}
        self.assertFalse(is_suppressed(finding("PII-007", "data/sync-reports/a.md"), config))

    def test_pathless_finding_ignores_prefix_entries(self):
        config = {"suppressions": ["POL-001:docs/"]}
        self.assertFalse(is_suppressed(finding("POL-001", None), config))

    def test_non_string_entries_are_ignored(self):
        """A malformed config entry must not raise; it simply matches nothing."""
        config = {"suppressions": [None, 17, ["PII-007:data/"], "PII-007:data/"]}
        self.assertTrue(is_suppressed(finding("PII-007", "data/a.md"), config))
        self.assertFalse(is_suppressed(finding("PII-005", "data/a.md"), config))


if __name__ == "__main__":
    unittest.main()
