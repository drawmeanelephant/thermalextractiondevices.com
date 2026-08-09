#!/usr/bin/env python3
"""Validate the cultivar identity claim registry against the content tree."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cultivar_claims import load_claims, validate_claims  # noqa: E402
from scripts.ingest.validation import collect_entity_ids  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path("content"),
        help="content tree whose frontmatter entity IDs are the claim graph",
    )
    parser.add_argument(
        "--claims", type=Path, default=Path("metadata/cultivar-claims.jsonl"),
        help="JSONL claim registry to validate",
    )
    args = parser.parse_args()

    try:
        entity_ids = collect_entity_ids(args.root)
        claims = load_claims(args.claims)
        problems = validate_claims(claims, entity_ids)
    except (OSError, ValueError) as error:
        print(f"Cultivar claims: error: {error}", file=sys.stderr)
        return 1

    if problems:
        print(
            f"Cultivar claims: {len(problems)} problem(s) in {args.claims}:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print(
        f"Cultivar claims: {len(claims)} claim(s) validated against "
        f"{len(entity_ids)} content entities; no problems"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
