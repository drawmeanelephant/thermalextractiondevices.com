"""Deleted-but-reachable blobs under regulated paths must block the release gate.

Removing a file from the working tree does not remove it from history. For build
output that is merely wasteful; for PRIVACY.md category-4 data it is a live
disclosure, because `git show <old-commit>:<path>` still returns the payload to
anyone who can clone the repository.

This was a real gap: after the DCC registry payloads were untracked, the
public-release audit reported "passed" while ~79 MiB of licensee data —
including roughly 20,681 recoverable email addresses — remained reachable from
`main`. The only signal was a `medium` finding, which sits below the `high` fail
threshold and therefore blocked nothing.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_common import Finding  # noqa: E402,F401


def grade(path: str, size: int, config: dict) -> str:
    """Mirror of the severity decision in audit_large_files.audit()."""
    prefixes = tuple(config.get("history_sensitive_paths", ["data/"]))
    return "high" if path.startswith(prefixes) else "medium"


class HistoryReachableSeverity(unittest.TestCase):
    def test_regulated_path_blocks(self):
        self.assertEqual(grade("data/dcc/license-registry/latest.json", 21_000_000, {}), "high")

    def test_build_output_only_informs(self):
        self.assertEqual(grade("dist/cantilever/bundle.js", 21_000_000, {}), "medium")

    def test_prefix_list_is_configurable(self):
        cfg = {"history_sensitive_paths": ["private/", "data/"]}
        self.assertEqual(grade("private/registry.json", 9_000_000, cfg), "high")
        self.assertEqual(grade("docs/big.pdf", 9_000_000, cfg), "medium")

    def test_default_applies_when_unconfigured(self):
        self.assertEqual(grade("data/anything.json", 9_000_000, {}), "high")

    def test_near_miss_path_does_not_block(self):
        """'database/' must not match the 'data/' prefix by accident."""
        self.assertEqual(grade("database-notes/readme.md", 9_000_000, {}), "medium")


class RealRepositoryState(unittest.TestCase):
    """Guard against the gap silently reopening in this repository."""

    def test_audit_module_grades_sensitive_history_as_high(self):
        import audit_large_files
        src = Path(audit_large_files.__file__).read_text(encoding="utf-8")
        self.assertIn("history_sensitive_paths", src)
        self.assertIn('severity="high"', src.split("LARGE-004")[1][:400])


if __name__ == "__main__":
    unittest.main()
