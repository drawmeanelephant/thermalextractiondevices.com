"""Tests for TED-owned finalization of the Boris HTML site."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.finalize_site import (
    SiteFinalizationError,
    finalize_site,
    write_redirect_manifest,
)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class FinalizeSiteTests(unittest.TestCase):
    def _repo(self, root: Path) -> tuple[Path, Path, Path]:
        repo = root / "repo"
        content = repo / "content"
        theme = repo / "themes" / "cantilever"
        site = root / "site"
        content.mkdir(parents=True)
        theme.mkdir(parents=True)
        (theme / "404.html").write_text("<title>Not found</title>\n", encoding="utf-8")
        (content / "index.md").write_text(
            '---\nid: index\ntitle: "Thermal Extraction Devices"\n'
            "summary: Archive introduction.\n---\n\n# Home\n",
            encoding="utf-8",
        )
        output = site / "devices" / "TED-0001.html"
        output.parent.mkdir(parents=True)
        output.write_text(
            "<!doctype html><html><head><title>Device</title></head>"
            "<body>Device</body></html>\n",
            encoding="utf-8",
        )
        (site / "devices" / "TED-0001-backlinks.html").write_text(
            "<!doctype html><html><head><title>Backlinks</title></head>"
            "<body>Related pages</body></html>\n",
            encoding="utf-8",
        )
        (site / "index.html").write_text(
            "<!doctype html><html><head><title>"
            "Thermal Extraction Devices · Thermal Extraction Devices</title></head>"
            "<body>Home</body></html>\n",
            encoding="utf-8",
        )
        (site / "sitemap.xml").write_text(
            '<?xml version="1.0"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "  <url><loc>https://example.com/index.html</loc></url>\n"
            "  <url><loc>https://example.com/devices/TED-0001.html</loc></url>\n"
            "</urlset>\n",
            encoding="utf-8",
        )
        _git(repo, "init", "-q")
        _git(repo, "config", "user.name", "Finalize Site Test")
        _git(repo, "config", "user.email", "finalize-test-author")
        return repo, content, theme

    def test_adds_canonical_metadata_robots_404_and_clean_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, content, theme = self._repo(root)
            (content / "devices").mkdir()
            (content / "devices" / "firewood.md").write_text(
                '---\nid: devices/TED-0001\ntitle: "Firewood 4"\n'
                'summary: "Device & thermal details."\n---\n\n# Firewood 4\n',
                encoding="utf-8",
            )
            _git(repo, "add", "content")
            _git(repo, "commit", "-qm", "add test pages")
            write_redirect_manifest(content, repo, repo / "metadata/legacy-paths.json")

            counts = finalize_site(
                content,
                theme,
                root / "site",
                "https://example.com",
                repo,
            )
            self.assertEqual(counts["pages"], 2)
            self.assertEqual(counts["descriptions"], 2)
            self.assertEqual(counts["sitemap_urls"], 2)
            self.assertEqual(counts["redirect_rules"], 2)

            page = (root / "site/devices/TED-0001.html").read_text(encoding="utf-8")
            self.assertIn(
                '<meta name="description" content="Device &amp; thermal details.">',
                page,
            )
            self.assertIn(
                '<link rel="canonical" href="https://example.com/devices/TED-0001">',
                page,
            )
            derived = (root / "site/devices/TED-0001-backlinks.html").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                '<link rel="canonical" href="https://example.com/devices/TED-0001-backlinks">',
                derived,
            )
            home = (root / "site/index.html").read_text(encoding="utf-8")
            self.assertIn('<link rel="canonical" href="https://example.com/">', home)
            self.assertIn("<title>Thermal Extraction Devices</title>", home)
            self.assertIn(
                '<meta name="description" content="Archive introduction.">',
                home,
            )

            sitemap = (root / "site/sitemap.xml").read_text(encoding="utf-8")
            self.assertNotIn(".html</loc>", sitemap)
            self.assertIn("https://example.com/</loc>", sitemap)
            self.assertIn(
                "Sitemap: https://example.com/sitemap.xml",
                (root / "site/robots.txt").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (root / "site/404.html").read_text(encoding="utf-8"),
                (theme / "404.html").read_text(encoding="utf-8"),
            )
            redirects = (root / "site/_redirects").read_text(encoding="utf-8")
            self.assertIn("/devices/firewood.html /devices/TED-0001 301", redirects)
            self.assertIn("/devices/firewood /devices/TED-0001 301", redirects)

    def test_follows_renamed_paths_in_git_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, content, theme = self._repo(root)
            devices = content / "devices"
            devices.mkdir()
            old = devices / "old-name.md"
            old.write_text(
                "---\nid: devices/old-name\ntitle: Old\n---\n\n"
                "# Device\n\n"
                + ("Stable source-backed technical description. " * 40)
                + "\n",
                encoding="utf-8",
            )
            _git(repo, "add", "content")
            _git(repo, "commit", "-qm", "add old page")
            old.rename(devices / "TED-0001.md")
            (devices / "TED-0001.md").write_text(
                "---\nid: devices/TED-0001\ntitle: New\n---\n\n"
                "# Device\n\n"
                + ("Stable source-backed technical description. " * 40)
                + "\n",
                encoding="utf-8",
            )
            _git(repo, "add", "content")
            _git(repo, "commit", "-qm", "rename page")
            output = root / "site" / "devices" / "TED-0001.html"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                "<!doctype html><html><head><title>New</title></head>"
                "<body>New</body></html>\n",
                encoding="utf-8",
            )
            write_redirect_manifest(content, repo, repo / "metadata/legacy-paths.json")

            counts = finalize_site(
                content,
                theme,
                root / "site",
                "https://example.com",
                repo,
            )
            redirects = (root / "site/_redirects").read_text(encoding="utf-8")
            self.assertEqual(counts["redirect_rules"], 2)
            self.assertIn("/devices/old-name.html /devices/TED-0001 301", redirects)

    def test_missing_redirect_target_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, content, theme = self._repo(root)
            (content / "devices").mkdir()
            (content / "devices" / "missing.md").write_text(
                "---\nid: devices/TED-9999\ntitle: Missing\n---\n\n# Missing\n",
                encoding="utf-8",
            )
            _git(repo, "add", "content")
            _git(repo, "commit", "-qm", "add missing page")
            write_redirect_manifest(content, repo, repo / "metadata/legacy-paths.json")
            with self.assertRaisesRegex(SiteFinalizationError, "Boris output is missing"):
                finalize_site(content, theme, root / "site", "https://example.com", repo)


if __name__ == "__main__":
    unittest.main()
