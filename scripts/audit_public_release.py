#!/usr/bin/env python3
"""Public-release readiness audit for the Thermal Extraction Devices repo.

Runs the sensitive-content and large-file/history audits and adds
repository-level checks:

* possible secrets ............................... SEC-001 / SEC-002
* prohibited public fields (emails, phones, ...) . PII-001 .. PII-006
* personal paths / file:// links ................. PII-006
* giant tracked files ............................ LARGE-001
* duplicate dataset blobs ........................ LARGE-003
* generated artifacts committed .................. GEN-001
* missing .gitignore coverage .................... GEN-002
* missing provenance records ..................... PROV-001
* missing repository-policy documents ............ POL-001
* insecure or absent security headers ............ HDR-001
* files that require human review ............... REV-001 / REV-002

Every check honors the shared JSON config (``--config``) for allowlists,
suppressions, and thresholds — findings are never silently ignored.

Run locally or in CI:

    python3 scripts/audit_public_release.py --config docs/audit-config.json

Exit codes: 0 = no findings above fail threshold, 1 = blocking findings,
2 = tool error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from audit_common import (
    Finding,
    human_path,
    is_generated_artifact,
    is_suppressed,
    load_config,
    severity_rank,
)
from audit_large_files import audit as audit_large
from audit_sensitive_content import audit as audit_sensitive

# Files that must exist with any name variation (e.g. LICENSE.md or LICENSE).
POLICY_FILES = [
    "README.md",
    "LICENSE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "DATA_SOURCES.md",
    "PRIVACY.md",
]

HEADER_FILE = "_headers"


def _check_policy_documents(root: Path, config: Dict[str, Any],
                            findings: List[Finding]) -> None:
    required = config.get("required_policy_documents", [])
    for rel in required:
        if not (root / rel).is_file():
            findings.append(Finding(
                code="POL-001", severity="medium",
                message="missing repository-policy document",
                path=rel,
            ))
    # LICENSE may be LICENSE.md, LICENSE, or LICENSE.txt — accept any.
    if not any(p.name.startswith("LICENSE") for p in root.iterdir() if p.is_file()):
        findings.append(Finding(
            code="POL-001", severity="medium",
            message="no LICENSE file present; licensing status is ambiguous",
        ))


def _check_provenance(root: Path, config: Dict[str, Any],
                      findings: List[Finding]) -> None:
    """Structural provenance checks: identity map, evidence includes, disclaimers."""
    if not (root / "metadata" / "id-map.jsonl").is_file():
        findings.append(Finding(
            code="PROV-001", severity="medium",
            message="missing identity migration map metadata/id-map.jsonl",
        ))
    includes = root / "content" / "includes"
    if includes.is_dir():
        warnings = sorted(p.name for p in includes.glob("*warning*.md"))
        if not warnings:
            findings.append(Finding(
                code="PROV-001", severity="low",
                message="no provenance/evidence warning include fragments found in content/includes/",
            ))
    # Flag third-party / regulated content for explicit human sign-off.
    review_paths = config.get("human_review_paths", [])
    for rel in review_paths:
        if (root / rel).exists():
            findings.append(Finding(
                code="REV-001", severity="info",
                message="third-party or regulated data — requires human review before public release",
                path=rel,
            ))


def _check_gitignore(root: Path, config: Dict[str, Any],
                     findings: List[Finding]) -> None:
    path = root / ".gitignore"
    if not path.is_file():
        findings.append(Finding(
            code="GEN-002", severity="high",
            message=".gitignore is missing",
        ))
        return
    text = path.read_text(encoding="utf-8")
    missing = [entry for entry in config.get("required_gitignore_entries", [])
               if entry not in text]
    if missing:
        findings.append(Finding(
            code="GEN-002", severity="medium",
            message=".gitignore lacks required entries: {}".format(", ".join(missing)),
        ))
    if not (root / ".gitattributes").is_file():
        findings.append(Finding(
            code="POL-002", severity="low",
            message=".gitattributes is missing (line-ending and binary handling unspecified)",
        ))


def _check_headers(root: Path, config: Dict[str, Any],
                   findings: List[Finding]) -> None:
    """Verify the committed _headers manifest covers recommended headers."""
    path = root / HEADER_FILE
    if not path.is_file():
        for header, severity in config.get("recommended_headers", {}).items():
            findings.append(Finding(
                code="HDR-001", severity=severity,
                message="missing security header: {}".format(header),
                path=HEADER_FILE,
            ))
        findings.append(Finding(
            code="HDR-001", severity="high",
            message="no {} file; custom response headers are not deployed".format(HEADER_FILE),
            path=HEADER_FILE,
        ))
        return
    text = path.read_text(encoding="utf-8")
    present = set()
    for header in config.get("recommended_headers", {}):
        if header.lower() in text.lower():
            present.add(header)
    for header, severity in config.get("recommended_headers", {}).items():
        if header not in present:
            findings.append(Finding(
                code="HDR-001", severity=severity,
                message="missing security header: {}".format(header),
                path=HEADER_FILE,
            ))


def audit(root: Path, config: Dict[str, Any]) -> List[Finding]:
    findings: List[Finding] = []
    findings.extend(audit_sensitive(root, config))
    large_findings, _report = audit_large(root, config)
    findings.extend(large_findings)
    _check_policy_documents(root, config, findings)
    _check_provenance(root, config, findings)
    _check_gitignore(root, config, findings)
    _check_headers(root, config, findings)
    return findings


def render(findings: List[Finding], config: Dict[str, Any]) -> str:
    active = [f for f in findings if not is_suppressed(f, config)]
    by_code: Dict[str, int] = {}
    for finding in active:
        by_code[finding.code] = by_code.get(finding.code, 0) + 1
    lines = ["Public-release audit: {} finding(s) ({} active)".format(len(findings), len(active))]
    lines.append("\nSummary by code:")
    for code, count in sorted(by_code.items()):
        lines.append("  {:8s} {:3d}".format(code, count))
    lines.append("\nFindings (suppressed ones skipped; capped at 80 lines):")
    shown = 0
    for finding in sorted(active, key=lambda f: (severity_rank(f.severity), f.code, f.path)):
        if shown >= 80:
            lines.append("  ... {} more finding(s); use --report for the full list".format(len(active) - shown))
            break
        location = finding.path + (":{}".format(finding.line) if finding.line else "")
        lines.append("[{}] {:>8} {} {}".format(
            finding.code, finding.severity.upper(), location, finding.message))
        if finding.detail:
            lines.append("        -> {}".format(finding.detail[:160]))
        shown += 1
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=None,
                        help="JSON allowlist/suppression config (see docs/audit-config.json)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--report", type=Path, default=None,
                        help="write JSON report to this path")
    parser.add_argument("--no-history", action="store_true",
                        help="skip the git history scan (faster; tree only)")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        config = load_config(args.config)
        findings = audit(root, config)
    except Exception as error:  # tool error => exit 2, never misread as findings
        print("public-release audit: error: {}".format(error), file=sys.stderr)
        return 2

    try:
        active = [f for f in findings if not is_suppressed(f, config)]
        blocking = [f for f in active if severity_rank(f.severity) >= severity_rank(str(config.get("fail_threshold", "high")))]

        if args.as_json or args.report is not None:
            payload = {
                "root": str(root),
                "fail_threshold": config.get("fail_threshold", "high"),
                "findings": [f.to_dict() for f in findings],
                "blocking_count": len(blocking),
            }
            if args.as_json:
                print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            if args.report is not None:
                args.report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if not args.as_json:
            print(render(findings, config))
        if blocking:
            print("public-release audit: {} blocking finding(s) at threshold '{}'; resolve before public release".format(
                len(blocking), config.get("fail_threshold", "high")), file=sys.stderr)
            return 1
        print("public-release audit: no findings above fail threshold '{}'".format(config.get("fail_threshold", "high")))
        return 0
    except Exception as error:
        print("public-release audit: error while rendering: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
