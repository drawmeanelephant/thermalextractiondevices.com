#!/usr/bin/env python3
"""Audit relative Markdown links against the Thermal Extraction Devices source tree."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


LINK = re.compile(r"\]\(([^)\s]+)")


def audit(root: Path) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    root = root.resolve()
    for source in sorted(root.rglob("*.md")):
        for destination in LINK.findall(source.read_text(encoding="utf-8")):
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path.lower().endswith(".md"):
                continue
            target = root / parsed.path.lstrip("/") if parsed.path.startswith("/") else source.parent / parsed.path
            target = target.resolve()
            if root not in target.parents and target != root:
                missing.append((str(source.relative_to(root)), destination))
            elif not target.is_file():
                missing.append((str(source.relative_to(root)), destination))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Markdown content directory")
    args = parser.parse_args()
    try:
        missing = audit(args.root)
    except (OSError, UnicodeError) as error:
        print(f"Markdown link audit: error: {error}", file=sys.stderr)
        return 2
    if missing:
        print(f"Markdown link audit: {len(missing)} missing local link(s)", file=sys.stderr)
        for source, destination in missing:
            print(f"  {source}: {destination}", file=sys.stderr)
        return 1
    print("Markdown link audit: all local Markdown links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
