"""Deleted-but-reachable blobs under regulated paths must block the release gate.

Removing a file from the working tree does not remove it from history. For build
output that is merely wasteful; for PRIVACY.md category-4 data it is a live
disclosure, because `git show <old-commit>:<path>` still returns the payload to
anyone who can clone the repository.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class HistoryReachableSeverity(unittest.TestCase):
    def test_audit_grades_deleted_reachable_blobs_by_path(self):
        """Exercise the production audit against real deleted Git objects."""
        import audit_large_files

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Audit Test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "audit@example.com"], check=True)

            (root / "data").mkdir()
            (root / "dist").mkdir()
            (root / "data" / "registry.json").write_text("sensitive fixture\n", encoding="utf-8")
            (root / "dist" / "bundle.js").write_text("generated fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "add fixtures"], check=True)

            (root / "data" / "registry.json").unlink()
            (root / "dist" / "bundle.js").unlink()
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "remove fixtures"], check=True)

            config = {
                "thresholds": {"large_file_bytes": 1, "review_file_bytes": 1},
                "allowlist": {"large_files": [], "duplicate_blobs": []},
                "history_sensitive_paths": ["data/"],
                "generated_artifact_patterns": [],
            }
            findings, _ = audit_large_files.audit(root, config)
            deleted = {
                finding.path: finding.severity
                for finding in findings
                if finding.code == "LARGE-004"
            }
            self.assertEqual(deleted["data/registry.json"], "high")
            self.assertEqual(deleted["dist/bundle.js"], "medium")


if __name__ == "__main__":
    unittest.main()
