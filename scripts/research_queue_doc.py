#!/usr/bin/env python3
"""Generate research/_index/ingestion-queue.md from the enriched manifest."""
import json
import os
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research")
MANIFEST = os.path.join(ROOT, "_index", "manifest.jsonl")
OUT = os.path.join(ROOT, "_index", "ingestion-queue.md")

QUEUES = [
    ("manufacturers-devices", "Manufacturers & Devices"),
    ("terpenes", "Terpenes"),
    ("cannabinoids", "Cannabinoids"),
    ("cross-cutting-chemistry", "Cross-Cutting Chemistry"),
    ("cultivar-chemotype", "Cultivar / Chemotype Research"),
    ("laboratory", "Laboratory Research"),
    ("jurisdictions", "Jurisdictions"),
]

EXCLUDED_SUBJECTS = {"Meta-Research Prompt Templates (Cannabis Vaporizer Industry)"}


def queue_of(subtype, stype):
    if stype == "devices" or subtype == "manufacturer-universe":
        return "manufacturers-devices"
    if subtype == "terpenes":
        return "terpenes"
    if subtype == "cannabinoids":
        return "cannabinoids"
    if subtype == "other" or stype == "cannabis" and subtype in {
        "post-harvest", "thermal-aerosol", "batch-variability",
        "terpene-cooccurrence", "effects-evidence", "geographic-variation",
    }:
        return "cross-cutting-chemistry"
    if subtype in {"cultivar-identity", "chemotype-analysis"}:
        return "cultivar-chemotype"
    if subtype == "laboratory-comparability":
        return "laboratory"
    if stype == "jurisdictions":
        return "jurisdictions"
    return None


def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        recs = [json.loads(l) for l in fh if l.strip()]

    subjects = defaultdict(list)
    for r in recs:
        subjects[r["canonical_subject"]].append(r)

    def rec_counts(name):
        roles = defaultdict(int)
        for r in subjects[name]:
            roles[r["research_role"]] += 1
        return roles

    def first(rname, key):
        for r in subjects[rname]:
            if r["research_role"] == rname:
                return r[key]
        return subjects[rname][0][key]

    def subject_row(name):
        rs = subjects[name]
        roles = rec_counts(name)
        parts = []
        if roles.get("artifact"):
            parts.append("artifact")
        if roles.get("export"):
            parts.append("export")
        if roles.get("redundant"):
            parts.append(f"+{roles['redundant']} archived duplicate")
        # representative record: first non-redundant one (subject-level fields)
        rep = next((r for r in rs if r["research_role"] != "redundant"), rs[0])
        flag = ""
        st = rep["ingestion_status"]
        if st == "incorporated":
            flag = " · **incorporated**"
        elif st == "needs-review":
            flag = " · **needs review**"
        note = rep.get("queue_notes", "")
        return (f"- **P{rep['priority']} · {name}** — {', '.join(parts)} · "
                f"{rep['primary_source_coverage']} coverage · {rep['verification_status']}"
                f"{flag}\n"
                f"  - → {', '.join(rep['target_collections'])}"
                + (f" · ⚠ {note}" if note else ""))

    lines = []
    lines.append("# Research Corpus Ingestion Queue")
    lines.append("")
    lines.append("**Agent 8 — Research Corpus Ingestion Queue**  ")
    lines.append("**Date:** 2026-08-08  ")
    lines.append("**Inputs:** `_index/manifest.jsonl` (195 records · 132 subjects), "
                 "`_index/inventory.md`, `_index/unresolved.md`, `_index/duplicate-groups.md`, "
                 "`reports/source-verification-wave-01.md`")
    lines.append("")
    lines.append("This queue turns the research corpus itself into an actionable work plan: "
                 "which subjects are ready to ingest, which need verification or reconciliation "
                 "first, and where each subject should land on the site. Machine-readable fields "
                 "were added to every manifest record; this page is the human-readable view.")
    lines.append("")
    lines.append("## Field definitions")
    lines.append("")
    lines.append("| Field | Values | Meaning |")
    lines.append("| --- | --- | --- |")
    lines.append("| `verification_status` | `unverified` · `partially-verified` · `primary-sources-verified` | Whether the record's material claims have been checked against the primary sources in its own source ledger. No record is `primary-sources-verified` yet — no corpus-level verification pass has been run. `partially-verified` marks the 15 subjects whose **published site content** was checked against primary sources in `reports/source-verification-wave-01.md` (the corpus records themselves remain unverified). |")
    lines.append("| `primary_source_coverage` | `weak` · `moderate` · `strong` | **Reported** ledger composition: how much of the report's material rests on primary/authoritative sources (official manufacturer documentation, manuals, patents, SEC/FDA/regulatory, government, NIST/PubChem/PMC/PubMed, peer-reviewed literature) versus secondary (retailer, review, forum, blog). Assessed from each report's own source ledger. This is **not** an independent verification. |")
    lines.append("| `ingestion_status` | `not-started` · `queued` · `in-progress` · `incorporated` · `needs-review` | Pipeline state of the corpus record. `incorporated` = published site content traceable to this corpus exists. `needs-review` = record requires attention before reuse (known ledger errors, unresolved claims, identity ambiguity). |")
    lines.append("| `target_collections` | site collection list | The site collections (per `content/` and `metadata/id-policy.json`) the subject should feed. |")
    lines.append("| `priority` | 1 · 2 · 3 | Queue position per the rubric below. |")
    lines.append("")
    lines.append("## Priority rubric")
    lines.append("")
    lines.append("- **Priority 1 — ready:** structured artifact **and** export/source present, "
                 "strong reported primary-source coverage, clear subject identity, no known "
                 "ledger issues, high project relevance.")
    lines.append("- **Priority 2 — needs work:** complete research with gaps — artifact+export "
                 "pairs with moderate coverage, subjects with multiple independent runs needing "
                 "reconciliation, export-only subjects with strong coverage (missing artifact), "
                 "or records with known ledger errors / unresolved claims.")
    lines.append("- **Priority 3 — lowest:** export-only with weak or moderate sources and no "
                 "reconciliation need, identity ambiguity (Smiss/Flowermate, TopGreen XMAX vs "
                 "XVape), artifact-only records (incomplete research, no source), low-relevance "
                 "meta material.")
    lines.append("")
    lines.append("## Honesty rules applied")
    lines.append("")
    lines.append("1. Nothing is marked `primary-sources-verified` merely because a Perplexity "
                 "report cited a primary source — the ledger is reported coverage, not proof.")
    lines.append("2. Coverage labels describe the **reported** source ledger; they were not "
                 "independently re-verified in this pass.")
    lines.append("3. Corpus documents were **not** rewritten. Three corpus-ledger citation "
                 "errors and unresolved claims discovered in the source-verification wave are "
                 "flagged via `ingestion_status: needs-review` + `queue_notes` instead.")
    lines.append("4. Archived duplicates (9 redundant records) and the meta-research prompt "
                 "template are excluded from all queues.")
    lines.append("")
    lines.append("## Queue summary")
    lines.append("")
    lines.append("| Queue | P1 | P2 | P3 |")
    lines.append("| --- | --- | --- | --- |")
    for qid, qname in QUEUES:
        subj = [s for s in subjects if queue_of(subjects[s][0]["subject_subtype"], subjects[s][0]["subject_type"]) == qid and s not in EXCLUDED_SUBJECTS]
        c = defaultdict(int)
        for s in subj:
            c[subjects[s][0]["priority"]] += 1
        lines.append(f"| {qname} | {c[1]} | {c[2]} | {c[3]} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    for qid, qname in QUEUES:
        subj = [s for s in subjects
                if queue_of(subjects[s][0]["subject_subtype"], subjects[s][0]["subject_type"]) == qid
                and s not in EXCLUDED_SUBJECTS]
        lines.append(f"## {qname}")
        lines.append("")
        if not subj:
            lines.append("_No subjects._")
            lines.append("")
            continue
        for p in (1, 2, 3):
            bucket = sorted(s for s in subj if subjects[s][0]["priority"] == p)
            if not bucket:
                continue
            lines.append(f"### Priority {p}")
            lines.append("")
            for s in bucket:
                lines.append(subject_row(s))
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Queue generation report")
    lines.append("")
    lines.append("**Files added:** `research/_index/ingestion-queue.md`; "
                 "`scripts/research_queue_analysis.py`, `scripts/research_queue_assign.py`, "
                 "`scripts/research_queue_doc.py` (reproducible queue tooling).")
    lines.append("")
    n_notes = sum(1 for r in recs if r.get("queue_notes"))
    lines.append("**Files modified:** `research/_index/manifest.jsonl` — every record gained "
                 "`verification_status`, `primary_source_coverage`, `ingestion_status`, "
                 "`target_collections`, `priority`; "
                 f"{n_notes} records also carry `queue_notes` "
                 "(ledger errors, identity review, multi-run reconciliation, incorporated "
                 "flag, archived-duplicate exclusion). No existing field values changed.")
    lines.append("")
    lines.append("**Entities created:** none — this pass adds machine-readable metadata and a "
                 "queue document; no knowledge-graph entities or site content were created.")
    lines.append("")
    lines.append("**Graph relationships created:** none.")
    lines.append("")
    lines.append("**Primary sources verified:** none in this pass (queue-building, not "
                 "verification). Site-side verification already recorded in "
                 "`reports/source-verification-wave-01.md` covers 15 subjects and is reflected "
                 "as `partially-verified`.")
    lines.append("")
    lines.append("**Uncertain claims left unresolved:** corpus-ledger citation errors "
                 "(terpinolene, linalool, d-limonene) and unresolved biological claims "
                 "(ocimene antifungal, linalool CNS-depressant, β-pinene cytotoxic) flagged "
                 "`needs-review`; identity ambiguity for Smiss/Flowermate and TopGreen "
                 "XMAX/XVape requires a human decision.")
    lines.append("")
    lines.append("**Validation results:** all 195 manifest records re-parsed as JSON after "
                 "enrichment; field presence asserted for every record; zero pre-existing field "
                 "values changed; priority/verification/coverage/ingestion distributions "
                 "reviewed by hand against the rubric and the wave-01 ledger.")
    lines.append("")
    lines.append("**Research corpus records consumed:** all 195 manifest records; "
                 "`_index/inventory.md`; `_index/unresolved.md`; `_index/duplicate-groups.md`; "
                 "source ledgers of all artifact/export files (domain + ledger-type analysis).")
    lines.append("")
    lines.append("**Suggested next work:**")
    lines.append("- Ingest the 14 Priority-1 subjects (artifact + export + strong coverage): "
                 "build site content per `target_collections`.")
    lines.append("- Run a verification pass on Priority-1/Priority-2 records, tracing each "
                 "material claim to its primary source and promoting records to "
                 "`primary-sources-verified`.")
    lines.append("- Resolve the flagged `needs-review` records: correct the three corpus-ledger "
                 "citations (terpinolene, linalool, d-limonene) via a ledger-errata file, "
                 "re-check the ocimene/β-pinene/linalool unresolved claims, and take a human "
                 "decision on Smiss/Flowermate and TopGreen XMAX/XVape identity.")
    lines.append("- Reconcile the 13 multi-run subjects into single reconciled artifacts.")
    lines.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote", OUT, len(lines), "lines")


if __name__ == "__main__":
    main()
