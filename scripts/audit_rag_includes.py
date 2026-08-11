#!/usr/bin/env python3
"""Audit source include references and resolved RAG exports.

The source audit validates that every ``content`` include marker resolves to a
safe file below ``content/includes``. The export audit is intentionally
stricter: a resolved RAG surface must contain no include markers at all.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Allow the publish wrapper to invoke this file as ``python3 scripts/...`` as
# well as allowing the test suite to import it as ``scripts....``.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.rag_includes import (
    IncludeAudit,
    audit_content_includes,
    audit_export_includes,
    format_include_issues,
)


def _report(label: str, audit: IncludeAudit) -> bool:
    if audit.issues:
        print(
            f"❌ {label} failed with {len(audit.issues)} finding(s):",
            file=sys.stderr,
        )
        print(format_include_issues(audit.issues), file=sys.stderr)
        return False
    print(
        f"✅ {label} passed: {audit.files_scanned} Markdown file(s), "
        f"{audit.reference_count} include marker(s), "
        f"{len(audit.unique_references)} unique include file(s)."
    )
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit TED include references and unresolved RAG markers."
    )
    parser.add_argument(
        "--content",
        type=Path,
        help="content root to validate against its includes/ directory",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="derived RAG export that must contain no include markers",
    )
    parser.add_argument(
        "--include-dir",
        default="includes",
        help="include directory below --content (default: includes)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.content is None and args.export is None:
        print("ERROR: provide --content, --export, or both", file=sys.stderr)
        return 2

    passed = True
    try:
        if args.content is not None:
            passed = _report(
                "Content include audit",
                audit_content_includes(args.content, include_dir=args.include_dir),
            ) and passed
        if args.export is not None:
            passed = _report(
                "Unresolved-include audit",
                audit_export_includes(args.export),
            ) and passed
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot audit RAG includes: {exc}", file=sys.stderr)
        return 2
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
