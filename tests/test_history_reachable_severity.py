"""Deleted-but-reachable blobs are graded by path, and none of those grades block.

Removing a file from the working tree does not remove it from history: `git show
<old-commit>:<path>` still returns it, so every clone keeps paying for it. Bulk
data under a sensitive prefix is therefore reported more loudly than build output.

Neither grade blocks the release gate. An earlier version graded anything under
`data/` as `high` on the assumption that such a path implied PRIVACY.md category-4
data. It did not: the payload in question was the California DCC licence register,
retrieved from the state's public licence-search system, and Cal. Civ. Code
s.1798.82(i) excludes information lawfully made public in government records from
the definition of personal information. A path prefix is not evidence of
disclosure; only content is. audit_sensitive_content.py does that job.
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
            # Bulk data under a sensitive prefix reports louder than build output,
            # but neither blocks. This deliberately no longer pins `high`: the
            # payload that motivated that grade was the California DCC licence
            # register from search.cannabis.ca.gov, a public government register.
            # Cal. Civ. Code s.1798.82(i) excludes government-record information
            # from the personal-information definition, so treating a path prefix
            # as proof of disclosure was wrong. Content-based detection lives in
            # audit_sensitive_content.py, which inspects payloads rather than paths
            # and is where a real category-4 finding should originate.
            self.assertEqual(deleted["data/registry.json"], "medium")
            self.assertEqual(deleted["dist/bundle.js"], "low")
            # Neither grade may reach the blocking threshold.
            self.assertNotIn("high", set(deleted.values()))


if __name__ == "__main__":
    unittest.main()
