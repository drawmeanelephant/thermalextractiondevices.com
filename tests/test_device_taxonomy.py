"""Unit tests for scripts/audit_device_taxonomy.py (Device Architecture Taxonomy)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_device_taxonomy import (
    TAXONOMY_DEFAULT,
    audit_file,
    parse_spec_rows,
    parse_tags,
)


def write_page(root: Path, name: str, body: str) -> Path:
    path = root / "devices" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def frontmatter(tags: list[str], summary: str = "Fixture record.") -> str:
    tag_list = ", ".join(f'"{t}"' for t in tags)
    return (
        "---\n"
        'id: devices/TED-9999\n'
        'title: "Fixture"\n'
        "parent: devices\n"
        "status: draft\n"
        f"tags: [{tag_list}]\n"
        f"summary: {summary}\n"
        "---\n"
    )


class TaxonomyFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.taxonomy = json.loads(Path(TAXONOMY_DEFAULT).read_text(encoding="utf-8"))

    def test_parse_tags(self) -> None:
        fm = 'id: devices/TED-0001\ntags: ["device", "portable", "hybrid"]\nrelations: []\n'
        self.assertEqual(parse_tags(fm), ["device", "portable", "hybrid"])

    def test_parse_spec_rows(self) -> None:
        text = "| Property | Specification |\n| --- | --- |\n| Heating Method | Convection |\n| Power | AC mains |\n"
        rows = parse_spec_rows(text)
        self.assertEqual(rows["Heating Method"], "Convection")
        self.assertEqual(rows["Power"], "AC mains")

    def _findings(self, body: str) -> list[tuple[str, str, str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "content"
            path = write_page(root, "TED-9999.md", body)
            return audit_file(path, self.taxonomy)

    def test_clean_record_no_findings(self) -> None:
        body = (
            frontmatter(["device", "portable", "convection", "battery", "on-demand"])
            + "# Fixture\n\n## Technical Specifications\n\n"
            "| Property | Specification |\n| --- | --- |\n"
            "| Heating Method | Pure convection |\n| Power Source | Internal battery |\n"
        )
        self.assertEqual(self._findings(body), [])

    def test_tax01_conduction_plus_convection(self) -> None:
        body = frontmatter(["device", "conduction", "convection"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "TAX-01" for _, rule, _ in findings))

    def test_tax02_flame_exclusive(self) -> None:
        body = frontmatter(["device", "direct-flame", "indirect-flame"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "TAX-02" for _, rule, _ in findings))

    def test_tax03_manual_vs_session(self) -> None:
        body = frontmatter(["device", "manual", "session"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "TAX-03" for _, rule, _ in findings))

    def test_tax04_battery_plus_mains(self) -> None:
        body = frontmatter(["device", "battery", "mains"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "TAX-04" for _, rule, _ in findings))

    def test_tax05_bundle_not_model(self) -> None:
        body = frontmatter(["device", "bundle", "ball-vape"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "TAX-05" for _, rule, _ in findings))

    def test_adv01_ball_vape_needs_component_role(self) -> None:
        body = frontmatter(["device", "desktop", "ball-vape", "convection"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "ADV-01" for _, rule, _ in findings))

    def test_adv01_ball_vape_with_role_passes(self) -> None:
        body = frontmatter(["device", "desktop", "ball-vape", "convection"]) + (
            "# Fixture\n\n## Technical Specifications\n\n"
            "| Property | Specification |\n| --- | --- |\n"
            "| Heating Method | Ball-assisted convection |\n"
            "| Component Role | heater head |\n"
        )
        findings = self._findings(body)
        self.assertFalse(any(rule == "ADV-01" for _, rule, _ in findings))

    def test_adv02_no_heating_mechanism_declared(self) -> None:
        body = frontmatter(["device", "portable", "analog"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "ADV-02" for _, rule, _ in findings))

    def test_vocab_warns_on_unknown_tag(self) -> None:
        body = frontmatter(["device", "portable", "definitely-not-a-term"])
        findings = self._findings(body)
        self.assertTrue(any(rule == "VOCAB" for _, rule, _ in findings))


if __name__ == "__main__":
    unittest.main()
