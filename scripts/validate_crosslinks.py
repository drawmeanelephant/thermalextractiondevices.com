#!/usr/bin/env python3
"""Validate the evidence-aware crosslink layer against the content tree.

Wraps ``scripts.crosslinks`` validation so the derived navigation graph can be
gated on every build without emitting artifacts. Checks:

* CXL-01 broken generated HTML links (with ``--html-dir``);
* CXL-02 relations to nonexistent entity IDs;
* CXL-03 incorrect relation types (analyte targets, lab targets, product
  targets, cultivar-claim targets, lineage/breeder endpoints);
* CXL-04 duplicate generated edges and duplicate targets within a section;
* CXL-05 derived edges presented as direct facts;
* CXL-06 derived edges without an evidence trace;
* CXL-07 frontmatter relations targeting nonexistent pages;
* CXL-08 unbounded page expansion (per-section caps);
* CXL-09 duplicate generated navigation targets in one section;
* CXL-10 unknown edge classes;
* CXL-13 fully isolated non-trunk satellite collections.

Exit codes: 0 = clean, 1 = findings, 2 = tool failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crosslinks import (  # noqa: E402
    build_graph,
    load_coa_records,
    load_entities,
    validate_graph,
    validate_index_pages,
    validate_injected_html,
    validate_sections,
)
from scripts.cultivar_claims import load_claims  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path("content"),
        help="content tree whose frontmatter supplies direct relations",
    )
    parser.add_argument(
        "--map", type=Path, default=Path("metadata/id-map.jsonl"),
        help="entity registry (id-map.jsonl)",
    )
    parser.add_argument(
        "--claims", type=Path, default=Path("metadata/cultivar-claims.jsonl"),
        help="cultivar identity claim registry",
    )
    parser.add_argument(
        "--coa", type=Path, default=Path("metadata/coa-records.jsonl"),
        help="durable COA records (JSONL, one CoaRecord per line)",
    )
    parser.add_argument(
        "--html-dir", type=Path, default=None,
        help="rendered HTML directory; when given, broken generated links are "
        "also checked (CXL-01)",
    )
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args()

    try:
        entities = load_entities(args.map)
        claims = load_claims(args.claims) if args.claims.exists() else []
        coa_records = load_coa_records(args.coa)
        graph = build_graph(args.root, entities, claims, coa_records)
        problems = validate_graph(graph, args.root)
        problems.extend(validate_sections(graph))
        if args.html_dir is not None:
            if not args.html_dir.exists():
                print(
                    f"Crosslinks validation: error: --html-dir {args.html_dir} "
                    "does not exist",
                    file=sys.stderr,
                )
                return 2
            problems.extend(validate_injected_html(args.html_dir, graph))
            problems.extend(validate_index_pages(args.html_dir, graph))
    except (OSError, ValueError, KeyError) as error:
        print(f"Crosslinks validation: error: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "ok": not problems,
            "entityCount": len(graph.entities),
            "edgeCount": len(graph.edges),
            "coaRecordCount": len(coa_records),
            "findings": problems,
        }, ensure_ascii=False, indent=2, sort_keys=True))
    elif problems:
        print(
            f"Crosslinks validation: {len(problems)} problem(s):",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    else:
        print(
            f"Crosslinks validation: {len(graph.entities)} entities, "
            f"{len(graph.edges)} edges, {len(coa_records)} COA record(s); "
            "no problems"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
