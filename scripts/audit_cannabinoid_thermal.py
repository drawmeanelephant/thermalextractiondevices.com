#!/usr/bin/env python3
"""Audit condition and provenance language in cannabinoid thermal records.

This is a deliberately narrow content audit.  It does not decide whether a
number is chemically correct; it catches the more basic failure where a
temperature or pressure is presented without saying what was measured, under
which conditions, or whether it is a device setting rather than a compound
property.

Rules
-----
THERM-001 (error)  A numeric boiling-point claim must name its pressure (or
                   explicitly say that the atmospheric/reduced-pressure value
                   is unresolved) and identify a prediction/derivation when it
                   is not a direct phase-change observation.
THERM-002 (error)  A numeric vapor-pressure claim must state a temperature and
                   a measurement/estimate/analogy status.
THERM-003 (error)  A numeric decomposition/decarboxylation/stability claim
                   must state a study condition or explicitly remain unresolved.
THERM-004 (error)  A record with thermal-extraction discussion must distinguish
                   pure-compound boiling point, device setpoint, and material or
                   sample temperature.
THERM-005 (error)  A numeric thermal claim must carry a footnote or explicit
                   unresolved language.
THERM-006 (error)  A thermal claim in the physical-properties, thermal-context,
                   processing, or degradation sections must carry a footnote or
                   explicitly remain unresolved.

Quoted marketing corrections are ignored when the surrounding sentence
clearly rejects the quoted value.  The audit is intended to be useful both on
the real collection and on small fixtures in tests.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


THERMAL_WORDS = re.compile(
    r"\b(?:boil(?:ing|s|ed)?|vapor\s+pressure|vapou?r\s+pressure|"
    r"vapor(?:i[sz]ation|i[sz]e|i[sz]es|i[sz]ed)|vapou?r(?:i[sz]ation|i[sz]e|i[sz]es|i[sz]ed)|"
    r"evapor(?:ation|ate|ates|ated|ating)|decarboxyl\w*|decompos\w*|thermal\s+stabil\w*)\b",
    re.IGNORECASE,
)
NUMERIC = re.compile(
    r"(?:[≈~<>≤≥]?\s*\d+(?:[.,]\d+)?(?:\s*[–-]\s*\d+(?:[.,]\d+)?)?\s*"
    r"(?:°\s*[CFK]|K\b|Pa\b|Torr\b|torr\b|mmHg\b|kPa\b|mbar\b|atm\b)|"
    r"\b\d+(?:[.,]\d+)?\s*(?:×\s*10|x\s*10))",
    re.IGNORECASE,
)
PRESSURE = re.compile(
    r"\b(?:1\s*atm|101(?:\.325)?\s*kPa|760\s*mmhg|atmospheric|"
    r"normal\s+boil|reduced\s+pressure|vacuum|torr|mmhg|kpa|mbar|"
    r"external\s+pressure|pressure)\b",
    re.IGNORECASE,
)
STATUS = re.compile(
    r"\b(?:measured|measurement|direct(?:ly)?|predicted|prediction|estimated|"
    r"estimate|extrapolat(?:ed|ion)|derived|calculated|by\s+analogy|analogy|"
    r"not\s+(?:experimentally\s+)?(?:measured|characteri[sz]ed)|"
    r"no\s+(?:direct\s+)?(?:experimental\s+)?data|unresolved|unknown|"
    r"unverified|not\s+reported)\b",
    re.IGNORECASE,
)
TEMPERATURE = re.compile(r"(?:°\s*[CFK]|\b\d+(?:[.,]\d+)?\s*K\b)", re.IGNORECASE)
CONDITION = re.compile(
    r"\b(?:in\s+(?:air|plant\s+matrix|botanical\s+matrix|a\s+matrix|solution|"
    r"extract|resin)|under\s+(?:vacuum|pressur|gc|thermal|the\s+cited)|"
    r"pressur(?:ized|e)|vacuum|gc(?:-|-\s*)injector|injector|solid\s+state|"
    r"matrix|sample|residence|prolonged|over\s+time|for\s+\S+\s+(?:min|minutes|h|hours)|"
    r"melting|melt|storage|stored|store|"
    r"study\s+condition|study-specific|condition-dependent|temperature/time|"
    r"device\s+(?:setpoint|setting)|chamber\s+temperature|"
    r"not\s+(?:a\s+)?(?:universal|intrinsic)|no\s+(?:universal|intrinsic)|"
    r"not\s+established|not\s+characteri[sz]ed|remains?\s+unresolved|"
    r"by\s+analogy|analog(?:y|ous)|unresolved)\b",
    re.IGNORECASE,
)
UNRESOLVED = re.compile(
    r"\b(?:not\s+(?:experimentally\s+)?(?:measured|reported|characteri[sz]ed)|"
    r"no\s+(?:reliable|authoritative|direct|compound-specific|defensible|"
    r"experiment(?:al|ally))|unresolved|unknown|unverified|not\s+established|"
    r"not\s+a\s+(?:universal|intrinsic)|no\s+(?:universal|intrinsic)|"
    r"by\s+analogy|predicted|estimated|extrapolat(?:ed|ion)|derived|calculated)\b",
    re.IGNORECASE,
)
REFERENCE = re.compile(r"\[\^[^\]]+\]")


def _is_rebuttal(line: str) -> bool:
    """Return true for a sentence explicitly rejecting a quoted bad value."""

    lower = line.lower()
    return bool(
        re.search(
            r"(?:marketing|blog|popular|vape|vaporizer).{0,100}"
            r"(?:not|incorrect|misinterpret|confus|not\s+a\s+physical)",
            lower,
        )
        or re.search(
            r"(?:not|no)\s+(?:a\s+)?(?:true\s+)?(?:atmospheric\s+)?boiling\s+point",
            lower,
        )
        or re.search(r"decompos\w*\s+before\s+boil", lower)
        or re.search(r"(?:not\s+supported|not\s+a\s+verified|not\s+verified)", lower)
    )


def _in_frontmatter(lines: list[str], index: int) -> bool:
    return sum(1 for line in lines[: index + 1] if line.strip() == "---") == 1


def _finding(path: Path, line_number: int, code: str, message: str) -> tuple[str, str, str]:
    return ("error", code, f"{path.name}:{line_number}: {message}")


def audit_file(path: Path) -> list[tuple[str, str, str]]:
    """Audit one cannabinoid Markdown record."""

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[tuple[str, str, str]] = []

    section = ""
    audited_sections = {
        "Physical properties",
        "Thermal-extraction context",
        "Biosynthesis and processing",
        "Degradation products",
    }

    for number, line in enumerate(lines, start=1):
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1)
        if _in_frontmatter(lines, number - 1) or line.lstrip().startswith("[^"):
            continue
        if "{{include" in line or line.lstrip().startswith("#"):
            continue
        if section in audited_sections and THERMAL_WORDS.search(line) and not REFERENCE.search(line) and not UNRESOLVED.search(line):
            findings.append(
                _finding(
                    path,
                    number,
                    "THERM-006",
                    "thermal-property statement needs a footnote or explicit unresolved wording",
                )
            )
        if not THERMAL_WORDS.search(line) or not NUMERIC.search(line):
            continue

        if re.search(r"\bboil(?:ing|s|ed)?\b", line, re.IGNORECASE) and not _is_rebuttal(line):
            if not PRESSURE.search(line) or not (STATUS.search(line) or UNRESOLVED.search(line)):
                findings.append(
                    _finding(
                        path,
                        number,
                        "THERM-001",
                        "numeric boiling-point claim needs explicit pressure and measurement/prediction status",
                    )
                )

        if re.search(r"vapor\s+pressure|vapou?r\s+pressure", line, re.IGNORECASE):
            if not TEMPERATURE.search(line) or not STATUS.search(line):
                findings.append(
                    _finding(
                        path,
                        number,
                        "THERM-002",
                        "numeric vapor-pressure claim needs temperature and measured/estimated/analogy status",
                    )
                )

        if re.search(r"decarboxyl|decompos|thermal\s+stabil", line, re.IGNORECASE):
            if not CONDITION.search(line):
                findings.append(
                    _finding(
                        path,
                        number,
                        "THERM-003",
                        "numeric thermal claim needs a study condition or explicit unresolved wording",
                    )
                )

        if not REFERENCE.search(line) and not UNRESOLVED.search(line):
            findings.append(
                _finding(
                    path,
                    number,
                    "THERM-005",
                    "numeric thermal claim needs a footnote or explicit unresolved wording",
                )
            )

    if THERMAL_WORDS.search(text) and "## Thermal-extraction context" in text:
        # The shared include contributes the pure-compound/device distinction;
        # the record itself must still name the sample/material side.
        context = text.split("## Thermal-extraction context", 1)[1]
        context = context.split("\n## ", 1)[0]
        if not re.search(
            r"(?:sample\s+temperature|material\s+temperature|plant\s+matrix|"
            r"botanical\s+matrix|from\s+the\s+matrix|matrix)",
            context,
            re.IGNORECASE,
        ):
            findings.append(
                _finding(
                    path,
                    next(i for i, line in enumerate(lines, 1) if line == "## Thermal-extraction context"),
                    "THERM-004",
                    "thermal context must identify sample/material temperature or matrix behavior",
                )
            )
        if not re.search(r"device\s+(?:setpoint|setting)|chamber\s+temperature|vaporizer", context, re.IGNORECASE):
            findings.append(
                _finding(
                    path,
                    next(i for i, line in enumerate(lines, 1) if line == "## Thermal-extraction context"),
                    "THERM-004",
                    "thermal context must identify device setpoint/chamber behavior",
                )
            )
        body = text.split("## Sources", 1)[0]
        if not re.search(r"(?:thermodynamic\s+boiling|pure\s+compound|physical\s+reference\s+property|normal\s+boiling)", body, re.IGNORECASE):
            findings.append(
                _finding(
                    path,
                    next(i for i, line in enumerate(lines, 1) if line == "## Thermal-extraction context"),
                    "THERM-004",
                    "record must distinguish thermodynamic/pure-compound boiling point",
                )
            )

    return findings


def _cannabinoid_dir(root: Path) -> Path:
    root = root.resolve()
    candidates = [root / "cannabinoids", root / "content" / "cannabinoids"]
    if root.name == "cannabinoids":
        candidates.insert(0, root)
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"could not find cannabinoid records below {root}")


def audit(root: Path) -> list[tuple[str, str, str]]:
    directory = _cannabinoid_dir(root)
    findings: list[tuple[str, str, str]] = []
    for path in sorted(directory.glob("*.md")):
        findings.extend(audit_file(path))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="repository root or content directory")
    args = parser.parse_args()
    try:
        findings = audit(args.root)
    except (OSError, UnicodeError) as error:
        print(f"Cannabinoid thermal audit: error: {error}", file=sys.stderr)
        return 2
    for severity, code, message in findings:
        print(f"  [{severity.upper()}] {code}: {message}")
    print(f"Cannabinoid thermal audit: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
