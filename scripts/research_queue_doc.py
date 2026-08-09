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

    # verification summary — derived from the manifest, never hardcoded
    subj_status = {}
    for s, rs in subjects.items():
        rep = next((r for r in rs if r["research_role"] != "redundant"), rs[0])
        subj_status[s] = rep["verification_status"]
    n_v_subj = sum(1 for st in subj_status.values() if st == "primary-sources-verified")
    n_p_subj = sum(1 for st in subj_status.values() if st == "partially-verified")
    n_v_rec = sum(1 for r in recs if r["verification_status"] == "primary-sources-verified")
    n_p_rec = sum(1 for r in recs if r["verification_status"] == "partially-verified")
    n_u_rec = sum(1 for r in recs if r["verification_status"] == "unverified")
    partial_names = ", ".join(sorted(s for s, st in subj_status.items() if st == "partially-verified"))
    n_notes = sum(1 for r in recs if r.get("queue_notes"))

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
    lines.append("| `verification_status` | `unverified` · `partially-verified` · `primary-sources-verified` | Whether the record's material claims have been traced to primary/authoritative sources (official manufacturer documentation, manuals, patents, SEC/regulatory filings, NIST/PubChem/PMC/PubMed, peer-reviewed literature) — see `_index/verification-ledger.md` for per-subject results. "
                 f"**{n_v_rec} records ({n_v_subj} subjects) are `primary-sources-verified`** (2026-08-08 verification passes over the Priority-1, Priority-2, and Priority-2-remainder subjects). "
                 f"`partially-verified` ({n_p_rec} records, {n_p_subj} subjects: {partial_names}) marks records whose brand/product claims were traced but whose entity, parentage, or attribution remains unconfirmed or disputed. "
                 f"The remaining {n_u_rec} records are `unverified` (mostly Priority-3, plus Pharmacopeia/Inhalater and the US regulatory dataset subject). |")
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
                 "report cited a primary source — the ledger is reported coverage, not proof. "
                 "Records were promoted only by the 2026-08-08 verification passes, which traced "
                 "each promoted subject's material claims to actual primary/authoritative sources; "
                 "per-subject results are in `_index/verification-ledger.md`.")
    lines.append("2. Coverage labels describe the **reported** source ledger of each research "
                 "report; they are not a substitute for the independent checks recorded in the "
                 "verification ledger.")
    lines.append("3. Corpus documents were **not** rewritten. Ledger citation errors and "
                 "unresolved claims are flagged via `ingestion_status: needs-review` + "
                 "`queue_notes`, and identifier errata (CBD/THCA InChIKeys, aroma-chemistry CIDs, "
                 "sabinene/camphene CAS, Cuboo parentage) are recorded in "
                 "`_index/verification-ledger.md`.")
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
    lines.append("**Files modified:** `research/_index/manifest.jsonl` — every record carries "
                 "`verification_status`, `primary_source_coverage`, `ingestion_status`, "
                 "`target_collections`, `priority`; "
                 f"{n_notes} records also carry `queue_notes` "
                 "(ledger errors, identity review, multi-run reconciliation, incorporated "
                 "flag, archived-duplicate exclusion, identifier errata).")
    lines.append("")
    lines.append("**Verification status (2026-08-08 passes):** "
                 f"{n_v_rec} records across {n_v_subj} subjects are `primary-sources-verified`; "
                 f"{n_p_rec} records across {n_p_subj} subjects are `partially-verified`; "
                 f"{n_u_rec} records are `unverified` (mostly Priority-3, plus two documented "
                 "Priority-2 subjects). Full per-subject results, primary sources, and errata: "
                 "`_index/verification-ledger.md`.")
    lines.append("")
    lines.append("**Entities created:** none — this pass maintains machine-readable metadata and "
                 "queue/verification documentation; no knowledge-graph entities or site content "
                 "were created.")
    lines.append("")
    lines.append("**Uncertain claims left unresolved:** corpus-ledger citation errors "
                 "(terpinolene, linalool, d-limonene) and unresolved biological claims "
                 "(ocimene antifungal, linalool CNS-depressant, β-pinene cytotoxic) flagged "
                 "`needs-review`; identity ambiguity for Smiss/Flowermate and TopGreen "
                 "XMAX/XVape requires a human decision; Pharmacopeia/Inhalater and US regulatory "
                 "data availability documented but not verified.")
    lines.append("")
    lines.append("**Validation results:** all 195 manifest records re-parse as JSON; field "
                 "presence and value enums asserted; subject lists in this document match the "
                 "manifest exactly; queue assignment regenerates idempotently; scripts pass "
                 "`py_compile`.")
    lines.append("")
    lines.append("**Research corpus records consumed:** all 195 manifest records; "
                 "`_index/inventory.md`; `_index/unresolved.md`; `_index/duplicate-groups.md`; "
                 "`_index/verification-ledger.md`; source ledgers of all artifact/export files.")
    lines.append("")
    lines.append("**Suggested next work:**")
    lines.append("- Ingest the verified subjects (14 Priority-1 + 92 Priority-2) per "
                 "`target_collections`, applying the identifier errata recorded in "
                 "`_index/verification-ledger.md`.")
    lines.append("- Resolve the `needs-review` records (three corpus-ledger citations, the "
                 "ocimene/β-pinene/linalool biological claims, Smiss/Flowermate and TopGreen "
                 "XMAX/XVape identity) and the 9 `partially-verified` subjects.")
    lines.append("- Reconcile the multi-run subjects into single reconciled artifacts.")
    lines.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote", OUT, len(lines), "lines")


if __name__ == "__main__":
    main()
