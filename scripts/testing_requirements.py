#!/usr/bin/env python3
"""Validate and render jurisdiction testing-requirement records.

Canonical structured data lives in ``data/testing-requirements/<state>.json``.
This script validates it against the schema in
``scripts/ingest/testing_requirements.py`` and renders the human-readable
records under ``content/requirements/TREQ-XXXX.md``. The JSON is the source of
truth; the markdown is a derived view (pipeline: source evidence -> pages).

Usage:
    python3 scripts/testing_requirements.py --validate   # check both datasets
    python3 scripts/testing_requirements.py --render     # write TREQ pages
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ingest.testing_requirements import (  # noqa: E402
    read_requirements,
    validate_requirements_file,
    render_requirements_markdown,
)

DATA_DIR = ROOT / "data" / "testing-requirements"
CONTENT_DIR = ROOT / "content" / "requirements"

# Stable registry anchors for the two reference jurisdictions. Keep in sync
# with content/ (jurisdictions/TJUR-0001 = CA, TJUR-0002 = MA).
JURISDICTIONS = {
    "california": {
        "title": "California Testing Requirements — Action Limits and Panel (Primary Citations)",
        "jurisdiction_id": "jurisdictions/TJUR-0001",
        "overview_id": "requirements/TREQ-0001",
        "tags": ["requirements", "testing", "action-limits", "california"],
        "summary": "Primary-cited testing panel, numeric action limits, and process rules for California cannabis goods under 4 CCR Division 42 Chapter 6.",
    },
    "massachusetts": {
        "title": "Massachusetts Testing Requirements — Action Limits and Panel (Primary Citations)",
        "jurisdiction_id": "jurisdictions/TJUR-0002",
        "overview_id": "requirements/TREQ-0002",
        "tags": ["requirements", "testing", "action-limits", "massachusetts"],
        "summary": "Primary-cited testing panel, action limits, and process rules for Massachusetts under 935 CMR 500.160 / 501.160 and the CCC's Sampling and Analysis Protocol.",
    },
}

_TREQ_RE = re.compile(r"^TREQ-(\d{4})$")


def next_treq_id() -> str:
    used: set[int] = set()
    for path in CONTENT_DIR.glob("TREQ-*.md"):
        match = _TREQ_RE.match(path.stem)
        if match:
            used.add(int(match.group(1)))
    number = 1
    while number in used:
        number += 1
    return f"TREQ-{number:04d}"


def render_record(state: str, req, treq_id: str) -> str:
    meta = JURISDICTIONS[state]
    relations = [
        f"relates_to={meta['jurisdiction_id']}",
        f"relates_to={meta['overview_id']}",
    ]
    frontmatter = (
        "---\n"
        f"id: requirements/{treq_id}\n"
        f"title: \"{meta['title']}\"\n"
        "parent: requirements\n"
        "status: published\n"
        f"tags: [{', '.join(meta['tags'])}]\n"
        f"relations: [{', '.join(relations)}]\n"
        f"summary: \"{meta['summary']}\"\n"
        "---\n\n"
    )
    provenance = (
        "\n## Source & Provenance\n\n"
        f"- **Generator**: scripts/testing_requirements.py (schema v{req.to_dict()['schema_version']})\n"
        f"- **Jurisdiction**: {req.jurisdiction_label}, United States\n"
        f"- **Retrieval date**: {req.updated_date}\n"
        "- **Research status**: " + req.research_status + "\n"
        "- **Data policy**: Numeric limits recorded only with primary citations. "
        "Values marked `pending-transcription` are located in the cited source but "
        "not yet transcribed from image-based tables; they are gaps, not zeros.\n"
    )
    return frontmatter + render_requirements_markdown(req) + provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="validate datasets only")
    parser.add_argument("--render", action="store_true", help="render TREQ pages")
    args = parser.parse_args()

    if not args.validate and not args.render:
        args.validate = True
        args.render = True

    problems: list[str] = []
    datasets: dict[str, object] = {}
    for path in sorted(DATA_DIR.glob("*.json")):
        state = path.stem
        if state not in JURISDICTIONS:
            problems.append(f"{path.name}: unknown jurisdiction key {state!r}")
            continue
        req = read_requirements(path)
        datasets[state] = req
        found = validate_requirements_file(path)
        problems.extend(f"{state}: {problem}" for problem in found)

    if problems:
        for problem in problems:
            print(f"testing_requirements: error: {problem}", file=sys.stderr)
        return 1

    if args.render:
        treq_ids: dict[str, str] = {}
        for state in sorted(JURISDICTIONS):
            treq_ids[state] = next_treq_id()
        for state, req in sorted(datasets.items()):
            treq_id = treq_ids[state]
            out = CONTENT_DIR / f"{treq_id}.md"
            out.write_text(render_record(state, req, treq_id), encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)} ({len(req.limits)} limits, {len(req.panel)} panel categories)")
    else:
        for state, req in sorted(datasets.items()):
            print(f"{state}: ok ({len(req.limits)} limits, {len(req.panel)} panel categories)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
