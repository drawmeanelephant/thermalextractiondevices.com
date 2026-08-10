"""Tests for the COA content audit (scripts/audit_coa_content.py).

Builds a tiny content tree in a tempdir and asserts the COA-01..07 rules fire
and stay quiet exactly where they should.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_coa_content import audit

DEMO_PAGE = """\
---
id: lab-results/TLAB-0001
title: "Demo COA"
parent: lab-results
status: published
tags: ["lab-results", "coa", "demonstration", "synthetic-data"]
relations: [relates_to=products/TPRD-0001, relates_to=terpenes/TTRP-0005, relates_to=cultivars/TCUL-0001]
summary: demo record
---

# Demo COA

{{include includes/demo-sample-record-warning.md}}

THCA 24.20 % w/w (sample)
"""

VERIFIED_PAGE = """\
---
id: lab-results/TLAB-0101
title: "Real COA"
parent: lab-results
status: published
tags: ["lab-results", "coa"]
relations: [relates_to=products/TPRD-0001, relates_to=cultivars/TCUL-0001, relates_to=cannabinoids/TCBN-0007]
summary: verified record
---

# Real COA

## Provenance & Sources

- Official portal: https://example.gov/coa/123 (retrieved 2026-01-02)
"""

BAD_ID_PAGE = """\
---
id: lab-results/NOT-AN-ID
title: "Bad"
parent: lab-results
status: published
tags: ["lab-results", "demonstration"]
relations: [relates_to=products/TPRD-0001]
summary: bad id
---

# Bad

{{include includes/demo-sample-record-warning.md}}
"""

CULTIVAR_CHEMISTRY = """\
---
id: cultivars/TCUL-0001
title: "Blue Dream"
parent: cultivars
status: published
tags: ["cultivar"]
summary: cultivar page
---

# Blue Dream

- THC: 22.0 %
- Myrcene: 0.8 mg/g
"""

CULTIVAR_CLEAN = """\
---
id: cultivars/TCUL-0002
title: "Skunk #1"
parent: cultivars
status: published
tags: ["cultivar"]
relations: [relates_to=terpenes/TTRP-0005]
summary: cultivar page
---

# Skunk #1

- Lineage: Afghan Indica x Colombian Gold
- 50% sativa / 50% indica
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def id_map(*ids: str) -> str:
    lines = []
    for entity_id in ids:
        lines.append(json.dumps({
            "collection": entity_id.split("/")[0],
            "form_id": entity_id.split("/")[-1],
            "id": entity_id,
            "source": entity_id + ".md",
            "role": "satellite",
        }))
    return "\n".join(lines) + "\n"


class AuditCoaContentTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        known = (
            "products/TPRD-0001", "cultivars/TCUL-0001", "cultivars/TCUL-0002",
            "terpenes/TTRP-0005", "cannabinoids/TCBN-0007", "lab-results/TLAB-0001",
        )
        write(self.root / "metadata" / "id-map.jsonl", id_map(*known))

    def tearDown(self):
        self._tmp.cleanup()

    def findings(self) -> list[tuple[str, str, str]]:
        return audit(self.root / "content", self.root / "metadata" / "id-map.jsonl")

    def codes(self, severity: str = "") -> list[str]:
        return [
            rule for sev, rule, _ in self.findings()
            if not severity or sev == severity
        ]

    def test_demo_page_passes(self):
        write(self.root / "content" / "lab-results" / "TLAB-0001.md", DEMO_PAGE)
        self.assertEqual(self.codes(), [])

    def test_missing_demo_warning_flagged(self):
        page = DEMO_PAGE.replace("{{include includes/demo-sample-record-warning.md}}\n", "")
        write(self.root / "content" / "lab-results" / "TLAB-0001.md", page)
        self.assertIn("COA-02", self.codes("error"))

    def test_verified_page_with_provenance_passes(self):
        write(self.root / "content" / "lab-results" / "TLAB-0101.md", VERIFIED_PAGE)
        codes = self.codes("error")
        self.assertNotIn("COA-03", codes)

    def test_verified_page_without_provenance_flagged(self):
        page = VERIFIED_PAGE.replace("## Provenance & Sources\n\n- Official portal: https://example.gov/coa/123 (retrieved 2026-01-02)\n", "")
        write(self.root / "content" / "lab-results" / "TLAB-0101.md", page)
        self.assertIn("COA-03", self.codes("error"))

    def test_cultivar_chemistry_flagged(self):
        write(self.root / "content" / "cultivars" / "TCUL-0001.md", CULTIVAR_CHEMISTRY)
        self.assertIn("COA-04", self.codes("error"))

    def test_cultivar_without_units_passes(self):
        write(self.root / "content" / "cultivars" / "TCUL-0002.md", CULTIVAR_CLEAN)
        self.assertNotIn("COA-04", self.codes("error"))

    def test_isolated_report_flagged(self):
        page = DEMO_PAGE.replace(
            "relations: [relates_to=products/TPRD-0001, relates_to=terpenes/TTRP-0005, relates_to=cultivars/TCUL-0001]",
            "relations: [relates_to=terpenes/TTRP-0005]",
        )
        write(self.root / "content" / "lab-results" / "TLAB-0001.md", page)
        self.assertIn("COA-05", self.codes("error"))

    def test_bad_id_flagged(self):
        write(self.root / "content" / "lab-results" / "BAD.md", BAD_ID_PAGE)
        self.assertIn("COA-01", self.codes("error"))

    def test_broken_relation_warns(self):
        page = DEMO_PAGE.replace("cultivars/TCUL-0001", "cultivars/TCUL-0999")
        write(self.root / "content" / "lab-results" / "TLAB-0001.md", page)
        codes = self.codes("warning")
        self.assertIn("COA-06", codes)
        self.assertNotIn("COA-06", self.codes("error"))

    def test_verified_page_requires_matching_durable_record(self):
        page = VERIFIED_PAGE.replace('tags: ["lab-results", "coa"]', 'tags: ["lab-results", "coa", "verified"]')
        write(self.root / "content" / "lab-results" / "TLAB-0101.md", page)
        registry = self.root / "metadata" / "coa-records.jsonl"
        registry.write_text(json.dumps({
            "report": {"report_id": "lab-results/TLAB-0101"},
            "batch": {"record_kind": "verified"},
        }) + "\n", encoding="utf-8")
        self.assertNotIn("COA-08", [rule for _, rule, _ in audit(
            self.root / "content", self.root / "metadata" / "id-map.jsonl", registry
        )])

        registry.unlink()
        self.assertIn("COA-08", [rule for _, rule, _ in audit(
            self.root / "content", self.root / "metadata" / "id-map.jsonl", registry
        )])

    def test_orphan_durable_verified_record_flagged(self):
        registry = self.root / "metadata" / "coa-records.jsonl"
        registry.write_text(json.dumps({
            "report": {"report_id": "lab-results/TLAB-0999"},
            "batch": {"record_kind": "verified"},
        }) + "\n", encoding="utf-8")
        findings = audit(self.root / "content", self.root / "metadata" / "id-map.jsonl", registry)
        self.assertTrue(any(rule == "COA-08" and "no verified lab-results page" in message
                            for _, rule, message in findings))


if __name__ == "__main__":
    unittest.main()
