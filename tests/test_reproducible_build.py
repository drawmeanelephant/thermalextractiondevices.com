"""Unit tests for the static-build reproducibility checker."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check_reproducible_build import (
    ROOT,
    compare_inventories,
    inventory_tree,
    safe_work_dir,
)


class ReproducibleBuildTests(unittest.TestCase):
    def test_identical_trees_have_identical_aggregate_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = base / "first"
            second = base / "second"
            for root in (first, second):
                (root / "nested").mkdir(parents=True)
                (root / "index.html").write_text("home\n", encoding="utf-8")
                (root / "nested" / "page.html").write_bytes(b"page\x00")

            first_inventory = inventory_tree(first)
            second_inventory = inventory_tree(second)
            self.assertEqual(first_inventory.tree_sha256, second_inventory.tree_sha256)
            self.assertEqual(first_inventory.file_count, 2)
            self.assertEqual(first_inventory.total_bytes, 10)
            self.assertEqual(
                compare_inventories(first_inventory, second_inventory),
                {"only_in_first": [], "only_in_second": [], "changed": []},
            )

    def test_content_and_path_differences_are_classified(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = base / "first"
            second = base / "second"
            first.mkdir()
            second.mkdir()
            (first / "shared.html").write_text("first", encoding="utf-8")
            (second / "shared.html").write_text("second", encoding="utf-8")
            (first / "old.html").write_text("old", encoding="utf-8")
            (second / "new.html").write_text("new", encoding="utf-8")

            differences = compare_inventories(
                inventory_tree(first), inventory_tree(second)
            )
            self.assertEqual(differences["only_in_first"], ["old.html"])
            self.assertEqual(differences["only_in_second"], ["new.html"])
            self.assertEqual(differences["changed"], ["shared.html"])

    def test_work_directory_must_be_isolated_below_dist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            accepted = safe_work_dir(root, Path("dist/reproducibility"))
            self.assertEqual(accepted, (root / "dist" / "reproducibility").resolve())
            for rejected in (Path("dist"), Path("."), Path("outside")):
                with self.subTest(rejected=rejected):
                    with self.assertRaises(ValueError):
                        safe_work_dir(root, rejected)

    def test_production_wrapper_rejects_output_outside_dist(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "must-not-be-created"
            environment = os.environ.copy()
            environment.update({
                "BORIS_BIN": shutil.which("true") or "/usr/bin/true",
                "DIST_DIR": str(outside),
            })
            result = subprocess.run(
                [str(ROOT / "scripts" / "ted-build.sh")],
                cwd=ROOT,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("refusing unsafe DIST_DIR", result.stderr)
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
