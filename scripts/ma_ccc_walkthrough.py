#!/usr/bin/env python3
"""READ-ONLY walk-through: map one real Massachusetts CCC package through the model.

**Massachusetts is NOT ingested, altered, or published by this script.** The
Massachusetts pipeline is fixture-only and merge-blocked by its own guards
(``state_ingest --fixtures-only`` exits 2 without ``--allow-fixture-content``),
and this task explicitly excludes Massachusetts work. This walk-through exists
so the *mapping* can be demonstrated and so the verification checklist is
concrete — it reads the verbatim fixture excerpt exactly as the tests do
(``tests/test_coa_model.py``), maps it through the existing adapter
(``scripts.ingest.states.massachusetts.normalize_testing_common`` →
``scripts.coa_model.from_massachusetts_normalized`` →
``scripts.coa_model.massachusetts_rows_to_record``), and writes **nothing**.

The package walked here: Metrc ``33fadba74ecad1e89afa916ac400043bf1c0e78cd3baa4e7e97b406958058a1c``
(2025-06-24, Lab_H — anonymized by the Commission), four rows:

    THC 1.34 %  → numeric      Lead 0.0 ppm  → zero (flagged, never nd)
    Arsenic 0.0 ppm → zero     Total Yeast and Mold 0.0 CFU/g → zero

When the pipeline is unblocked (a verified live CCC snapshot ingested), the
same mapping is reused unchanged; only the record identity changes:
provisional ``ma-ccc:<tag>`` → canonical ``lab-results/TLAB-XXXX``, real lab
names from the license registry, and provenance (dataset URL, retrieval date,
hash, upstream row keys).

Usage:
    python3 scripts/ma_ccc_walkthrough.py            # model walk (print only)
    python3 scripts/ma_ccc_walkthrough.py --write    # refuses: MA publication is blocked
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.coa_model import (
    ResultState,
    censorship_summary,
    coa_problems,
    coa_warnings,
    from_massachusetts_normalized,
    massachusetts_rows_to_record,
)
from scripts.ingest.states.massachusetts import normalize_testing_common

FIXTURE = ROOT / "tests" / "fixtures" / "massachusetts" / "CCC_Testing_Results_2025.csv"
RELEASE = "CCC_Testing_Results_2025"
PACKAGE_PREFIX = "33fadba74ecad1e89afa916ac400043bf1c0e78cd3baa4e7e97b406958058a1c"

MA_BLOCK_NOTICE = (
    "Massachusetts publication is BLOCKED by design: the CCC pipeline is "
    "fixture-only and merge-blocked, and this task excludes Massachusetts "
    "content. state_ingest --fixtures-only exits 2 without "
    "--allow-fixture-content. No content page was written; no pipeline "
    "was altered; the model maps the same rows unchanged once a verified "
    "live snapshot exists."
)


def load_package_rows() -> list[dict]:
    """Read the verbatim fixture rows for the walked package (read-only)."""
    rows = []
    with open(FIXTURE, newline="", encoding="utf-8-sig") as handle:
        for raw in csv.DictReader(handle):
            if raw["METRC SOURCE TAG"].startswith(PACKAGE_PREFIX):
                rows.append(raw)
    if not rows:
        raise SystemExit(f"no fixture rows for package prefix {PACKAGE_PREFIX!r}")
    return rows


def walk() -> tuple[list[dict], list[dict], object]:
    """Return (raw_rows, normalized_rows, CoaRecord) for the package."""
    raw_rows = load_package_rows()
    normalized = [
        normalize_testing_common(r, release=RELEASE) for r in raw_rows
    ]
    rec = massachusetts_rows_to_record(
        normalized, metrc_tag=raw_rows[0]["METRC SOURCE TAG"]
    )
    return raw_rows, normalized, rec


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="(intentionally unsupported) write a content page")
    args = parser.parse_args(argv)

    if args.write:
        print(MA_BLOCK_NOTICE, file=sys.stderr)
        return 2

    raw_rows, normalized, rec = walk()
    tag = raw_rows[0]["METRC SOURCE TAG"]

    print("=== Massachusetts CCC package walk-through (READ-ONLY) ===")
    print(f"source: {FIXTURE.relative_to(ROOT)} (verbatim excerpt, 39 rows)")
    print(f"package: {tag}")
    print(f"date: {raw_rows[0]['DATE']}  lab: {raw_rows[0]['LAB PERFORMING THE TEST']} "
          f"(anonymized by CCC)  metrc_id: {raw_rows[0]['METRC ID'][:18]}…")
    print()
    print("=== Mapped record (massachusetts_rows_to_record) ===")
    print(f"  report_id:   {rec.report.report_id}  (PROVISIONAL — non-verified only)")
    print(f"  record_kind: {rec.batch.record_kind.value}")
    print(f"  batch_id:    {rec.batch.batch_id[:18]}…  metrc_tag set")
    print(f"  laboratory:  {rec.report.laboratory.name if rec.report.laboratory else None} "
          "(no canonical TSTL id — anonymized; real names come from the license registry)")
    print(f"  basis:       {rec.batch.basis.value}  (CCC CSVs do not encode basis)")
    print()
    print("=== Measurements (from_massachusetts_normalized) ===")
    print("| analyte | printed | state | value | unit | note |")
    for m in rec.measurements:
        note = ""
        if m.state is ResultState.ZERO:
            note = "flagged for review — never treated as nd"
        elif m.state is ResultState.NUMERIC:
            note = "fully quantified"
        print(f"| {m.compound_name} | {m.reported_value} | {m.state.value} | "
              f"{m.value} | {m.unit} | {note} |")
    print()
    print("=== Result-state census ===")
    for state, count in censorship_summary(rec).items():
        if count:
            print(f"  {state}: {count}")
    print()
    print("=== Hard validation (coa_problems) ===")
    print(f"  {coa_problems(rec)}  (unverified record is legal)")
    print()
    print("=== Soft warnings (coa_warnings) ===")
    for w in coa_warnings(rec):
        print(f"  - {w}")
    print()
    print("=== What verification requires (BLOCKED until pipeline unblocks) ===")
    print("  1. Fixture guard: state_ingest --fixtures-only exits 2 without")
    print("     --allow-fixture-content; no MA content may be generated until a")
    print("     verified live CCC snapshot is ingested and verified.")
    print("  2. Provenance: official CCC dataset URL, retrieval date, artifact")
    print("     hash, and upstream row keys (ma-ccc ingestion step).")
    print("  3. Canonical ids: lab-results/TLAB-XXXX (report), testing-")
    print("     laboratories/TSTL-* (real lab names), organizations/TORG-* and")
    print("     products/TPRD-* (producer/product) where records exist.")
    print("  4. Missing metadata stays unknown: the CCC CSVs carry no method,")
    print("     LOD/LOQ, or basis — soft warnings persist, and below_lod /")
    print("     below_loq states plus Grade A/B comparisons remain impossible")
    print("     for MA until laboratory method summaries are sourced.")
    print("  5. Explicit zeros stay zeros: Lead/Arsenic/Yeast&Mold printed 0.0")
    print("     are recorded as zero, never converted to nd or missing.")
    print()
    print(MA_BLOCK_NOTICE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
