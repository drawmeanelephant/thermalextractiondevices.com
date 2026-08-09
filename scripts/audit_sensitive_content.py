#!/usr/bin/env python3
"""Audit the Thermal Extraction Devices repository for sensitive content.

Scans the tracked working tree (and, optionally, reachable git history) for:

* possible secrets and API keys / tokens / private keys
* email addresses, phone numbers, full street addresses, coordinates,
  tax identifiers, and parcel-like numbers (``prohibited public fields``)
* personal filesystem paths, local usernames, and ``file://`` links
* credential-shaped file names (``.env``, ``*.pem``, private keys, ...)

Matches are surfaced as findings with a stable code, severity, and
repo-relative path. Allowlists and suppressions are configured through a
JSON file (``--config``); nothing is silently ignored.

Exit codes: 0 = clean (or only sub-threshold findings), 1 = findings meet
the fail threshold, 2 = tool error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from audit_common import (
    CREDENTIAL_FILE_NAMES,
    CREDENTIAL_FILE_SUFFIXES,
    DEFAULT_SCAN_EXTENSIONS,
    Finding,
    human_path,
    is_suppressed,
    load_config,
    list_tracked_files,
    severity_rank,
)

# --- patterns -------------------------------------------------------------

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# Phone numbers: international prefix with 7-15 digits, or a 3-3-4 digit
# group pattern that REQUIRES separators between groups so bare numbers
# (ports, years, counts) are not flagged.
PHONE_RE = re.compile(
    r"\b(?:\+\d{7,15}"
    r"|(?:\+?1[ .\-]?)?\(?\d{3}\)?[ .\-]\d{3}[ .\-]\d{4})\b"
)
ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+[A-Z][A-Za-z]{2,}(?:\s+[A-Z][A-Za-z]{2,})*"
    r"\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|"
    r"Lane|Ln\.?|Drive|Dr\.?|Court|Ct\.?|Way|Circle|Cir\.?|Place|Pl\.?|"
    r"Highway|Hwy\.?)\b"
)
COORDINATE_RE = re.compile(
    # Decimal pairs; lookbehind excludes letters/digits/hyphens so SVG path
    # chains ("m42.32,33.93c-0.51,-0.25") and embedded UI icon paths are not
    # mistaken for geographic coordinates.
    r"(?<![A-Za-z0-9-])(?:-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,})"
    r"|(?:\d{1,3}°\s*\d{1,2}['′]?\s*\d{1,2}(?:\.\d+)?[\"″]?\s*[NS])"
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EIN_RE = re.compile(r"\b\d{2}-\d{7}\b")
LONG_NUMERIC_RE = re.compile(r"\b\d{9,12}\b")  # candidate tax/parcel identifiers
# Parcel/APN formats (dash-separated, unambiguous against ISO dates):
# Ohio 20-digit parcels like 010-00-00-123-0000, CA APNs like 1234-567-890.
PARCEL_RE = re.compile(
    r"\b\d{2,4}-\d{2}-\d{2}-\d{3}-\d{4}\b|\b\d{4}-\d{3}-\d{3}\b"
)
PERSONAL_PATH_RE = re.compile(
    r"(?:/Users/[^/\s]+|(?<![A-Za-z0-9.:])/home/[^/\s]+|C:\\Users\\[^\\\s]+|file:///|~/[^/\s]+)"
)
# Functional/role mailboxes. PRIVACY.md category 4 prohibits "personal email
# addresses ... of individuals or private premises"; a role mailbox is by
# definition neither. On published archive content these are the manufacturer
# contacts a hardware reference is expected to carry — including product-safety
# recall contacts — so they are category 5 (maintainer sign-off), not a
# publication blocker. Raw ingest payloads under data/ are deliberately excluded:
# 96.5% of the emails there are personal-looking licensee addresses.
ROLE_MAILBOX_RE = re.compile(
    r"\b(?:support|service|services|info|sales|contact|help|helpdesk|recall|recalls"
    r"|repair|repairs|customerservice|customer_service|customercare|privacy|security"
    r"|press|media|legal|admin|hello|orders|order|warranty|office|inquiries|enquiries"
    r"|abuse|postmaster|webmaster|noreply|no-reply)@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    re.IGNORECASE,
)


def _is_business_contact_path(rel_path: str) -> bool:
    """Published archive content, where business contacts are expected and curated."""
    return rel_path.startswith("content/")


SECRET_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "Amazon AWS access key id"),
    ("aws-secret-key", re.compile(r"\b(?:aws_secret_access_key|awsSecretAccessKey)\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{20,}"), "Amazon AWS secret key"),
    ("github-token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "GitHub personal access token"),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "GitHub fine-grained token"),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{20,}\b"), "Slack token"),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), "Google API key"),
    ("stripe-secret", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"), "Stripe live secret key"),
    ("twilio-token", re.compile(r"\bAC[0-9a-f]{32}\b"), "Twilio account identifier"),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b"), "JSON Web Token"),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY(?: BLOCK)?"), "private key material"),
    (    "generic-credential", re.compile(
        r"\b(?:api[_-]?key|apikey|secret|secret[_-]?key|access[_-]?token|auth[_-]?token|"
        r"password|passwd|client[_-]?secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+]{16,}"
    ), "credential-shaped key/value pair"),
    ("webhook-url", re.compile(r"https://(?:discord(?:app)?\.com/api/webhooks/|hooks\.slack\.com/services/)"), "webhook URL"),
    ("aws-arn", re.compile(r"\barn:aws:(?:iam|secretsmanager)::\d{12}:[^\s]+"), "AWS ARN"),
]

SEVERITY_BY_SECRET = {
    "aws-access-key": "critical", "aws-secret-key": "critical",
    "github-token": "critical", "github-pat": "critical",
    "private-key": "critical", "stripe-secret": "critical",
    "webhook-url": "critical", "aws-arn": "critical",
    "slack-token": "high", "google-api-key": "high",
    "twilio-token": "high", "jwt": "high", "generic-credential": "high",
}


def _allowed_secret(match_text: str, line: str, allowlist: List[str]) -> bool:
    """True when a secret match should be ignored by config or context."""
    for pattern in allowlist:
        try:
            if re.search(pattern, line):
                return True
        except re.error:
            continue
    # GitHub Actions secret references (${{ secrets.X }}) are not values.
    if "${{" in line and ("secrets." in line or "env." in line):
        if "secrets." in line and match_text not in ("secrets",):
            return True
    return False


def _scan_text(text: str, rel_path: str, config: Dict[str, Any],
               findings: List[Finding]) -> None:
    allow = config.get("allowlist", {})
    email_allow = allow.get("emails", [])
    secret_allow = allow.get("secrets", [])
    path_allow = allow.get("personal_paths", [])
    phone_allow = allow.get("phones", [])
    address_allow = allow.get("addresses", [])
    coord_allow = allow.get("coordinates", [])
    tax_allow = allow.get("tax_ids", [])

    business_ctx = _is_business_contact_path(rel_path)

    for line_number, line in enumerate(text.splitlines(), start=1):
        # Emails
        for match in EMAIL_RE.finditer(line):
            email = match.group(0)
            if any(token in email for token in email_allow):
                continue
            if business_ctx and ROLE_MAILBOX_RE.match(email):
                # PRIVACY.md category 5, not category 4: a functional mailbox
                # (support@, recall@, service@) on published archive content is a
                # business contact for an identifiable business, not an
                # individual's personal address. Needs maintainer sign-off, not a
                # publication block.
                findings.append(Finding(
                    code="REV-001", severity="medium",
                    message="business contact on published content — requires maintainer sign-off (PRIVACY.md category 5)",
                    path=rel_path, line=line_number, detail=email,
                ))
                continue
            findings.append(Finding(
                code="PII-001", severity="high",
                message="email address in tracked content",
                path=rel_path, line=line_number, detail=email,
            ))
        # Phones
        for match in PHONE_RE.finditer(line):
            if any(token in match.group(0) for token in phone_allow):
                continue
            findings.append(Finding(
                code="PII-002", severity="high",
                message="phone number pattern in tracked content",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        # Street addresses
        for match in ADDRESS_RE.finditer(line):
            if any(token in match.group(0) for token in address_allow):
                continue
            findings.append(Finding(
                code="PII-003", severity="high",
                message="full street address pattern in tracked content",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        # Coordinates
        for match in COORDINATE_RE.finditer(line):
            if any(token in match.group(0) for token in coord_allow):
                continue
            findings.append(Finding(
                code="PII-004", severity="high",
                message="geographic coordinates in tracked content",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        # Tax identifiers / parcel-like numbers
        for match in SSN_RE.finditer(line):
            if any(token in match.group(0) for token in tax_allow):
                continue
            findings.append(Finding(
                code="PII-005", severity="high",
                message="SSN-format identifier in tracked content",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        for match in EIN_RE.finditer(line):
            if any(token in match.group(0) for token in tax_allow):
                continue
            findings.append(Finding(
                code="PII-005", severity="medium",
                message="EIN-format identifier in tracked content",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        for match in PARCEL_RE.finditer(line):
            if any(token in match.group(0) for token in tax_allow):
                continue
            findings.append(Finding(
                code="PII-005", severity="medium",
                message="parcel-number format identifier in tracked content",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        for match in LONG_NUMERIC_RE.finditer(line):
            if any(token in match.group(0) for token in tax_allow):
                continue
            findings.append(Finding(
                code="PII-005", severity="low",
                message="long numeric identifier (candidate tax/parcel number) — human review",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        # Personal filesystem paths and file:// links
        for match in PERSONAL_PATH_RE.finditer(line):
            if any(token in match.group(0) for token in path_allow):
                continue
            findings.append(Finding(
                code="PII-006", severity="high",
                message="personal filesystem path or file:// link",
                path=rel_path, line=line_number, detail=match.group(0),
            ))
        # Prohibited field names (config-driven; e.g. registry PII keys).
        for name in config.get("prohibited_fields", []):
            if name in line:
                findings.append(Finding(
                    code="PII-007", severity="medium",
                    message="prohibited field name present: {}".format(name),
                    path=rel_path, line=line_number,
                ))
        # Secrets
        for label, pattern, description in SECRET_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            if _allowed_secret(match.group(0), line, secret_allow):
                continue
            findings.append(Finding(
                code="SEC-001", severity=SEVERITY_BY_SECRET.get(label, "high"),
                message="possible secret: {}".format(description),
                path=rel_path, line=line_number, detail=match.group(0)[:120],
            ))


def _scan_file(path: Path, root: Path, config: Dict[str, Any],
               findings: List[Finding]) -> None:
    rel = human_path(path.relative_to(root).as_posix())
    name = path.name
    if name in CREDENTIAL_FILE_NAMES or any(name.endswith(s) for s in CREDENTIAL_FILE_SUFFIXES):
        findings.append(Finding(
            code="SEC-002", severity="critical",
            message="credential-shaped file name is tracked",
            path=rel,
        ))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        # Binary files: size is handled by audit_large_files; flag for review.
        if path.stat().st_size > 0:
            findings.append(Finding(
                code="REV-002", severity="low",
                message="binary or non-UTF-8 file tracked (human review)",
                path=rel,
            ))
        return
    _scan_text(text, rel, config, findings)


def _scan_git_log(root: Path, config: Dict[str, Any],
                  findings: List[Finding]) -> None:
    """Scan commit authors, committers, and messages across reachable history."""
    email_allow = config.get("allowlist", {}).get("emails", [])
    secret_allow = config.get("allowlist", {}).get("secrets", [])
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", "--all",
             "--format=%H%x09%an%x09%ae%x09%cn%x09%ce%x09%s"],
            capture_output=True, text=True, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if proc.returncode != 0:
        return
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 6:
            continue
        sha, an, ae, cn, ce, subject = parts[:6]
        for email in (ae, ce):
            if not email:
                continue
            if any(token in email for token in email_allow):
                continue
            findings.append(Finding(
                code="PII-001", severity="high",
                message="email address in git history metadata",
                path="<history>", detail="{} ({})".format(sha[:8], email),
            ))
        for label, pattern, description in SECRET_PATTERNS:
            match = pattern.search(subject)
            if not match:
                continue
            if _allowed_secret(match.group(0), subject, secret_allow):
                continue
            findings.append(Finding(
                code="SEC-001", severity=SEVERITY_BY_SECRET.get(label, "high"),
                message="possible secret in commit message: {}".format(description),
                path="<history>", detail=sha[:8],
            ))


def audit(root: Path, config: Dict[str, Any], include_history: bool = True,
          include_ignored: bool = False) -> List[Finding]:
    findings: List[Finding] = []
    tracked = set(list_tracked_files(root))
    if tracked:
        for rel in sorted(tracked):
            path = root / rel
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            if ext in DEFAULT_SCAN_EXTENSIONS or path.name in CREDENTIAL_FILE_NAMES:
                _scan_file(path, root, config, findings)
    else:
        tracked = set()
    if include_ignored:
        # Scan the full working tree (tracked + ignored/local artifacts).
        for path in sorted(root.rglob("*")):
            if not path.is_file() or ".git" in path.parts:
                continue
            rel = human_path(path.relative_to(root).as_posix())
            if rel in tracked:
                continue
            ext = path.suffix.lower()
            if ext in DEFAULT_SCAN_EXTENSIONS or path.name in CREDENTIAL_FILE_NAMES:
                _scan_file(path, root, config, findings)
    if include_history:
        _scan_git_log(root, config, findings)
    # Deduplicate prohibited-field-name findings: one per (path, field) pair
    # regardless of how many lines/records reference it.
    seen_fields = set()
    deduped = []
    for finding in findings:
        if finding.code == "PII-007":
            key = (finding.path, finding.message)
            if key in seen_fields:
                continue
            seen_fields.add(key)
        deduped.append(finding)
    return deduped


def render(findings: List[Finding], config: Dict[str, Any]) -> str:
    lines = ["Sensitive-content audit: {} finding(s) (first 60 shown)".format(len(findings))]
    for index, finding in enumerate(findings):
        if index >= 60:
            lines.append("... {} more finding(s); use --report for the full list".format(len(findings) - index))
            break
        marker = "SUPPRESSED" if is_suppressed(finding, config) else "ACTIVE"
        location = finding.path + (":{}".format(finding.line) if finding.line else "")
        lines.append(
            "[{}] {} {:>8} {} {}".format(
                marker, finding.code, finding.severity.upper(), location,
                finding.message,
            )
        )
        if finding.detail:
            lines.append("        -> {}".format(finding.detail[:160]))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=None,
                        help="JSON allowlist/suppression config")
    parser.add_argument("--no-history", action="store_true",
                        help="skip git history scan")
    parser.add_argument("--include-ignored", action="store_true",
                        help="also scan local/ignored working-tree artifacts (e.g. caches, .env)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--report", type=Path, default=None,
                        help="write JSON report to this path")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        config = load_config(args.config)
        findings = audit(root, config, include_history=not args.no_history,
                         include_ignored=args.include_ignored)
    except Exception as error:  # tool error => exit 2, never misread as findings
        print("sensitive-content audit: error: {}".format(error), file=sys.stderr)
        return 2

    try:
        active = [f for f in findings if not is_suppressed(f, config)]
        blocking = [f for f in active if severity_rank(f.severity) >= severity_rank(str(config.get("fail_threshold", "high")))]

        if args.as_json or args.report is not None:
            payload = {"findings": [f.to_dict() for f in findings]}
            if args.as_json:
                print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            if args.report is not None:
                args.report.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        if not args.as_json:
            print(render(findings, config))
        if blocking:
            print("sensitive-content audit: {} blocking finding(s); see above".format(len(blocking)), file=sys.stderr)
            return 1
        if active:
            print("sensitive-content audit: no findings above fail threshold ({})".format(config.get("fail_threshold", "high")))
        else:
            print("sensitive-content audit: clean")
        return 0
    except Exception as error:
        print("sensitive-content audit: error while rendering: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
