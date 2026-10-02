"""Tests for reachable-history duplicate blob detection."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import audit_large_files  # noqa: E402


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class DuplicateBlobHistoryTests(unittest.TestCase):
    def _repo(self, root: Path) -> None:
        _git(root, "init", "-q")
        _git(root, "config", "user.name", "Duplicate Test")
        _git(root, "config", "user.email", "duplicate-test-author")

    def test_rename_across_history_is_not_a_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._repo(root)
            old = root / "old-name.md"
            old.write_text("same content\n", encoding="utf-8")
            _git(root, "add", "old-name.md")
            _git(root, "commit", "-qm", "add old path")
            old.rename(root / "new-name.md")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "rename path")

            self.assertEqual(audit_large_files.duplicate_entries(root), [])

    def test_same_tree_duplicate_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._repo(root)
            (root / "first.md").write_text("same content\n", encoding="utf-8")
            (root / "second.md").write_text("same content\n", encoding="utf-8")
            _git(root, "add", "first.md", "second.md")
            _git(root, "commit", "-qm", "add duplicate paths")

            duplicates = audit_large_files.duplicate_entries(root)
            self.assertEqual(len(duplicates), 1)
            _, paths = duplicates[0]
            self.assertEqual(paths, ["first.md", "second.md"])

    def test_paths_in_different_trees_are_not_combined(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._repo(root)
            (root / "first.md").write_text("same content\n", encoding="utf-8")
            _git(root, "add", "first.md")
            _git(root, "commit", "-qm", "first path")
            (root / "first.md").rename(root / "second.md")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "second path")

            self.assertEqual(audit_large_files.duplicate_entries(root), [])


if __name__ == "__main__":
    unittest.main()
