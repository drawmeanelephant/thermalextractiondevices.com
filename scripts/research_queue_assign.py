#!/usr/bin/env python3
"""Agent 8 — Research Corpus Ingestion Queue: deterministic field assignment.

Reads research/_index/manifest.jsonl (read-only), computes subject-level
ingestion metadata from the corpus ledger analysis in research_queue_analysis.py
plus the site-side verification record (reports/source-verification-wave-01.md),
and writes the enriched manifest + ingestion-queue.md.

Outputs (all under research/_index/):
  manifest.jsonl          — enriched with verification_status,
                             primary_source_coverage, ingestion_status,
                             target_collections, priority, queue_notes
  ingestion-queue.md      — human-readable actionable work queue
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

import research_queue_analysis as rqa

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research")
MANIFEST = os.path.join(ROOT, "_index", "manifest.jsonl")

# ---------------------------------------------------------------------------
# Subject-level knowledge (from reports/source-verification-wave-01.md and the
# corpus index files), reviewed and frozen by the agent.
# ---------------------------------------------------------------------------

# Subjects whose published site content was checked against primary sources in
# Agent 3's source-verification wave (strengthened or retained rows).
PARTIALLY_VERIFIED = {
    "Arizer (Arizer Tech Inc.)",
    "DynaVap, LLC",
    "Storz & Bickel GmbH & Co. KG",
    "Terpinolene",
    "α-Humulene",
    "Ocimene (α/β isomers)",
    "Eucalyptol (1,8-Cineole)",
    "Linalool",
    "Nerolidol",
    "D-Limonene",
    "α-Pinene",
    "β-Pinene",
    "α-Bisabolol",
    "β-Caryophyllene",
    "β-Myrcene",
}

# Subjects with published site pages traceable to this corpus.
INCORPORATED = {
    "Arizer (Arizer Tech Inc.)",
    "DynaVap, LLC",
    "Storz & Bickel GmbH & Co. KG",
    "α-Bisabolol", "α-Humulene", "α-Pinene", "β-Caryophyllene", "β-Myrcene",
    "β-Pinene", "D-Limonene", "Eucalyptol (1,8-Cineole)", "Linalool",
    "Nerolidol", "Ocimene (α/β isomers)", "Terpinolene", "Valencene",
    "Cannabis Cultivar Names Versus Measured Chemotypes",
    "Evidence Architecture for Cannabis Compounds, Profiles, and Reported Effects",
}

# Corpus-ledger citation errors and unresolved claims discovered in wave 01.
LEDGER_ISSUES = {
    "Terpinolene": "corpus ledger citation error (Aydin et al. 2013, not 'Gasic et al.') - see reports/source-verification-wave-01.md",
    "Linalool": "corpus ledger citation error (Linck et al. 2010, not 'Kashiwadani et al.'); CNS-depressant claim unresolved",
    "D-Limonene": "corpus ledger citation error (Sanshita/Devi Int J Nanomedicine 2025, not 'Devi N Pharmaceutics')",
    "Ocimene (α/β isomers)": "antifungal claim unresolved (no primary source located in wave 01)",
    "β-Pinene": "cellular cytotoxic claim unresolved (no primary source located in wave 01)",
}

# Identity ambiguity requiring human decision before collapse/ingestion.
IDENTITY_REVIEW = {
    "Smiss Technology Co., Ltd.": "Flowermate parentage claimed but unverified; do not collapse without primary-source confirmation",
    "TopGreen Technology (XMAX)": "XMAX vs XVape brand split; keep distinct until primary-source confirmation",
    "XVape (TopGreen Technology)": "XMAX vs XVape brand split; keep distinct until primary-source confirmation",
}

MULTI_RUN = rqa.MULTI_RUN_SUBJECTS

# Coverage override: Cannabis Hardware's ledger includes official product pages,
# Nasdaq press release, and Montana DoR source; classifier under-credited it.
COVERAGE_OVERRIDE = {"Cannabis Hardware, LLC": "moderate"}

# target_collections by subject_subtype
TARGET_COLLECTIONS = {
    "manufacturers": ["manufacturers", "devices"],
    "terpenes": ["terpenes", "botanicals"],
    "cannabinoids": ["botanicals", "reference"],
    "other": ["botanicals", "reference"],
    "cultivar-identity": ["cultivars", "reference"],
    "chemotype-analysis": ["reference", "cultivars"],
    "batch-variability": ["cultivars", "lab-results", "datasets"],
    "terpene-cooccurrence": ["terpenes", "botanicals", "reference"],
    "effects-evidence": ["reference", "guides"],
    "laboratory-comparability": ["testing-laboratories", "lab-results", "datasets"],
    "post-harvest": ["reference", "botanicals"],
    "thermal-aerosol": ["reference", "guides", "safety"],
    "geographic-variation": ["jurisdictions", "datasets", "reference"],
    "manufacturer-universe": ["manufacturers", "reference", "devices"],
    "research-prompts": ["reference", "guides"],
    "united-states": ["jurisdictions", "datasets", "law-and-use"],
}

RELEVANCE = {
    "devices": "high",
    "compounds": "high",        # terpenes/cannabinoids/aroma all feed the site's compound collections
    "cannabis": "medium",
    "industry": "medium",
    "jurisdictions": "medium",
}


def subject_aggregates():
    """Recompute subject-level aggregates using the reviewed classifier."""
    with open(MANIFEST, encoding="utf-8") as fh:
        recs = [json.loads(l) for l in fh if l.strip()]
    subjects = defaultdict(list)
    for r in recs:
        subjects[r["canonical_subject"]].append(r)

    out = {}
    for subject, rs in subjects.items():
        roles = Counter(r["research_role"] for r in rs)
        subtype = Counter(r["subject_subtype"] for r in rs).most_common(1)[0][0]
        stype = Counter(r["subject_type"] for r in rs).most_common(1)[0][0]
        scan_files = []
        for r in rs:
            if r["research_role"] in ("artifact", "export"):
                p = os.path.join(ROOT, r["normalized_path"].replace("research/", "", 1))
                if os.path.exists(p):
                    scan_files.append(p)
        agg, markers, brand = Counter(), Counter(), set()
        for p in scan_files:
            c, m, b = rqa.scan_ledger(p, subject)
            agg.update(c)
            markers.update(m)
            brand |= b
        auth = agg.get("authoritative", 0)
        weak = agg.get("weak", 0)
        neutral = agg.get("neutral", 0)
        total = auth + weak + neutral
        official_docs = markers.get("official", 0) + markers.get("manual", 0)
        gov_sci = (markers.get("govreg", 0) + markers.get("sec", 0)
                   + markers.get("sci", 0) + markers.get("patent", 0))
        brand_official = len(brand)
        ratio = auth / total if total else 0
        coverage = "weak"
        if total or brand_official:
            if (auth >= 3 and ratio >= 0.5) or (brand_official + official_docs >= 3 and (gov_sci >= 1 or auth >= 2)) or (brand_official >= 2 and auth >= 1) or (stype == "compounds" and auth >= 10 and ratio >= 0.4):
                coverage = "strong"
            elif (auth >= 2 and ratio >= 0.3) or (brand_official >= 2 and (auth >= 1 or official_docs >= 1)) or (brand_official + markers.get("manual", 0) >= 2) or (gov_sci >= 3) or (auth >= 4):
                coverage = "moderate"
        coverage = COVERAGE_OVERRIDE.get(subject, coverage)
        out[subject] = {
            "stype": stype, "subtype": subtype,
            "roles": dict(roles),
            "has_artifact": roles.get("artifact", 0) > 0,
            "has_export": roles.get("export", 0) > 0,
            "coverage": coverage,
            "multi": subject in MULTI_RUN,
            "idrisk": subject in IDENTITY_REVIEW,
            "ledger_issue": LEDGER_ISSUES.get(subject),
            "identity_review": IDENTITY_REVIEW.get(subject),
            "partially_verified": subject in PARTIALLY_VERIFIED,
            "incorporated": subject in INCORPORATED,
            "relevance": RELEVANCE.get(stype, "medium"),
        }
    return out


def assign_priority(a):
    """Rubric from the task brief:
    P1 artifact+source, strong coverage, clear identity, high relevance.
    P2 complete research, verification gaps, multiple runs to reconcile.
    P3 export only, weak sources, identity ambiguity, incomplete research.
    """
    if a["idrisk"]:
        return 3
    if a["roles"].get("redundant", 0) and not (a["has_artifact"] or a["has_export"]):
        return 3
    if not a["has_artifact"] and not a["has_export"]:
        return 3
    if a["has_artifact"] and a["has_export"]:
        if a["multi"] or a["ledger_issue"]:
            return 2
        if a["coverage"] == "strong" and a["relevance"] == "high":
            return 1
        if a["coverage"] in ("strong", "moderate"):
            return 2
        return 3
    # export-only or artifact-only
    if a["has_artifact"]:            # artifact-only: incomplete research (no source)
        return 3
    # export-only
    if a["coverage"] == "strong":
        return 2
    if a["coverage"] == "moderate" and a["multi"]:
        return 2
    if a["coverage"] == "moderate" and a["relevance"] == "high":
        return 2
    return 3


def assign_ingestion_status(a):
    if a["ledger_issue"] or a["identity_review"]:
        return "needs-review"
    if a["incorporated"]:
        return "incorporated"
    if assign_priority(a) <= 2:
        return "queued"
    return "not-started"


def assign_verification(a):
    return "partially-verified" if a["partially_verified"] else "unverified"


def queue_note(a, role):
    notes = []
    if a["ledger_issue"]:
        notes.append("LEDGER ISSUE: " + a["ledger_issue"])
    if a["identity_review"]:
        notes.append("IDENTITY REVIEW: " + a["identity_review"])
    if a["multi"]:
        notes.append("Multiple independent research runs; reconcile before ingestion")
    if a["incorporated"]:
        notes.append("Published site content exists; see content/")
    if role == "redundant":
        notes.append("Archived duplicate; excluded from ingestion queues (see duplicate-groups.md)")
    return "; ".join(notes)


def main():
    subs = subject_aggregates()
    with open(MANIFEST, encoding="utf-8") as fh:
        recs = [json.loads(l) for l in fh if l.strip()]

    manifest_out = []
    for r in recs:
        subject = r["canonical_subject"]
        a = subs[subject]
        fields = {
            "verification_status": assign_verification(a),
            "primary_source_coverage": a["coverage"],
            "ingestion_status": assign_ingestion_status(a),
            "target_collections": TARGET_COLLECTIONS.get(a["subtype"], ["reference"]),
            "priority": assign_priority(a),
        }
        r.pop("queue_notes", None)  # idempotent: never inherit stale notes
        note = queue_note(a, r.get("research_role"))
        if note:
            fields["queue_notes"] = note
        manifest_out.append({**r, **fields})

    # sanity: all records got every field
    for f in ("verification_status", "primary_source_coverage", "ingestion_status",
              "target_collections", "priority"):
        assert all(f in r for r in manifest_out), f"missing field {f}"

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        for r in manifest_out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # summary for review
    print("priority:", Counter(r["priority"] for r in manifest_out))
    print("verification:", Counter(r["verification_status"] for r in manifest_out))
    print("coverage:", Counter(r["primary_source_coverage"] for r in manifest_out))
    print("ingestion:", Counter(r["ingestion_status"] for r in manifest_out))
    print("subjects:", len(subs))
    for p in (1, 2, 3):
        names = sorted(s for s, a in subs.items() if assign_priority(a) == p)
        print(f"\nP{p} ({len(names)}):")
        for n in names:
            a = subs[n]
            print(f"  {n}  [{a['coverage']} | {'a+e' if a['has_artifact'] and a['has_export'] else 'export' if a['has_export'] else 'artifact'}"
                  f"{' | multi' if a['multi'] else ''}{' | idrisk' if a['idrisk'] else ''}{' | inc' if a['incorporated'] else ''}]")


if __name__ == "__main__":
    main()
