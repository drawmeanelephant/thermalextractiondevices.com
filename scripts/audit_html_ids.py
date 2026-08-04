#!/usr/bin/env python3
"""Audit rendered HTML for duplicate id attributes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


ID_ATTRIBUTE = re.compile(r"\bid\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))")


def audit(root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in sorted(root.rglob("*.html")):
        ids: list[str] = []
        for match in ID_ATTRIBUTE.finditer(path.read_text(encoding="utf-8")):
            ids.append(next(value for value in match.groups() if value is not None))
        duplicates = {value: count for value, count in Counter(ids).items() if count > 1}
        if duplicates:
            findings.append({"path": path.relative_to(root).as_posix(), "duplicates": duplicates})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Rendered HTML directory")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        findings = audit(args.root)
    except (OSError, UnicodeError) as error:
        print(f"HTML ID audit: error: {error}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(findings, ensure_ascii=False, sort_keys=True))
    else:
        extra = sum(sum(count - 1 for count in item["duplicates"].values()) for item in findings)
        print(f"HTML ID audit: {len(findings)} pages with duplicate IDs; {extra} duplicate occurrences")
        for item in findings[:20]:
            print(f"{item['path']}: {item['duplicates']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
