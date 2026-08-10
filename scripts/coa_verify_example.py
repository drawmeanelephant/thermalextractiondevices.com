#!/usr/bin/env python3
"""Walk one real published Certificate of Analysis through the durable COA model.

This is the archive's first VERIFIED COA ingestion (``lab-results/TLAB-0002``),
transcribed by hand from a real published laboratory report:

* **Product:** "Dragonberry 750ml (10mg)" — Edible Liquid (THC beverage),
  client **Powered By Plants**.
* **Laboratory:** Infinite Chemical Analysis Labs, CA (San Diego) —
  ``testing-laboratories/TSTL-0006`` (license C8-0000047-LIC), also the
  archive's ``organizations/TORG-0006``.
* **Batch / Lot / Sample:** 250410-37-002 / ICC-250410 / ICC-250410-37-002.
* **Produced:** 2025-07-11 · collected 2025-04-10 · matrix density
  1.03634 g/ml.
* **Provenance:** official verification endpoint
  ``https://lims.tagleaf.com/coa_/6iE0zRnhl3`` (HTTP 200 at retrieval),
  archived PDF on the client's Shopify CDN, sha256
  ``863b356de58bfa0d2cb77fde1784dc227a4fe30579c349d19dec6654de6f1261``.

The printed document carries the full panels: 16 cannabinoid rows (numeric,
many ND, three calculated totals with formulas), ~42 residual solvents
(Ethanol 10200 µg/g is the only numeric), 7 heavy metals (Lead is the only
``<LOQ``), mycotoxins, microbial (PCR + Petrifilm), and ~90 pesticide analytes
(all ND). This walk-through transcribes the full cannabinoid panel and the
notable safety rows; the complete panel remains authoritative in the source
document, which is linked and hashed (see ``docs/coa-data-model.md`` §8).

``parser_version = "coa-verify-example/1.0"`` is recorded on the record so the
transcription can be re-audited against the source hash.

Usage:
    python3 scripts/coa_verify_example.py            # model walk (print only)
    python3 scripts/coa_verify_example.py --write    # also write the lab-results page
    python3 scripts/coa_verify_example.py --snapshot # Path A: checksum PDF into var/,
                                                     # write datasets/TDTS-0022 record
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.coa_model import (
    AnalyteMeasurement,
    Batch,
    CoaRecord,
    InstrumentTechnique,
    Laboratory,
    MethodMetadata,
    MoistureMethod,
    RecordKind,
    Report,
    ReportingBasis,
    ResultState,
    SourceProvenance,
    censorship_summary,
    coa_problems,
    coa_warnings,
)

# ---------------------------------------------------------------------------
# Provenance constants (the retrieval metadata for this ingestion)
# ---------------------------------------------------------------------------

SOURCE_URL = "https://lims.tagleaf.com/coa_/6iE0zRnhl3"
SOURCE_PDF = (
    "https://cdn.shopify.com/s/files/1/0568/7659/7293/files/"
    "Dragonberry_750ml_COA_Batch_250410-37-002.pdf"
)
DOCUMENT_HASH = "863b356de58bfa0d2cb77fde1784dc227a4fe30579c349d19dec6654de6f1261"
RETRIEVAL_DATE = "2026-08-09"
PARSER_VERSION = "coa-verify-example/1.0"
UPSTREAM_RECORD_ID = "ICC-250410-37-002"

# Path A compliance (docs/graph/coa-migration.md §3): the immutable raw
# snapshot lives in the git-ignored ingest working area, checksummed; the
# dataset record (committed) references it. The public CDN URL is the durable
# public copy.
SNAPSHOT_PATH = ROOT / "var" / "ingest" / "coa-verify" / "raw" \
    / "2026-08-09" / f"{UPSTREAM_RECORD_ID}.pdf"
DATASET_ID = "datasets/TDTS-0022"
DATASET_SLUG = "coa-snapshot/infinitecal-ICC-250410-37-002"
RETRIEVAL_TIMESTAMP = "2026-08-09"

# Canonical compound records that exist for the analytes on this COA
# (metadata/id-map.jsonl). Analytes without a record keep compound_id = null.
COMPOUND_IDS = {
    "CBD": "cannabinoids/TCBN-0002",
    "CBDA": "cannabinoids/TCBN-0003",
    "CBDV": "cannabinoids/TCBN-0004",
    "CBG": "cannabinoids/TCBN-0005",
    "CBGA": "cannabinoids/TCBN-0006",
    "THCA": "cannabinoids/TCBN-0007",
    "THCV": "cannabinoids/TCBN-0008",
    "Pyrethrins": "contaminants/TCNT-0001",
    "Aflatoxin B1": "contaminants/TCNT-0002",
    "Ochratoxin A": "contaminants/TCNT-0003",
    "STEC": "contaminants/TCNT-0004",
    "Salmonella": "contaminants/TCNT-0005",
    "Aspergillus flavus": "contaminants/TCNT-0006",
    "Lead": "contaminants/TCNT-0007",
    "Residual solvents (panel)": "contaminants/TCNT-0008",
}

# The COA prints the amount column in mg/pkg; LOD/LOQ for the cannabinoid
# panel are printed in mg/ml. The % column is w/w computed per 35 g package
# (e.g. 11.0 mg / 35 g = 0.314 mg/g = 0.0314 % w/w).
CANNABINOID_PANEL = [
    # (name, printed, state, amount mg/pkg, (lod, loq) as printed in mg/ml,
    #  calculated formula)
    ("CBC", "ND", ResultState.ND, None, ("0.00114", "0.00341"), None),
    ("CBD", "0.219", ResultState.NUMERIC, 0.219, ("0.000347", "0.00172"), None),
    ("CBDA", "ND", ResultState.ND, None, ("0.000831", "0.00250"), None),
    ("CBDV", "ND", ResultState.ND, None, ("0.000276", "0.00172"), None),
    ("CBG", "ND", ResultState.ND, None, ("0.000393", "0.00172"), None),
    ("CBGA", "ND", ResultState.ND, None, ("0.000612", "0.00184"), None),
    ("CBL", "ND", ResultState.ND, None, ("0.000272", "0.00172"), None),
    ("CBN", "ND", ResultState.ND, None, ("0.000393", "0.00172"), None),
    ("CBT", "ND", ResultState.ND, None, ("0.000493", "0.00172"), None),
    ("Δ8-THC", "0.217", ResultState.NUMERIC, 0.217, ("0.000279", "0.00172"), None),
    ("Δ9-THC", "11.0", ResultState.NUMERIC, 11.0, ("0.000460", "0.00172"), None),
    ("THCA", "ND", ResultState.ND, None, ("0.000632", "0.00190"), None),
    ("THCV", "ND", ResultState.ND, None, ("0.000212", "0.00172"), None),
    ("Total THC", "11.2", ResultState.NUMERIC, 11.2, (None, None),
     "Total THC = Delta-9-THC + (THCA x 0.877)"),
    ("Total CBD", "0.219", ResultState.NUMERIC, 0.219, (None, None),
     "Total CBD = CBD + (CBDA x 0.877)"),
    ("Total Cannabinoids", "11.4", ResultState.NUMERIC, 11.4, (None, None),
     "Total Cannabinoids = Neutral Cannabinoids + (Acidic Cannabinoids * 0.877)"),
]

# Notable safety rows: (name, state, value, unit, lod, loq, compound_id)
SAFETY_ROWS = [
    # (name, printed, state, value, unit, (lod, loq) as printed, compound_id)
    ("Ethanol", "10200", ResultState.NUMERIC, 10200.0, "ug/g", ("4.80", "14.4"), None),
    ("Benzene", "ND", ResultState.ND, None, "ug/g", ("0.400", "1.10"), None),
    ("Toluene", "ND", ResultState.ND, None, "ug/g", ("0.400", "1.20"), None),
    ("Arsenic", "ND", ResultState.ND, None, "ug/g", ("0.00300", "0.00900"), None),
    ("Cadmium", "ND", ResultState.ND, None, "ug/g", ("0.00100", "0.00200"), None),
    ("Lead", "< LOQ", ResultState.BELOW_LOQ, None, "ug/g", ("0.00100", "0.00400"),
     COMPOUND_IDS["Lead"]),
    ("Mercury", "ND", ResultState.ND, None, "ug/g", ("0.00500", "0.0140"), None),
    ("Chromium", "ND", ResultState.ND, None, "ug/g", ("0.00926", "0.0278"), None),
    ("Copper", "0.456", ResultState.NUMERIC, 0.456, "ug/g", ("0.0109", "0.0326"), None),
    ("Nickel", "ND", ResultState.ND, None, "ug/g", ("0.00517", "0.0155"), None),
    ("Aflatoxin B1", "ND", ResultState.ND, None, "ug/kg", ("2.60", "7.88"),
     COMPOUND_IDS["Aflatoxin B1"]),
    ("Ochratoxin A", "ND", ResultState.ND, None, "ug/kg", ("3.87", "11.7"),
     COMPOUND_IDS["Ochratoxin A"]),
    ("Salmonella", "ND", ResultState.ND, None, "CFU/g", (None, None),
     COMPOUND_IDS["Salmonella"]),
    ("STEC", "ND", ResultState.ND, None, "CFU/g", (None, None),
     COMPOUND_IDS["STEC"]),
    ("Aspergillus flavus", "ND", ResultState.ND, None, "CFU/g", (None, None),
     COMPOUND_IDS["Aspergillus flavus"]),
    ("Yeast & Mold", "ND", ResultState.ND, None, "CFU/g", (None, None), None),
    ("Coliforms", "ND", ResultState.ND, None, "CFU/g", (None, None), None),
    ("Aerobic Bacteria", "ND", ResultState.ND, None, "CFU/g", (None, None), None),
    ("Pyrethrins", "ND", ResultState.ND, None, "ug/g", ("0.00431", "0.0300"),
     COMPOUND_IDS["Pyrethrins"]),
    ("Bifenthrin", "ND", ResultState.ND, None, "ug/g", ("0.00500", "0.0300"), None),
    ("Spinosad", "ND", ResultState.ND, None, "ug/g", ("0.00410", "0.0300"), None),
]

# Per-panel instrumentation as printed on the COA (SOP identifiers included).
PANEL_METHOD_NOTES = (
    "Panels as printed: POT-INST-005 Cannabinoids UHPLC-DAD; "
    "Utah RS-PREP-001/RS-INST-003 Residual Solvents GC-MS; "
    "HM-PREP-001/HM-INST-003 Heavy Metals ICP-MS; "
    "MICRO-008/MICRO-PREP-001/MICRO-INST-001 PCR-Microbial; "
    "PEST-GC-PREP-001/PEST-GC-INST-003 Pesticides GC-MS/MS; "
    "PESTMYCO-LC-PREP-001/PESTMYCO-LC-INST-004 Mycotoxins/Pesticides LC-MS/MS; "
    "MICR-005/MICR-006 Petrifilm Yeast&Mold; MICR-002 Petrifilm Coliforms/Aerobic"
)

REPORT_METHOD = MethodMetadata(
    instrument_technique=InstrumentTechnique.UHPLC_DAD,
    moisture_method=MoistureMethod.LOSS_ON_DRYING,  # "Moisture: Mass by Drying"
    extraction_method=PANEL_METHOD_NOTES,
)

PANEL_METHODS = {
    "Ethanol": MethodMetadata(
        instrument_technique=InstrumentTechnique.GC_MS,
        extraction_method="Utah RS-PREP-001 / RS-INST-003 (GC-MS)",
    ),
    "Lead": MethodMetadata(
        instrument_technique=InstrumentTechnique.ICP_MS,
        extraction_method="HM-PREP-001 / HM-INST-003 (ICP-MS)",
    ),
    "Salmonella": MethodMetadata(
        instrument_technique=InstrumentTechnique.PCR,
        extraction_method="MICRO-008 / MICRO-PREP-001 / MICRO-INST-001 (PCR)",
    ),
}


def measurements() -> list[AnalyteMeasurement]:
    out: list[AnalyteMeasurement] = []
    for name, printed, state, amount, limits, formula in CANNABINOID_PANEL:
        lod = float(limits[0]) if limits and limits[0] is not None else None
        loq = float(limits[1]) if limits and limits[1] is not None else None
        out.append(AnalyteMeasurement(
            compound_id=COMPOUND_IDS.get(name),
            compound_name=name,
            reported_value=printed,
            reported_unit="mg/pkg",
            state=state,
            value=amount,
            unit="other",  # per-package quantity; not a canonical concentration
            lod=lod,
            loq=loq,
            quantitation_note=(
                "amounts printed in mg per 35 g package; LOD/LOQ as printed in "
                "mg/ml; printed % column is w/w (11.0 mg / 35 g = 0.0314 % w/w)"
                if state is ResultState.NUMERIC else
                "LOD/LOQ as printed in mg/ml; reported amount unit is mg/pkg"
            ),
            calculation_formula=formula,
        ))
    for name, printed, state, value, unit, limits, compound_id in SAFETY_ROWS:
        lod = float(limits[0]) if limits and limits[0] is not None else None
        loq = float(limits[1]) if limits and limits[1] is not None else None
        normalized_unit = "other" if unit == "ug/kg" else unit
        out.append(AnalyteMeasurement(
            compound_id=compound_id,
            compound_name=name,
            reported_value=printed,
            reported_unit="µg/g" if unit == "ug/g" else
                          ("µg/kg" if unit == "ug/kg" else unit),
            state=state,
            value=value,
            unit=normalized_unit,
            lod=lod,
            loq=loq,
            method=PANEL_METHODS.get(name),
            quantitation_note=(
                "printed unit µg/g == ug/g (unicode normalization only)"
                if unit == "ug/g" and state is ResultState.NUMERIC
                else
                "printed unit µg/kg; not a canonical concentration unit"
                if unit == "ug/kg" else None
            ),
        ))
    return out


def record() -> CoaRecord:
    report = Report(
        report_id="lab-results/TLAB-0002",
        source_reference=(
            "TagLeaf LIMS COA verification 6iE0zRnhl3; "
            "InfiniteCAL sample ICC-250410-37-002"
        ),
        report_date="2025-07-11",
        sample_date="2025-04-10",
        sample_id=UPSTREAM_RECORD_ID,
        laboratory=Laboratory(
            name="Infinite Chemical Analysis Labs",
            lab_id="testing-laboratories/TSTL-0006",
            license_number="C8-0000047-LIC",
            jurisdiction="CA",
        ),
        jurisdiction="CA",
        test_panels=(
            "cannabinoid", "residual-solvent", "heavy-metal",
            "pesticide", "mycotoxin", "microbial",
        ),
        provenance=SourceProvenance(
            source_url=SOURCE_URL,
            document_hash=DOCUMENT_HASH,
            retrieval_date=RETRIEVAL_DATE,
            upstream_record_id=UPSTREAM_RECORD_ID,
            parser_version=PARSER_VERSION,
            retrieval_note=(
                f"official verification endpoint HTTP 200 at retrieval; "
                f"archived PDF: {SOURCE_PDF}"
            ),
        ),
        method=REPORT_METHOD,
    )
    batch = Batch(
        batch_id="250410-37-002",
        lot_number="ICC-250410",
        product_id="products/TPRD-0002",
        sample_type="edible",
        matrix_detail="Edible Liquid (THC beverage), 35 g package",
        basis=ReportingBasis.UNKNOWN,
        decarb_convention="native",  # acids and neutrals printed separately
        record_kind=RecordKind.VERIFIED,
        jurisdiction="CA",
    )
    return CoaRecord(report=report, batch=batch, measurements=tuple(measurements()))


def render_page(rec: CoaRecord) -> str:
    """Render the lab-results content page from the model record."""
    m = rec.measurements
    links = {
        "cannabinoids/TCBN-0002": "cannabinoids/cbd.md",
        "cannabinoids/TCBN-0003": "cannabinoids/cbda.md",
        "cannabinoids/TCBN-0004": "cannabinoids/cbdv.md",
        "cannabinoids/TCBN-0005": "cannabinoids/cbg.md",
        "cannabinoids/TCBN-0006": "cannabinoids/cbga.md",
        "cannabinoids/TCBN-0007": "cannabinoids/thca.md",
        "cannabinoids/TCBN-0008": "cannabinoids/thcv.md",
        "contaminants/TCNT-0001": "contaminants/TCNT-0001.md",
        "contaminants/TCNT-0002": "contaminants/TCNT-0002.md",
        "contaminants/TCNT-0003": "contaminants/TCNT-0003.md",
        "contaminants/TCNT-0005": "contaminants/TCNT-0005.md",
        "contaminants/TCNT-0006": "contaminants/TCNT-0006.md",
        "contaminants/TCNT-0007": "contaminants/TCNT-0007.md",
    }
    def compound_link(mm: AnalyteMeasurement) -> str:
        if mm.compound_id in links:
            rel = "../" + links[mm.compound_id]
            return f"[{mm.compound_name}]({rel})"
        return mm.compound_name

    def limits_text(mm: AnalyteMeasurement) -> str:
        lod_s = "—"
        loq_s = "—"
        for row in CANNABINOID_PANEL + SAFETY_ROWS:
            if row[0] == mm.compound_name and row[-2] and row[-2][0] is not None:
                lod_s, loq_s = row[-2]
                break
        return f"{lod_s} / {loq_s}"

    def row_text(mm: AnalyteMeasurement) -> str:
        if mm.state is ResultState.ND:
            result = "ND"
            status = "Not Detected"
        elif mm.state is ResultState.BELOW_LOQ:
            result = "&lt;LOQ"
            status = "Below LOQ"
        else:
            result = mm.reported_value
            status = "Quantified"
        return (
            f"| {compound_link(mm)} | {result} | {mm.reported_unit} | "
            f"{status} | {limits_text(mm)} |"
        )

    calculated = {"Total THC", "Total CBD", "Total Cannabinoids"}
    safety_names = {row[0] for row in SAFETY_ROWS}
    cann_rows = "\n".join(
        row_text(mm) for mm in m
        if mm.compound_name not in calculated and mm.compound_name not in safety_names
    )
    safety_rows = "\n".join(
        row_text(mm) for mm in m if mm.compound_name in safety_names
    )

    calc_rows = "\n".join(
        f"| {compound_link(mm)} | {mm.reported_value} | {mm.reported_unit} | "
        f"`{mm.calculation_formula}` |"
        for mm in m
        if mm.calculation_formula is not None
    )

    return f"""---
id: lab-results/TLAB-0002
title: "Verified COA: Dragonberry 750ml (10mg) — Batch 250410-37-002 (InfiniteCAL)"
parent: lab-results
status: published
tags: ["lab-results", "coa", "verified", "california", "edible"]
relations: [relates_to=products/TPRD-0002, relates_to=testing-laboratories/TSTL-0006, relates_to=organizations/TORG-0006, relates_to=jurisdictions/TJUR-0001, relates_to=cannabinoids/TCBN-0002, relates_to=cannabinoids/TCBN-0003, relates_to=cannabinoids/TCBN-0004, relates_to=cannabinoids/TCBN-0005, relates_to=cannabinoids/TCBN-0006, relates_to=cannabinoids/TCBN-0007, relates_to=cannabinoids/TCBN-0008, relates_to=contaminants/TCNT-0002, relates_to=contaminants/TCNT-0003, relates_to=contaminants/TCNT-0005, relates_to=contaminants/TCNT-0006, relates_to=contaminants/TCNT-0007]
summary: Verified certificate of analysis (Infinite Chemical Analysis Labs, CA) for Powered By Plants Dragonberry 750ml (10mg) edible liquid, batch 250410-37-002, with provenance.
---

# Verified COA: Dragonberry 750ml (10mg) — Batch 250410-37-002

This is the archive's **first verified COA record**. It was transcribed from a
real published laboratory report and is traceable to its source document
(see [Provenance & Sources](#provenance-sources) below).

## Report Identity

| Field | Value |
| --- | --- |
| Report ID | `lab-results/TLAB-0002` |
| Testing Laboratory | [Infinite Chemical Analysis Labs](../testing-laboratories/TSTL-0006.md) (`C8-0000047-LIC`, San Diego, CA) |
| Client / Producer | Powered By Plants *(named on the COA; no archive organization record yet)* |
| Product | [Dragonberry 750ml (10mg)](../products/TPRD-0002.md) — Edible Liquid |
| Batch / Lot / Sample | 250410-37-002 / ICC-250410 / ICC-250410-37-002 |
| Report date | 2025-07-11 |
| Sample collected | 2025-04-10 |
| Jurisdiction | CA (lab state); compliance cited: UT Hemp, CA Cannabis/Hemp, CO Hemp |
| Matrix | Edible Liquid (35 g package, density 1.03634 g/ml) |
| Batch Result | **Pass** (Potency, Solvents, Metals, Pesticides, Mycotoxins, Microbial, Foreign) |
| Panels | Cannabinoid · Residual Solvent · Heavy Metal · Pesticide · Mycotoxin · Microbial |

## Cannabinoid Panel (as printed)

| Analyte | Amount (mg/pkg) | Unit | Status | LOD/LOQ (mg/ml) |
| --- | --- | --- | --- | --- |
{cann_rows}

### Calculated (report-derived) totals

| Analyte | Amount (mg/pkg) | Unit | Formula (as printed) |
| --- | --- | --- | --- |
{calc_rows}

> [!NOTE]
> **Measured vs calculated.** CBD, Δ8-THC, and Δ9-THC are individually measured
> rows; THCA and the other acids were printed as ND. Total THC / Total CBD /
> Total Cannabinoids are **calculated** rows whose formulas are retained
> verbatim above. Acid and neutral cannabinoids are never collapsed.

## Safety Panel Summary

| Analyte | Result | Unit | Status | LOD/LOQ |
| --- | --- | --- | --- | --- |
{safety_rows}

> [!NOTE]
> **Full panel in the source document.** The printed COA additionally lists
> ~41 more residual-solvent analytes (all ND except Ethanol), 3 more mycotoxin
> rows (Aflatoxin B2/G1/G2 and Aflatoxins total, all ND), Salmonella/STEC PCR
> duplicates, Aspergillus fumigatus/niger/terreus, and ~85 more pesticide
> analytes (all ND) — every panel passed. Those rows are authoritative in the
> linked, hashed source document and are not duplicated here.

## Qualifier Semantics

| Printed | Model state | Meaning |
| --- | --- | --- |
| `ND` | `nd` | Tested, not detected — never zero |
| `11.0`, `0.219`, `10200` | `numeric` | Quantified values |
| `< LOQ` (Lead) | `below_loq` | Below quantitation limit; `loq` 0.00400 µg/g — never zero |
| *(absent terpene panel)* | `not_tested` | This matrix was not terpene-tested; absence of a result is not evidence of absence |

The per-package `mg/pkg` unit is **not** a concentration unit, so the model
records it verbatim using its explicit `other` unit escape hatch rather than
pretending it is a canonical concentration; the printed `%` column is w/w
per 35 g package (11.0 mg / 35 g = 0.314 mg/g = 0.0314 % w/w).

## Provenance & Sources

| Field | Value |
| --- | --- |
| Official verification | [TagLeaf LIMS COA verification](https://lims.tagleaf.com/coa_/6iE0zRnhl3) (HTTP 200 at retrieval) |
| Source document (PDF) | [{SOURCE_PDF}]({SOURCE_PDF}) |
| Document hash (sha256) | `{DOCUMENT_HASH}` |
| Retrieval date | {RETRIEVAL_DATE} |
| Upstream record id | `ICC-250410-37-002` |
| Parser / import version | `{PARSER_VERSION}` |

Every value on this page traces to the source above: AnalyteResult → LabReport
→ source document / official endpoint → retrieval metadata
(`docs/coa-data-model.md` §8).

## Related Graph Connections

- [Dragonberry 750ml (10mg) product record](../products/TPRD-0002.md)
- [Infinite Chemical Analysis Labs](../testing-laboratories/TSTL-0006.md) · [Organization record](../organizations/TORG-0006.md)
- Compound records referenced: [CBD](../cannabinoids/cbd.md), [THCA](../cannabinoids/thca.md), [THCV](../cannabinoids/thcv.md), [Lead](../contaminants/TCNT-0007.md), [Ochratoxin A](../contaminants/TCNT-0003.md), [Salmonella](../contaminants/TCNT-0005.md)
"""


def snapshot_pdf() -> Path:
    """Download the source PDF into var/ and verify its sha256 (Path A).

    Idempotent: if the file already exists with the recorded hash it is left
    untouched; a hash mismatch raises so an immutable snapshot is never
    silently overwritten.
    """
    if SNAPSHOT_PATH.exists():
        existing = hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest()
        if existing == DOCUMENT_HASH:
            print(f"snapshot already present and verified: {SNAPSHOT_PATH}")
            return SNAPSHOT_PATH
        raise SystemExit(
            f"snapshot exists with hash {existing}, expected {DOCUMENT_HASH}; "
            "refusing to overwrite an immutable snapshot"
        )
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        SOURCE_PDF, headers={"User-Agent": "Mozilla/5.0 (coa-verify-example/1.0)"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != DOCUMENT_HASH:
        raise SystemExit(
            f"downloaded bytes hash {digest}, expected {DOCUMENT_HASH}; "
            "refusing to write an unverified snapshot"
        )
    SNAPSHOT_PATH.write_bytes(data)
    print(f"snapshot verified and written: {SNAPSHOT_PATH}")
    return SNAPSHOT_PATH


def render_dataset_page(rec: CoaRecord) -> str:
    """Render the datasets/TDTS-0022 record for the raw snapshot."""
    snapshot_rel = SNAPSHOT_PATH.relative_to(ROOT).as_posix()
    return f"""---
id: datasets/TDTS-0022
title: "COA Snapshot — Dragonberry 750ml (10mg) Batch 250410-37-002 (2026-08-09)"
parent: datasets
status: published
tags: ["dataset", "coa", "lab-results", "california"]
relations: [relates_to=lab-results/TLAB-0002, relates_to=products/TPRD-0002, relates_to=testing-laboratories/TSTL-0006, relates_to=jurisdictions/TJUR-0001]
summary: "Dated raw snapshot of the verified InfiniteCAL COA for Powered By Plants Dragonberry 750ml (10mg) batch 250410-37-002, checksummed in the ingest working area."
---

# COA Snapshot Dataset — Dragonberry 750ml (10mg) Batch 250410-37-002

Raw snapshot of the laboratory report transcribed by
`lab-results/TLAB-0002`, captured under Path A of `docs/graph/coa-migration.md`:
immutable PDF archived in the git-ignored ingest working area, checksummed,
and registered here.

## Dataset Identity

| Field | Value |
| --- | --- |
| Dataset | `{DATASET_SLUG}` |
| Schema version | 1.0 |
| Generator | scripts/coa_verify_example.py (parser `{PARSER_VERSION}`) |
| Retrieval timestamp | {RETRIEVAL_TIMESTAMP} |
| Artifacts | 1 PDF (4 pages, 78 KB) |
| Raw checksums | `{UPSTREAM_RECORD_ID}.pdf` `{DOCUMENT_HASH}` |
| Derived record | [lab-results/TLAB-0002](../lab-results/TLAB-0002.md) |
| Product | [products/TPRD-0002](../products/TPRD-0002.md) |

## Retrieval Parameters

- Official verification endpoint: `{SOURCE_URL}` (HTTP 200 at retrieval)
- Source document (public copy): `{SOURCE_PDF}`
- Archive (working area, git-ignored): `{snapshot_rel}`
- Batch / Lot / Sample: 250410-37-002 / ICC-250410 / {UPSTREAM_RECORD_ID}
- Laboratory: Infinite Chemical Analysis Labs (CA), license C8-0000047-LIC
- Report produced: 2025-07-11 · sample collected 2025-04-10

## Source & Provenance

- **Official source**: {SOURCE_URL}
- **Jurisdiction**: California, United States
- **Retrieval date**: {RETRIEVAL_TIMESTAMP}
- **Source-data caveat**: Laboratory reports are self-published by the
  laboratory/brand; the archive verifies retrievability and hashes the
  artifact but cannot certify the underlying measurements.
- **Record status**: synced
- **Generator**: scripts/coa_verify_example.py v1.0 (schema 1.0)
- **Stable entity ID**: datasets/TDTS-0022
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="write the verified page and durable COA registry record")
    parser.add_argument("--snapshot", action="store_true",
                        help="Path A: checksum the PDF into var/ and write "
                             "content/datasets/TDTS-0022.md")
    args = parser.parse_args()

    rec = record()
    print("=== Provenance ===")
    print(f"  source_url:        {rec.report.provenance.source_url}")
    print(f"  document_hash:     {rec.report.provenance.document_hash}")
    print(f"  retrieval_date:    {rec.report.provenance.retrieval_date}")
    print(f"  upstream_record_id:{rec.report.provenance.upstream_record_id}")
    print(f"  parser_version:    {rec.report.provenance.parser_version}")
    print()
    print("=== Record identity ===")
    print(f"  report_id: {rec.report.report_id}  (revision {rec.report.revision})")
    print(f"  batch_id:  {rec.batch.batch_id}  lot {rec.batch.lot_number}")
    print(f"  matrix:    {rec.batch.matrix_detail}  sample_type={rec.batch.sample_type}")
    print(f"  lab:       {rec.report.laboratory.name} ({rec.report.laboratory.lab_id})")
    print(f"  product:   {rec.batch.product_id}  record_kind={rec.batch.record_kind.value}")
    print(f"  measurements: {len(rec.measurements)}")
    print()
    print("=== Result-state census ===")
    for state, count in censorship_summary(rec).items():
        if count:
            print(f"  {state}: {count}")
    print()
    print("=== Hard validation (coa_problems) ===")
    problems = coa_problems(rec)
    print("  [] — verified record passes" if not problems else problems)
    print()
    print("=== Soft validation (coa_warnings) ===")
    warnings = coa_warnings(rec)
    for w in warnings:
        print(f"  - {w}")
    print()
    print("=== JSON (abridged: 3 of the measurements) ===")
    payload = rec.to_dict()
    payload["measurements"] = [payload["measurements"][i] for i in (0, 1, 10)]
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.snapshot:
        snapshot_pdf()
        dataset_target = ROOT / "content" / "datasets" / "TDTS-0022.md"
        dataset_target.write_text(render_dataset_page(rec), encoding="utf-8")
        print(f"wrote {dataset_target.relative_to(ROOT)}")

    if args.write:
        target = ROOT / "content" / "lab-results" / "TLAB-0002.md"
        target.write_text(render_page(rec), encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")
        registry = ROOT / "metadata" / "coa-records.jsonl"
        existing: list[str] = []
        if registry.exists():
            existing = [line for line in registry.read_text(encoding="utf-8").splitlines() if line.strip()]
        existing = [
            line for line in existing
            if json.loads(line).get("report", {}).get("report_id") != rec.report.report_id
        ]
        existing.append(json.dumps(rec.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        existing.sort(key=lambda line: json.loads(line).get("report", {}).get("report_id", ""))
        registry.write_text("\n".join(existing) + "\n", encoding="utf-8")
        print(f"wrote {registry.relative_to(ROOT)} ({len(existing)} record(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
