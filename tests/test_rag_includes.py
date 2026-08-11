import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.rag_includes import (
    IncludeResolutionError,
    IncludeResolver,
    audit_content_includes,
    audit_export_includes,
    format_include_issues,
)
from scripts.resolve_rag_includes import create_resolved_export


class RagIncludeTests(unittest.TestCase):
    def test_content_audit_and_nested_resolution_are_deterministic(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content = root / "content"
            includes = content / "includes"
            includes.mkdir(parents=True)
            (includes / "leaf.md").write_text("leaf body", encoding="utf-8")
            (includes / "wrapper.md").write_text(
                "wrapper start\n{{include includes/leaf.md}}\nwrapper end\n",
                encoding="utf-8",
            )
            (content / "page.md").write_text(
                "before\n{{include includes/wrapper.md}}\nafter\n",
                encoding="utf-8",
            )

            first = audit_content_includes(content)
            second = audit_content_includes(content)
            self.assertEqual(first, second)
            self.assertEqual(first.reference_count, 2)
            self.assertEqual(first.unique_references, ("includes/leaf.md", "includes/wrapper.md"))
            self.assertEqual(first.issues, ())

            resolved = IncludeResolver(includes).resolve_text(
                (content / "page.md").read_text(encoding="utf-8"),
                source="page.md",
            )
            self.assertEqual(
                resolved,
                "before\nwrapper start\nleaf body\nwrapper end\n\nafter\n",
            )
            self.assertNotIn("{{include", resolved)

    def test_source_audit_reports_sorted_missing_and_unsafe_references(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content = root / "content"
            includes = content / "includes"
            includes.mkdir(parents=True)
            (content / "z-page.md").write_text(
                "{{include includes/missing.md}}\n", encoding="utf-8"
            )
            (content / "a-page.md").write_text(
                "{{include ../outside.md}}\n{{include}}\n", encoding="utf-8"
            )

            audit = audit_content_includes(content)
            rendered = format_include_issues(audit.issues)
            self.assertEqual(
                rendered.splitlines(),
                [
                    "a-page.md:1:1: include path must start with includes/ [{{include ../outside.md}}]",
                    "a-page.md:2:1: malformed or unterminated include marker [{{include}}]",
                    "z-page.md:1:1: include file does not exist: includes/missing.md [{{include includes/missing.md}}]",
                ],
            )
            self.assertEqual(rendered, format_include_issues(audit.issues))

    def test_unresolved_export_audit_is_sorted_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            export = Path(temporary) / "rag"
            export.mkdir()
            (export / "working-2.md").write_text(
                "{{include includes/two.md}}\n", encoding="utf-8"
            )
            (export / "working-1.md").write_text(
                "{{include includes/one.md}}\n", encoding="utf-8"
            )
            audit = audit_export_includes(export)
            self.assertEqual(
                [issue.source for issue in audit.issues],
                ["working-1.md", "working-2.md"],
            )
            self.assertEqual(audit.reference_count, 2)
            self.assertEqual(
                audit.unique_references,
                ("includes/one.md", "includes/two.md"),
            )

    def test_resolved_export_preserves_raw_bytes_and_rebuilds_deterministically(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content = root / "content"
            includes = content / "includes"
            includes.mkdir(parents=True)
            (includes / "note.md").write_text(
                "> [!NOTE]\n> Resolved caveat.\n", encoding="utf-8"
            )
            source = content / "page.md"
            source.write_text(
                "---\nid: page\n---\n\n{{include includes/note.md}}\n",
                encoding="utf-8",
            )

            raw = root / "rag"
            raw.mkdir()
            raw_pack = (
                "# Boris working context pack 1/1\n\n"
                "<!-- boris-rag-doc: id=\"content/page\" source=\"page.md\" -->\n"
                "---\nid: page\n---\n\n{{include includes/note.md}}\n"
            ).encode("utf-8")
            (raw / "working-1.md").write_bytes(raw_pack)
            raw_manifest = {
                "format": "boris-rag",
                "schema_version": 2,
                "boris_version": "0.8.1",
                "mode": "working",
                "upload_files": [{"path": "working-1.md", "bytes": len(raw_pack)}],
                "documents": [
                    {
                        "source": "page.md",
                        "pack": "working-1.md",
                        "bytes": len(source.read_bytes()),
                        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    }
                ],
            }
            raw_manifest_bytes = json.dumps(raw_manifest).encode("utf-8")
            (raw / "manifest.json").write_bytes(raw_manifest_bytes)
            raw_pack_before = (raw / "working-1.md").read_bytes()
            raw_manifest_before = (raw / "manifest.json").read_bytes()

            resolved = root / "rag-resolved"
            manifest = create_resolved_export(raw, resolved, content)
            second = root / "rag-resolved-2"
            second_manifest = create_resolved_export(raw, second, content)

            self.assertEqual(raw_pack_before, (raw / "working-1.md").read_bytes())
            self.assertEqual(raw_manifest_before, (raw / "manifest.json").read_bytes())
            output = (resolved / "working-1.md").read_text(encoding="utf-8")
            self.assertIn("> Resolved caveat.", output)
            self.assertNotIn("{{include", output)
            self.assertEqual(audit_export_includes(resolved).issues, ())
            self.assertEqual(manifest, second_manifest)
            self.assertEqual(
                (resolved / "working-1.md").read_bytes(),
                (second / "working-1.md").read_bytes(),
            )
            self.assertEqual(manifest["surface"], "resolved-working")
            self.assertEqual(manifest["mode"], "working")
            self.assertEqual(
                manifest["resolved_from"]["manifest_sha256"],
                hashlib.sha256(raw_manifest_bytes).hexdigest(),
            )
            self.assertEqual(manifest["upload_files"][0]["raw_bytes"], len(raw_pack))
            self.assertEqual(
                manifest["upload_files"][0]["bytes"],
                (resolved / "working-1.md").stat().st_size,
            )
            self.assertEqual(
                manifest["documents"][0]["raw_bytes"],
                len(source.read_bytes()),
            )
            self.assertEqual(manifest["include_resolution"]["unresolved_markers"], 0)

    def test_resolver_rejects_include_cycles(self):
        with tempfile.TemporaryDirectory() as temporary:
            includes = Path(temporary) / "includes"
            includes.mkdir()
            (includes / "a.md").write_text(
                "{{include includes/b.md}}", encoding="utf-8"
            )
            (includes / "b.md").write_text(
                "{{include includes/a.md}}", encoding="utf-8"
            )
            with self.assertRaisesRegex(IncludeResolutionError, "include cycle"):
                IncludeResolver(includes).resolve_text("{{include includes/a.md}}")

    def test_failed_audit_does_not_replace_existing_resolved_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content = root / "content"
            (content / "includes").mkdir(parents=True)
            (content / "page.md").write_text(
                "{{include includes/missing.md}}\n", encoding="utf-8"
            )
            raw = root / "rag"
            raw.mkdir()
            (raw / "working-1.md").write_text(
                "{{include includes/missing.md}}\n", encoding="utf-8"
            )
            (raw / "manifest.json").write_text(
                json.dumps(
                    {
                        "mode": "working",
                        "upload_files": [{"path": "working-1.md", "bytes": 1}],
                        "documents": [],
                    }
                ),
                encoding="utf-8",
            )
            resolved = root / "rag-resolved"
            resolved.mkdir()
            (resolved / "sentinel.txt").write_text("keep me", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "content include audit failed"):
                create_resolved_export(raw, resolved, content)

            self.assertEqual(
                (resolved / "sentinel.txt").read_text(encoding="utf-8"),
                "keep me",
            )
            self.assertFalse((resolved / "working-1.md").exists())


if __name__ == "__main__":
    unittest.main()
