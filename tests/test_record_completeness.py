"""Unit tests for scripts/audit_record_completeness.py (record-completeness floor)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_record_completeness import (
    TAXONOMY_DEFAULT,
    audit_file,
    primary_source_domains,
)

ALL_AXES = ["convection", "coil", "water-tool", "continuous-desktop", "external-pid"]


def write_page(root: Path, name: str, body: str) -> Path:
    path = root / "devices" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def page(
    tags: list[str] = ALL_AXES,
    part_number: bool = True,
    sources: str = "[^1]: Maker, product page. https://example-maker.com/p/1\n",
    safety: bool = True,
    role: bool = True,
) -> str:
    tag_list = ", ".join(f'"{t}"' for t in ["device"] + tags)
    rows = ["| Property | Specification |", "| --- | --- |", "| Manufacturer | Maker |"]
    if part_number:
        rows.append("| Part Number | 1234 |")
    if role:
        rows.append("| Component Role | Heater head |")
    body = (
        "---\n"
        "id: devices/TED-9999\n"
        'title: "Fixture"\n'
        "parent: devices\n"
        "status: draft\n"
        f"tags: [{tag_list}]\n"
        "summary: Fixture record.\n"
        "---\n\n"
        "# Fixture\n\n"
        "## Technical Specifications\n\n" + "\n".join(rows) + "\n\n"
    )
    if safety:
        body += "## Safety Notes\n\n- Hot.\n\n"
    body += "## Sources\n\n" + sources
    return body


def rules(findings) -> set[str]:
    return {rule for _, rule, _ in findings}


def errors(findings) -> set[str]:
    return {rule for severity, rule, _ in findings if severity == "error"}


class RecordCompletenessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.taxonomy = json.loads(Path(TAXONOMY_DEFAULT).read_text(encoding="utf-8"))

    def audit(self, body: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_page(Path(tmp), "TED-9999.md", body)
            return audit_file(path, self.taxonomy)

    def test_complete_record_raises_no_errors(self):
        """The floor must be satisfiable — otherwise the audit is unusable."""
        findings = self.audit(page(sources=(
            "[^1]: Maker, product page. https://example-maker.com/p/1\n"
            "[^2]: Maker, manual. https://docs.example-maker.org/manual.pdf\n"
        )))
        self.assertEqual(errors(findings), set())
        self.assertEqual(rules(findings), set())

    def test_missing_axis_is_an_error(self):
        findings = self.audit(page(tags=["convection", "coil", "water-tool", "continuous-desktop"]))
        self.assertIn("REC-01", errors(findings))

    def test_each_axis_is_checked_independently(self):
        for drop in range(len(ALL_AXES)):
            kept = [t for i, t in enumerate(ALL_AXES) if i != drop]
            with self.subTest(dropped=ALL_AXES[drop]):
                self.assertIn("REC-01", errors(self.audit(page(tags=kept))))

    def test_missing_part_number_is_an_error(self):
        self.assertIn("REC-02", errors(self.audit(page(part_number=False))))

    def test_part_number_declared_unpublished_satisfies_the_rule(self):
        """An honestly absent identifier passes; silence does not."""
        body = page(part_number=False).replace(
            "| Component Role | Heater head |",
            "| Component Role | Heater head |\n| Part Number | Not published by the manufacturer |",
        )
        self.assertNotIn("REC-02", errors(self.audit(body)))

    def test_dossier_only_footnote_is_not_a_primary_source(self):
        body = page(sources="[^1]: Research dossier (internal provenance: `research/devices/x.md`).\n")
        self.assertIn("REC-03", errors(self.audit(body)))

    def test_missing_sources_section_is_an_error(self):
        body = page().replace("## Sources", "## Bibliography")
        self.assertIn("REC-03", errors(self.audit(body)))

    def test_missing_safety_is_a_warning_not_an_error(self):
        findings = self.audit(page(safety=False))
        self.assertIn("REC-04", rules(findings))
        self.assertNotIn("REC-04", errors(findings))

    def test_missing_role_row_is_a_warning(self):
        self.assertIn("REC-05", rules(self.audit(page(role=False))))

    def test_single_source_domain_warns(self):
        self.assertIn("REC-06", rules(self.audit(page())))

    def test_two_domains_clear_the_single_source_warning(self):
        findings = self.audit(page(sources=(
            "[^1]: Maker, product page. https://example-maker.com/p/1\n"
            "[^2]: Regulator filing. https://sec.example.gov/f/2\n"
        )))
        self.assertNotIn("REC-06", rules(findings))

    def test_same_domain_twice_still_counts_as_single_sourced(self):
        findings = self.audit(page(sources=(
            "[^1]: Maker, product page. https://example-maker.com/p/1\n"
            "[^2]: Maker, other page. https://www.example-maker.com/p/2\n"
        )))
        self.assertIn("REC-06", rules(findings))

    def test_primary_source_domains_ignores_dossier_but_keeps_cited_urls(self):
        text = (
            "[^1]: Research dossier (internal provenance: `research/x.md`).\n"
            "[^2]: Maker manual. https://example-maker.com/manual\n"
        )
        self.assertEqual(primary_source_domains(text), {"example-maker.com"})


if __name__ == "__main__":
    unittest.main()
