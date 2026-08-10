#!/usr/bin/env python3
"""Audit COA / lab-result content pages against the archive's COA graph rules.

The durable model (scripts/coa_model.py) enforces measurement semantics on the
JSON record; this audit enforces the *published content* contract described in
docs/coa-data-model.md — that every page in content/lab-results/ is a proper
report record, that synthetic/demonstration pages are unmistakably labeled,
that real reports carry provenance, and that cultivar pages never attach
chemistry to a cultivar name.

Rules
-----
COA-01 (error)   every lab-results satellite carries a canonical
                 lab-results/TLAB-XXXX id and status: published
COA-02 (error)   a demonstration/synthetic lab-results page includes the
                 demo-sample-record-warning include (unmistakable label)
COA-03 (error)   a non-demonstration lab-results page has a Provenance/Sources
                 section that cites at least one URL
COA-04 (error)   a cultivar page carries numeric measurement units (chemistry
                 attached directly to a cultivar name as if universal)
COA-05 (error)   a lab-results page has no product/cultivar/organization
                 relation (an isolated report that cannot be traced to a batch)
COA-06 (warning) a frontmatter relation references an entity id that is not
                 present in metadata/id-map.jsonl (broken relation)
COA-07 (warning) a lab-results page links to no compound pages
                 (cannabinoid/terpene/contaminant)
COA-08 (error)   verified lab-result pages and durable verified COA records
                 must have a one-to-one report-id parity

Severity split is deliberate. COA-01…05 are mechanically decidable and block;
COA-06…07 inform without failing a page that is honestly thin.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
TAGS_LINE = re.compile(r"^tags:\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
ID_LINE = re.compile(r"^id:\s*(.+?)\s*$", re.MULTILINE)
STATUS_LINE = re.compile(r"^status:\s*(.+?)\s*$", re.MULTILINE)
RELATIONS_LINE = re.compile(r"^relations:\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
URL = re.compile(r"https?://\S+")
RELATION_REF = re.compile(r"(?:relates_to|depends_on|parent)=([A-Za-z0-9_./-]+)")

TLAB_ID = re.compile(r"^lab-results/TLAB-[0-9]{4}$")

DEMO_INCLUDE = "demo-sample-record-warning"
PROVENANCE_SECTION = re.compile(r"provenance|sources", re.IGNORECASE)
BATCH_LINK_SECTION = re.compile(r"batch|product", re.IGNORECASE)

# Measurement vocabulary: a numeric claim followed by an explicit unit token.
# Bare "%" is deliberately excluded — cultivar prose legitimately says
# "50% sativa". The check targets the units laboratories actually print.
CHEMISTRY_UNIT = re.compile(
    r"\d+(?:\.\d+)?\s*(?:mg/g|µg/g|ug/g|ng/g|mg/mL|ug/mL|CFU/g|CFU/mL|%\s*w/w|%\s*w/v)"
    r"|\b(?:ppm|ppb)\b",
    re.IGNORECASE,
)

COMPOUND_COLLECTIONS = ("cannabinoids/", "terpenes/", "contaminants/")
BATCH_LINK_COLLECTIONS = ("products/", "cultivars/", "organizations/")


def parse_tags(frontmatter: str) -> set[str]:
    match = TAGS_LINE.search(frontmatter)
    if not match:
        return set()
    return {t.strip().strip('"').strip("'") for t in match.group(1).split(",") if t.strip()}


def parse_relations(frontmatter: str) -> set[str]:
    match = RELATIONS_LINE.search(frontmatter)
    if not match:
        return set()
    return {ref for ref in RELATION_REF.findall(match.group(1))}


def read_frontmatter(text: str) -> str:
    match = FRONTMATTER.search(text)
    return match.group(1) if match else ""


def load_id_map(path: Path) -> set[str]:
    ids: set[str] = set()
    if not path.exists():
        return ids
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("id"):
            ids.add(str(item["id"]))
    return ids


def audit_lab_result(path: Path, known_ids: set[str]) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")
    name = path.name
    frontmatter = read_frontmatter(text)

    id_match = ID_LINE.search(frontmatter)
    entity_id = id_match.group(1).strip() if id_match else ""
    status_match = STATUS_LINE.search(frontmatter)
    status = status_match.group(1).strip() if status_match else ""

    if not TLAB_ID.fullmatch(entity_id):
        findings.append(
            ("error", "COA-01",
             f"{name}: lab-results pages require a canonical lab-results/TLAB-XXXX id (found {entity_id!r})")
        )
    if status != "published":
        findings.append(
            ("error", "COA-01", f"{name}: lab-results pages require status: published (found {status!r})")
        )

    tags = parse_tags(frontmatter)
    relations = parse_relations(frontmatter)
    sections = {s.strip().lower() for s in SECTION.findall(text)}
    is_demonstration = "demonstration" in tags or DEMO_INCLUDE in text

    if is_demonstration:
        if DEMO_INCLUDE not in text:
            findings.append(
                ("error", "COA-02",
                 f"{name}: demonstration/synthetic record must include {DEMO_INCLUDE} "
                 "so it is unmistakably labeled DEMONSTRATION / SYNTHETIC DATA")
            )
    else:
        has_provenance_section = any(PROVENANCE_SECTION.search(s) for s in sections)
        has_url = bool(URL.search(text))
        if not has_provenance_section or not has_url:
            findings.append(
                ("error", "COA-03",
                 f"{name}: non-demonstration report needs a Provenance/Sources section "
                 "citing at least one source URL")
            )

    if not any(ref.startswith(p) for ref in relations for p in BATCH_LINK_COLLECTIONS):
        findings.append(
            ("error", "COA-05",
             f"{name}: no product/cultivar/organization relation — the report cannot be "
             "traced to a batch (add relations: [relates_to=...])")
        )

    for ref in sorted(relations):
        if known_ids and ref not in known_ids:
            findings.append(
                ("warning", "COA-06", f"{name}: relation {ref!r} is not in metadata/id-map.jsonl")
            )

    if not any(ref.startswith(COMPOUND_COLLECTIONS) for ref in relations):
        findings.append(
            ("warning", "COA-07",
             f"{name}: no relation to a compound page (cannabinoids/terpenes/contaminants) — "
             "measurements cannot be traced to a canonical compound")
        )

    return findings


def audit_cultivars(root: Path) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    cultivars = root / "cultivars"
    if not cultivars.is_dir():
        return findings
    for path in sorted(cultivars.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if CHEMISTRY_UNIT.search(text):
            findings.append(
                ("error", "COA-04",
                 f"{path.name}: cultivar page carries numeric measurement units — "
                 "chemistry belongs to reports/batches, never to a cultivar name")
            )
    return findings


def audit_registry_parity(root: Path, registry_path: Path) -> list[tuple[str, str, str]]:
    """Require one durable record for every verified page, and vice versa."""
    findings: list[tuple[str, str, str]] = []
    if not registry_path.exists():
        findings.append(("error", "COA-08", f"{registry_path}: durable COA registry is missing"))
        return findings

    verified_records: dict[str, int] = {}
    try:
        for line_no, line in enumerate(registry_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                findings.append(("error", "COA-08", f"{registry_path}:{line_no}: invalid JSON: {error}"))
                continue
            report = record.get("report") or {}
            batch = record.get("batch") or {}
            report_id = str(report.get("report_id") or "")
            if batch.get("record_kind") != "verified":
                continue
            if report_id in verified_records:
                findings.append(("error", "COA-08", f"{registry_path}:{line_no}: duplicate verified record {report_id!r}"))
            verified_records[report_id] = line_no
    except (OSError, UnicodeError) as error:
        findings.append(("error", "COA-08", f"{registry_path}: cannot read durable registry: {error}"))
        return findings

    verified_pages: set[str] = set()
    lab_results = root / "lab-results"
    if lab_results.is_dir():
        for path in sorted(lab_results.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            frontmatter = read_frontmatter(text)
            tags = parse_tags(frontmatter)
            if "verified" not in tags or "demonstration" in tags:
                continue
            id_match = ID_LINE.search(frontmatter)
            if id_match:
                verified_pages.add(id_match.group(1).strip())

    for report_id in sorted(verified_pages - verified_records.keys()):
        findings.append(("error", "COA-08", f"{report_id}: verified lab-results page has no durable COA record"))
    for report_id in sorted(verified_records.keys() - verified_pages):
        findings.append(("error", "COA-08", f"{report_id}: durable verified COA record has no verified lab-results page"))
    return findings


def audit(root: Path, id_map_path: Path, coa_path: Path | None = None) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    known_ids = load_id_map(id_map_path)
    lab_results = root / "lab-results"
    if lab_results.is_dir():
        for path in sorted(lab_results.glob("*.md")):
            findings.extend(audit_lab_result(path, known_ids))
    findings.extend(audit_cultivars(root))
    if coa_path is not None:
        findings.extend(audit_registry_parity(root, coa_path))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="content directory")
    parser.add_argument("--map", dest="id_map", type=Path,
                        default=Path("metadata/id-map.jsonl"), help="id-map.jsonl path")
    parser.add_argument("--coa", dest="coa_path", type=Path,
                        default=Path("metadata/coa-records.jsonl"), help="durable COA registry path")
    parser.add_argument("--warnings-only", action="store_true",
                        help="never exit non-zero; report findings only")
    args = parser.parse_args()

    try:
        findings = audit(args.root, args.id_map, args.coa_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"COA content audit: error: {error}", file=sys.stderr)
        return 2

    errors = [f for f in findings if f[0] == "error"]
    warnings = [f for f in findings if f[0] == "warning"]

    for severity, rule, message in findings:
        print(f"  [{severity.upper()}] {rule}: {message}")

    print(
        f"COA content audit: {len(errors)} error(s), {len(warnings)} warning(s) "
        f"across {len(findings)} finding(s)"
    )
    if args.warnings_only:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
