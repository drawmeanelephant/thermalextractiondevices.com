"""Publication guards: privacy allowlist scanning and relation-target checks.

The privacy scan is intentionally conservative: it flags excluded field names
*and* representative sensitive-value patterns (EIN/TIN, email, phone, street
address, raw coordinates) anywhere in generated Markdown. Raw local snapshots
are exempt by design (they live in the ignored working directory).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .core import PrivacyViolationError

# ---------------------------------------------------------------------------
# Sensitive value patterns
# ---------------------------------------------------------------------------

EIN_RE = re.compile(r"\b\d{2}-\d{7}\b")                       # 12-3456789
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+1[-\s.]?)?\(?\d{3}\)?[-\s.]\d{3}[-\s.]\d{4}\b")
ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")
STREET_RE = re.compile(
    r"\b\d{1,6}\s+[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*)*\s+"
    r"(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Drive|Dr\.?|"
    r"Lane|Ln\.?|Way|Court|Ct\.?|Circle|Cir\.?|Highway|Hwy\.?|Pike|Turnpike|"
    r"Route|Rte\.?|Parkway|Pkwy\.?)\b",
    re.IGNORECASE,
)
# Raw coordinates: an explicit lat,lon pair, or a standalone value with 5+
# decimal places (unambiguous coordinate precision). Loose 4-decimal numbers
# (e.g. market shares like 0.0023) must NOT be flagged.
COORD_PAIR_RE = re.compile(r"[-+]?\d{1,2}\.\d{4,}\s*,\s*[-+]?\d{1,3}\.\d{4,}")
COORD_RE = re.compile(r"[-+]?\d{1,2}\.\d{5,}")

# Excluded field names as they appear in source schemas (case-insensitive).
EXCLUDED_FIELD_NAMES = {
    "ein_tin", "ein", "tin", "fein",
    "business_email", "business_phone", "email", "email_address", "phone",
    "phone_number", "fax", "mailing_address_1", "mailing_address_2",
    "business_address_1", "business_address_2", "business_address",
    "establishment_address_1", "establishment_address_2",
    "mailing_city", "mailing_state", "mailing_zip_code",
    "agent_name", "agent_first_name", "agent_last_name", "agent_email",
    "application_notes", "internal_notes", "notes_comments",
    "latitude", "longitude", "lat", "lon",
}

# Field-name markers that, when present in a generated page, indicate an
# excluded source field leaked through.
EXCLUDED_FIELD_MARKERS = {
    "ein_tin", "business_email", "business_phone", "mailing_address_1",
    "business_address_1", "agent_email", "application_notes", "internal_notes",
}


@dataclass
class Finding:
    path: str
    pattern: str
    snippet: str
    line: int = 0

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.path}:{self.line} [{self.pattern}] {self.snippet!r}"


@dataclass
class PrivacySpec:
    """Allowlist/exclusion policy for one state's generated content."""

    state: str
    excluded_field_names: set = field(default_factory=lambda: set(EXCLUDED_FIELD_NAMES))
    excluded_markers: set = field(default_factory=lambda: set(EXCLUDED_FIELD_MARKERS))
    entity_allowlists: dict = field(default_factory=dict)   # entity_type -> fields

    def allowed_fields(self, entity_type: str) -> list[str]:
        return self.entity_allowlists.get(entity_type, [])


def scan_text(text: str, spec: PrivacySpec, *, path: str = "<text>") -> list[Finding]:
    """Scan one Markdown payload for excluded field names and sensitive values."""
    findings: list[Finding] = []
    lower = text.lower()

    for marker in sorted(spec.excluded_markers):
        if re.search(rf"\b{re.escape(marker)}\b", lower):
            index = lower.find(marker)
            snippet = text[max(0, index - 40): index + 60].replace("\n", " ")
            findings.append(Finding(path, f"field:{marker}", snippet))

    patterns = [
        ("ein/tin", EIN_RE),
        ("email", EMAIL_RE),
        ("phone", PHONE_RE),
        ("street-address", STREET_RE),
        ("coordinates", COORD_PAIR_RE),
        ("coordinates", COORD_RE),
    ]
    for label, pattern in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            snippet = text[max(0, start - 40): end + 60].replace("\n", " ")
            findings.append(Finding(path, label, snippet))
    return findings


def scan_directory(
    content_root: Path,
    spec: PrivacySpec,
    *,
    only_collections: Optional[list[str]] = None,
) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(content_root.rglob("*.md")):
        rel = path.relative_to(content_root)
        parts = rel.parts
        if not parts:
            continue
        collection = parts[0]
        if collection in ("includes",) or parts[-1].startswith("_"):
            continue
        if only_collections and collection not in only_collections:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        findings.extend(scan_text(text, spec, path=rel.as_posix()))
    return findings


def assert_clean(findings: list[Finding]) -> None:
    if findings:
        preview = "\n".join(f"  {finding}" for finding in findings[:20])
        raise PrivacyViolationError(
            f"privacy scan found {len(findings)} issue(s) in generated Markdown:\n{preview}"
        )


# ---------------------------------------------------------------------------
# Relation targets
# ---------------------------------------------------------------------------


def collect_entity_ids(content_root: Path) -> set[str]:
    """Collect entity IDs declared in frontmatter across the content tree."""
    ids = set()
    for path in content_root.rglob("*.md"):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^---\n(.*?)\n---", text, flags=re.S)
        if not match:
            continue
        id_match = re.search(r"^id:\s*(.+)$", match.group(1), flags=re.M)
        if id_match:
            value = id_match.group(1).strip().strip('"')
            ids.add(value)
    return ids


RELATION_RE = re.compile(r"^relations:\s*\[(.*)\]$", flags=re.M)


def validate_relations(content_root: Path) -> list[str]:
    """Return a list of broken relation targets (empty list == all good)."""
    entity_ids = collect_entity_ids(content_root)
    broken = []
    for path in sorted(content_root.rglob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = RELATION_RE.search(text)
        if not match:
            continue
        for target in match.group(1).split(","):
            target = target.strip()
            if not target:
                continue
            if "=" in target:
                target = target.split("=", 1)[1].strip()
            if target and target not in entity_ids:
                broken.append(f"{path.relative_to(content_root)}: {target}")
    return broken
