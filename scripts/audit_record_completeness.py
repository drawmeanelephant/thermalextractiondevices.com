#!/usr/bin/env python3
"""Audit device records against the archive's record-completeness floor.

The Device Architecture Taxonomy (TREF-0004) promises that every device record
classifies its subject on five orthogonal axes and identifies it by the
manufacturer's own part number. A standard that most records do not implement is
not a standard, so this audit turns that promise into a machine check.

Rules
-----
REC-01 (error)   every axis in metadata/device-taxonomy.json carries at least one
                 tag on the record
REC-02 (error)   a "Part Number" spec row exists; an unpublished identifier is
                 declared explicitly rather than omitted
REC-03 (error)   a "Sources" section exists and cites at least one primary-source
                 URL (a footnote whose only provenance is the internal research
                 dossier does not count)
REC-04 (warning) a "Safety Notes" section exists
REC-05 (warning) a component-role or form-factor role statement exists
REC-06 (warning) the record cites more than one distinct source domain

Severity split is deliberate. REC-01…03 are objective and mechanically decidable,
so they block. REC-04…06 depend on how much the manufacturer published, so they
inform without failing a record that is honestly thin.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TAXONOMY_DEFAULT = "metadata/device-taxonomy.json"
DEVICES_SUBDIR = "devices"

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
TAGS_LINE = re.compile(r"^tags:\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|$", re.MULTILINE)
SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
FOOTNOTE = re.compile(r"^\[\^[^\]]+\]:\s*(.*)$", re.MULTILINE)
URL = re.compile(r"https?://\S+")
DOMAIN = re.compile(r"https?://(?:www\.)?([A-Za-z0-9.-]+)")

# A footnote that only points at the internal research corpus is provenance, not
# a primary source; the archive's evidence rules require a reachable citation.
DOSSIER_ONLY = re.compile(r"research/|internal provenance", re.IGNORECASE)

PART_NUMBER_ROW = re.compile(r"^(part number|part numbers|model number|sku)$", re.IGNORECASE)
ROLE_ROW = re.compile(r"component role|form factor", re.IGNORECASE)
SAFETY_SECTION = re.compile(r"safety", re.IGNORECASE)


def parse_tags(frontmatter: str) -> set[str]:
    match = TAGS_LINE.search(frontmatter)
    if not match:
        return set()
    return {t.strip().strip('"').strip("'") for t in match.group(1).split(",") if t.strip()}


def parse_spec_rows(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for prop, value in ROW.findall(text):
        if prop in {"---", "Property"} or set(prop) <= {"-", " "}:
            continue
        rows.setdefault(prop.strip(), value.strip())
    return rows


def primary_source_domains(text: str) -> set[str]:
    """Domains cited by footnotes that are not dossier-only provenance."""
    domains: set[str] = set()
    for body in FOOTNOTE.findall(text):
        if DOSSIER_ONLY.search(body) and not URL.search(body):
            continue
        for url in URL.findall(body):
            match = DOMAIN.search(url)
            if match:
                domains.add(match.group(1).lower())
    return domains


def audit_file(path: Path, taxonomy: dict) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")
    name = path.name

    fm_match = FRONTMATTER.search(text)
    frontmatter = fm_match.group(1) if fm_match else ""
    tags = parse_tags(frontmatter)
    rows = parse_spec_rows(text)
    sections = {s.strip() for s in SECTION.findall(text)}

    missing_axes = [
        axis for axis, values in taxonomy["axes"].items() if not (tags & set(values))
    ]
    if missing_axes:
        findings.append(
            ("error", "REC-01", f"{name}: no tag for axis {', '.join(sorted(missing_axes))}")
        )

    if not any(PART_NUMBER_ROW.match(prop.strip()) for prop in rows):
        findings.append(
            ("error", "REC-02", f"{name}: no 'Part Number' row (state it, or state that the manufacturer publishes none)")
        )

    domains = primary_source_domains(text)
    if not any(s == "Sources" for s in sections):
        findings.append(("error", "REC-03", f"{name}: no 'Sources' section"))
    elif not domains:
        findings.append(
            ("error", "REC-03", f"{name}: no primary-source URL — every cited footnote is dossier-only provenance")
        )

    if not any(SAFETY_SECTION.search(s) for s in sections):
        findings.append(("warning", "REC-04", f"{name}: no safety section"))

    if not any(ROLE_ROW.search(prop) for prop in rows):
        findings.append(("warning", "REC-05", f"{name}: no component-role or form-factor row"))

    if len(domains) <= 1:
        findings.append(
            ("warning", "REC-06", f"{name}: cites {len(domains)} source domain(s) — single-sourced")
        )

    return findings


def audit(root: Path, taxonomy: dict) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    devices = root / DEVICES_SUBDIR
    if not devices.is_dir():
        return findings
    for path in sorted(devices.glob("*.md")):
        findings.extend(audit_file(path, taxonomy))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="content directory containing devices/")
    parser.add_argument("--vocab", type=Path, default=Path(TAXONOMY_DEFAULT), help="path to device-taxonomy.json")
    parser.add_argument("--warnings-only", action="store_true", help="never exit non-zero; report findings only")
    args = parser.parse_args()

    try:
        taxonomy = json.loads(args.vocab.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Record completeness audit: error loading vocabulary: {error}", file=sys.stderr)
        return 2

    try:
        findings = audit(args.root, taxonomy)
    except (OSError, UnicodeError) as error:
        print(f"Record completeness audit: error: {error}", file=sys.stderr)
        return 2

    errors = [f for f in findings if f[0] == "error"]
    warnings = [f for f in findings if f[0] == "warning"]

    for severity, rule, message in findings:
        print(f"  [{severity.upper()}] {rule}: {message}")

    print(
        f"Record completeness audit: {len(errors)} error(s), {len(warnings)} warning(s) "
        f"across {len(findings)} finding(s)"
    )
    if args.warnings_only:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
