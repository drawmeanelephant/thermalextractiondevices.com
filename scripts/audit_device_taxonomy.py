#!/usr/bin/env python3
"""Audit device records against the Device Architecture Taxonomy (TREF-0004).

Checks every `content/devices/*.md` record against the controlled vocabulary
in `metadata/device-taxonomy.json` and applies the contradiction rules
(TAX-01..TAX-05) and advisory rules (ADV-01..ADV-02) defined there.

Usage:
    python3 scripts/audit_device_taxonomy.py content
    python3 scripts/audit_device_taxonomy.py content --vocab metadata/device-taxonomy.json

Exit codes: 0 = no rule violations; 1 = at least one contradiction (error);
2 = tooling error (missing vocab, unreadable file).
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
TAGS_LINE = re.compile(r'^tags:\s*\[(.*?)\]', re.MULTILINE | re.DOTALL)
ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|$")

HEATING_MECHANISM_TAGS = {"conduction", "convection", "hybrid", "radiant"}

# Natural-language signals that a ball-vape page states its component role.
BALL_VAPE_ROLE_RE = re.compile(
    r"\b(heater head|head assembly|complete system|base station|bundle|component|station)\b",
    re.IGNORECASE,
)


def parse_tags(frontmatter: str) -> list[str]:
    match = TAGS_LINE.search(frontmatter)
    if not match:
        return []
    return [token.strip().strip('"').strip("'") for token in match.group(1).split(",") if token.strip()]


def parse_spec_rows(text: str) -> dict[str, str]:
    """Extract Property -> Specification pairs from markdown tables."""
    rows: dict[str, str] = {}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        key, value = match.group(1).strip(), match.group(2).strip()
        if key and value:
            rows[key] = value
    return rows


def known_tags(taxonomy: dict) -> set[str]:
    known: set[str] = set()
    for values in taxonomy["axes"].values():
        known.update(values)
    known.update(taxonomy["recognized_descriptors"])
    known.update(taxonomy["manufacturer_slugs"])
    known.update(taxonomy["ball_vape_components"])
    return known


def audit_file(path: Path, taxonomy: dict) -> list[tuple[str, str, str]]:
    """Return (severity, rule, message) findings for one device record."""
    findings: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")
    fm = FRONTMATTER.search(text)
    if not fm:
        findings.append(("error", "PARSE", f"{path.name}: missing YAML frontmatter"))
        return findings

    tags = parse_tags(fm.group(1))
    known = known_tags(taxonomy)

    for tag in tags:
        if tag not in known:
            findings.append(
                ("warning", "VOCAB", f"{path.name}: tag '{tag}' is not in the device taxonomy vocabulary")
            )

    tag_set = set(tags)

    # TAX-01: conduction + convection without hybrid.
    if "conduction" in tag_set and "convection" in tag_set and "hybrid" not in tag_set:
        findings.append(("error", "TAX-01", f"{path.name}: {taxonomy['contradiction_rules']['TAX-01']['message']}"))

    # TAX-02: direct-flame + indirect-flame mutually exclusive.
    if "direct-flame" in tag_set and "indirect-flame" in tag_set:
        findings.append(("error", "TAX-02", f"{path.name}: {taxonomy['contradiction_rules']['TAX-02']['message']}"))

    # TAX-03: manual thermal cycle + session.
    if "manual" in tag_set and "session" in tag_set:
        findings.append(("error", "TAX-03", f"{path.name}: {taxonomy['contradiction_rules']['TAX-03']['message']}"))

    # TAX-04: battery + mains.
    if "battery" in tag_set and "mains" in tag_set:
        findings.append(("error", "TAX-04", f"{path.name}: {taxonomy['contradiction_rules']['TAX-04']['message']}"))

    # TAX-05: bundle is never a model.
    if "bundle" in tag_set:
        findings.append(("error", "TAX-05", f"{path.name}: {taxonomy['contradiction_rules']['TAX-05']['message']}"))

    # ADV-01: ball-vape pages should state their component role.
    if "ball-vape" in tag_set and not BALL_VAPE_ROLE_RE.search(text):
        findings.append(
            ("warning", "ADV-01", f"{path.name}: {taxonomy['advisory_rules']['ADV-01']['message']}")
        )

    # ADV-02: every device should declare a heating mechanism (tag or spec row).
    rows = parse_spec_rows(text)
    heating_row = next((v.lower() for k, v in rows.items() if "heating method" in k.lower()), "")
    has_mechanism_tag = bool(tag_set & HEATING_MECHANISM_TAGS)
    if not has_mechanism_tag and not heating_row:
        findings.append(
            ("warning", "ADV-02", f"{path.name}: {taxonomy['advisory_rules']['ADV-02']['message']}")
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
    args = parser.parse_args()

    try:
        taxonomy = json.loads(args.vocab.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Device taxonomy audit: error loading vocabulary: {error}", file=sys.stderr)
        return 2

    try:
        findings = audit(args.root, taxonomy)
    except (OSError, UnicodeError) as error:
        print(f"Device taxonomy audit: error: {error}", file=sys.stderr)
        return 2

    errors = [f for f in findings if f[0] == "error"]
    warnings = [f for f in findings if f[0] == "warning"]

    for severity, rule, message in findings:
        print(f"  [{severity.upper()}] {rule}: {message}")

    print(
        f"Device taxonomy audit: {len(errors)} error(s), {len(warnings)} warning(s) "
        f"across {len(findings)} finding(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
