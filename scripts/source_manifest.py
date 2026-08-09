#!/usr/bin/env python3
"""Jurisdiction source manifest tooling.

Usage
-----

    python3 scripts/source_manifest.py --validate                # validate all manifests
    python3 scripts/source_manifest.py --render california      # markdown report
    python3 scripts/source_manifest.py --stubs                  # (re)generate un-researched stubs

Manifests live in ``data/source-manifests/``. Stub manifests are generated for
every US state (and DC) that has not been researched; they declare
``researched: false`` and must never claim sources they do not have.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ingest.sources import (  # noqa: E402
    SourceManifest,
    build_stub_manifest,
    read_manifest,
    render_manifest_markdown,
    write_manifest,
)

MANIFEST_DIR = ROOT / "data" / "source-manifests"

# All US states + DC. State codes with active researched manifests are skipped
# by --stubs so they are never overwritten.
JURISDICTIONS = [
    ("alabama", "AL"), ("alaska", "AK"), ("arizona", "AZ"), ("arkansas", "AR"),
    ("california", "CA"), ("colorado", "CO"), ("connecticut", "CT"),
    ("delaware", "DE"), ("florida", "FL"), ("georgia", "GA"), ("hawaii", "HI"),
    ("idaho", "ID"), ("illinois", "IL"), ("indiana", "IN"), ("iowa", "IA"),
    ("kansas", "KS"), ("kentucky", "KY"), ("louisiana", "LA"), ("maine", "ME"),
    ("maryland", "MD"), ("massachusetts", "MA"), ("michigan", "MI"),
    ("minnesota", "MN"), ("mississippi", "MS"), ("missouri", "MO"),
    ("montana", "MT"), ("nebraska", "NE"), ("nevada", "NV"),
    ("new-hampshire", "NH"), ("new-jersey", "NJ"), ("new-mexico", "NM"),
    ("new-york", "NY"), ("north-carolina", "NC"), ("north-dakota", "ND"),
    ("ohio", "OH"), ("oklahoma", "OK"), ("oregon", "OR"),
    ("pennsylvania", "PA"), ("rhode-island", "RI"), ("south-carolina", "SC"),
    ("south-dakota", "SD"), ("tennessee", "TN"), ("texas", "TX"),
    ("utah", "UT"), ("vermont", "VT"), ("virginia", "VA"),
    ("washington", "WA"), ("west-virginia", "WV"), ("wisconsin", "WI"),
    ("wyoming", "WY"), ("district-of-columbia", "DC"),
]

RESEARCHED = {"california", "massachusetts"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true",
                       help="validate every manifest and stub")
    group.add_argument("--render", metavar="STATE",
                       help="render a markdown report for one state")
    group.add_argument("--stubs", action="store_true",
                       help="(re)generate stub manifests for un-researched states")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.stubs:
        count = 0
        for slug, code in JURISDICTIONS:
            if slug in RESEARCHED:
                continue
            stub = build_stub_manifest(slug)
            write_manifest(MANIFEST_DIR / "stubs" / f"{slug}.json", stub)
            count += 1
        print(f"source_manifest: wrote {count} stub manifests under "
              f"data/source-manifests/stubs/")
        return 0

    if args.render:
        state = args.render
        path = MANIFEST_DIR / f"{state}.json"
        if not path.is_file():
            print(f"source_manifest: no manifest for {state}", file=sys.stderr)
            return 1
        print(render_manifest_markdown(read_manifest(path)))
        return 0

    # --validate
    problems: list[str] = []
    checked = 0
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        checked += 1
        manifest = read_manifest(path)
        problems.extend(f"{path.name}: {p}" for p in manifest.validate())
    for path in sorted((MANIFEST_DIR / "stubs").glob("*.json")):
        checked += 1
        manifest = read_manifest(path)
        problems.extend(f"stubs/{path.name}: {p}" for p in manifest.validate())
    if problems:
        print(f"source_manifest: {len(problems)} problem(s) across {checked} manifests")
        for problem in problems[:20]:
            print(f"  - {problem}")
        return 1
    print(f"source_manifest: validated {checked} manifests; all clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
