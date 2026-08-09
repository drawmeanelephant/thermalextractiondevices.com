# Terpenes & Research Corpus Audit

**Date:** 2026-08-08
**Baseline:** `d3676bc` (github/main, fast-forwarded before this pass)
**Scope:** Research corpus (`research/`), Terpenes collection (`content/terpenes/`, `content/terpenes.md`), and their linkage to the Reference standards (TREF-0001, TREF-0003) and Botanicals collection.

## Summary

The terpene area is in good shape on scientific substance: every boiling point is pressure-referenced (TREF-0001), every biological claim is evidence-classified (TREF-0003), and the corpus-ledger errata from wave 01 (ocimene CAS↔CID, linalool citation, d-limonene citation) are already carried correctly into content. No boiling-point-as-setpoint, no isomer collapse, no anecdote-as-clinical, no Perplexity-cited-as-primary patterns were found.

The audit found two real structural gaps and several consistency issues, all addressed in this pass:

1. **The research corpus files are not in git** — content pages cite `research/compounds/terpenes/<slug>/` dossiers that resolve only in the main worktree (pre-existing finding M-2; now documented on `research/README.md` so downstream agents know to mirror it).
2. **`research/README.md` misdescribed the corpus** as "195 Perplexity exports" — the manifest is 142 exports + 44 artifacts + 9 archived-redundant. Fixed.
3. **The terpenes index page had no catalog** — 19 records existed but the index listed none of them. Rebuilt with a full comparison table.
4. **Identity tables were inconsistent** — 7 of 19 records carried IUPAC/PubChem/molecular-mass data; 12 did not. All 19 now carry the full identity block.

---

## 1. Research corpus findings

### R-1 (pre-existing, now documented): corpus files are untracked

`git ls-files research/` returns only 4 files: `README.md`, `_index/manifest.jsonl`, `_index/ingestion-queue.md`, `_index/verification-ledger.md`. The 195 corpus records (all under `research/devices/`, `research/compounds/`, `research/cannabis/`, `research/jurisdictions/`, `research/_archive/`) live only in the main worktree and are hash-verified against the manifest. This is the previously-flagged M-2 packaging decision; it was not re-litigated here, but the consequence is now documented on `research/README.md` because **published content cites these paths** (e.g., every terpene page's "Research-corpus dossier" footnote under biological activity).

Manifest integrity re-verified against the main worktree mirror (per the wave-01 audit method):

| Check | Result |
| --- | --- |
| Manifest records | 195 — all parse as JSON |
| Roles | export 142 · artifact 44 · redundant 9 |
| Dispositions | keep 186 · archived-redundant 9 |
| Terpene subjects | 19 canonical subjects, all with published `content/terpenes/TTRP-*` records |
| Terpene → content coverage | 19/19 (folders ↔ published pages match 1:1) |

### R-2: `research/README.md` count wording (M-1, fixed)

"Built from 195 Perplexity deep-research Markdown exports" → "195 research records — 142 Perplexity deep-research exports, 44 structured artifacts, and 9 archived-redundant files", plus a packaging note referencing this report and the wave-01 audit.

### R-3: `_index/` completeness

`research/README.md` names `inventory.md`, `duplicate-groups.md`, and `unresolved.md` among `_index/` contents, but only `manifest.jsonl`, `ingestion-queue.md`, and `verification-ledger.md` are tracked (and the two other files are present in the main worktree but untracked, per M-2). Not fixed here — it is part of the same packaging decision. Flagged so the manifest remains the authoritative inventory.

### R-4: content↔corpus claim linkage (clean)

Scanned every `research/compounds/terpenes/…` citation in `content/terpenes/`. All are framed as evidence-class disclosure ("…not translated to cannabis inhalation; not re-verified in this wave"), never as primary evidence — consistent with TREF-0003 and the wave-01 L-1 finding. Identity data newly added to the 12 sparse records was footnoted to **PubChem directly** (verified CIDs), not to the Perplexity dossiers, per the corpus rule *"never treat a Perplexity research report as primary evidence."*

---

## 2. Terpenes section findings

### T-1 (fixed): the index page listed no records

`content/terpenes.md` was prose-only — no catalog, no comparison surface, no cross-links to the standards that govern the records. Rebuilt with:

- A 19-row **catalog table** (compound → CAS → family → boiling point at its reference pressure → data-confidence tier), so the collection is usable as a reference surface, not just a folder of pages.
- A "Reading the table" section: pressure comparability, the TREF-0001 confidence tiers, and the boiling-point ≠ device-setpoint caveat.
- Collection composition stats (13 monoterpene-class, 6 sesquiterpene-class) and links to Botanicals, Cannabinoids, Lab Results, TREF-0001, and TREF-0003.

### T-2 (fixed): identity tables were inconsistent

7 records (α-terpineol, camphene, fenchol, geraniol, guaiol, sabinene, valencene) carried a full identity block (IUPAC name, PubChem CID, molecular mass, stereochemistry); the other 12 (α-bisabolol, α-humulene, α-pinene, β-caryophyllene, β-myrcene, β-pinene, d-limonene, eucalyptol, linalool, nerolidol, ocimene, terpinolene) carried only preferred name / CAS / family / formula. All 19 records now carry the full identity block, with values verified against PubChem (CIDs re-checked: β-caryophyllene 5281515, α-humulene 5281520, β-myrcene 31253, β-pinene 14896, α-pinene 6654, d-limonene 440917, eucalyptol 2758, linalool 6549, nerolidol 5284507, β-ocimene 18756, terpinolene 11463, α-bisabolol 104770). Each record gained one PubChem footnote.

### T-3 (fixed): isomer identity tightened on nerolidol and ocimene

- **Nerolidol**: the record previously declared "Trans-Nerolidol / Cis-Nerolidol" under a single CAS (7212-44-4) without distinguishing the isomers. Now states that CAS 7212-44-4 is the mixed/unspecified material, that trans-nerolidol carries its own CAS (40716-66-3), and that the geometric isomers (each with enantiomeric forms) are distinct identities — consistent with the archive's never-collapse rule.
- **Ocimene**: added the α-/β-ocimene position-isomer distinction (α-ocimene: CAS 6874-44-8) and the (E)/(Z) geometric-isomer split for β-ocimene (e.g., (3E)-trans-β-ocimene: CAS 3779-61-1), addressing the corpus-ledger's CAS↔CID mispair note by citing PubChem CID 18756 (the CID that resolves from CAS 13877-91-3) rather than the corpus's generic-row value.

### T-4 (clean, no change)

- Boiling points: pressure-referenced on every record; reduced-pressure values (α-bisabolol 5 mmHg, guaiol 10 Torr, valencene 11 mmHg) are labeled and never compared against atmospheric values.
- Confidence: every non-NIST value says so ("unconfirmed by NIST", "Antoine estimate", "predicted") rather than implying a primary measurement.
- Biological claims: all classified into human / preclinical / in vitro / traditional, with unresolved claims explicitly labeled (linalool CNS-depressant, ocimene antifungal, β-pinene cytotoxic/antioxidant, α-pinene bronchodilator, β-caryophyllene human evidence).
- Relations: terpene ↔ botanical edges exist for every botanical record (hops ↔ β-myrcene/β-caryophyllene/α-humulene; citrus ↔ d-limonene/fenchol/nerolidol/valencene; lavender ↔ linalool).

---

## 3. Files changed

| File | Change |
| --- | --- |
| `content/terpenes.md` | Rebuilt with 19-record catalog table, reading guidance, composition stats, related-collection links |
| `content/terpenes/alpha-bisabolol.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/alpha-humulene.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/alpha-pinene.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/beta-caryophyllene.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/beta-myrcene.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/beta-pinene.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/d-limonene.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/eucalyptol.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/linalool.md` | Identity block enriched (+PubChem footnote) |
| `content/terpenes/nerolidol.md` | Identity block enriched; trans/cis isomer distinction clarified |
| `content/terpenes/ocimene.md` | Identity block enriched; α/β + E/Z isomer distinction clarified; CID corrected |
| `content/terpenes/terpinolene.md` | Identity block enriched (+PubChem footnote) |
| `research/README.md` | Corpus-count wording corrected (M-1); packaging note added |
| `reports/terpene-research-audit.md` | This report |

No frontmatter schema changes, no new entities, no graph edges added. All 12 enrichment footnotes cite PubChem (primary database), never the untracked corpus.

## 3.5 Follow-up pass: measured cannabis-occurrence context (verified)

Requested follow-up: verify the dossiers' primary-sourced cannabis concentration data and add measured-occurrence context to every terpene record's "Cannabis laboratory results" section.

**Method.** Each dossier's cannabis-occurrence table was mined for the strongest peer-reviewed measured value(s) per terpene. Every primary source planned for citation was verified to exist and match the claim (PubMed/PMC/DOI lookups) before being published. Eleven primary sources were used and verified:

| Source | Verified as | Used for |
| --- | --- | --- |
| Joy et al. 2025, PMC12670203 / PMID 40042239 (validated GC-MS, hemp essential oil, GA) | ✓ | α-bisabolol, α-humulene, α-pinene, β-caryophyllene, β-myrcene, β-pinene, geraniol, ocimene |
| Booth et al. 2017, *PLoS One* 12(3):e0173911, PMID 28355238 (Finola hemp) | ✓ | α-pinene, geraniol |
| Booth et al. 2020, *Plant Physiol* 184(1):130–147, PMID 32591428 (chemotype survey) | ✓ | α-humulene, α-pinene, β-caryophyllene, β-myrcene, camphene, d-limonene, linalool, ocimene |
| Fischedick 2017, *Cannabis Cannabinoid Res* 2(1):34–47, PMID 28861503 (233 samples/30 cultivars, CA) | ✓ | camphene, α-terpineol |
| Ibrahim et al. 2023, *Cannabis Cannabinoid Res* 8(5):899–910, PMID 36322895 (Univ. Mississippi GC-FID) | ✓ | α-terpineol |
| Zager et al. 2019, *Plant Physiol* 180(4):1877–1897 (9-cultivar profiling) | ✓ | nerolidol |
| Chacon et al. 2022, *Biomedicines* 10(12):3142, PMID 36551898 (secondary-terpene review) | ✓ | fenchol, sabinene |
| Mazzara et al. 2022, *Plants* 11(7):891, doi:10.3390/plants11070891 (9 Italian hemp cultivars) | ✓ | terpinolene, valencene |
| Janta et al. 2024, *J Cannabis Res*, doi:10.1186/s42238-024-00252-w, PMID 39639406 (19 Thai cultivars) | ✓ | eucalyptol |
| Anil et al. 2021, *Sci Rep* 11, doi:10.1038/s41598-021-81049-2, PMID 33446817 (high-CBD extract) | ✓ | guaiol |
| Spindle et al. 2024 (already cited as d-limonene [^2]) | ✓ (previously verified) | d-limonene trial material |

**Added to content.** All 19 records now carry a measured-occurrence sentence with a primary-source footnote (e.g., β-myrcene 5.85–8.62 mg/g, Joy 2025; d-limonene 525–2,644 µg/g across five cultivars, Booth 2020; terpinolene up to 30.5 mg/g in one of nine Italian hemp cultivars, Mazzara 2022; nerolidol above LOQ only in Black Lime at <0.1%, Zager 2019). Where peer-reviewed quantitative data are scarce or absent, the record says so explicitly (guaiol, valencene drug-type flower, geraniol below LOQ) rather than importing industry or marketing figures. Units and basis (dry weight vs essential oil vs peak area) are stated. Claims from unidentifiable dossier references (e.g., the unnamed 54-chemotype survey) were not imported.

Footnote integrity re-verified across all 19 records; `ted_ids`, markdown-link audit, and the Cantilever build all pass.

## 4. Suggested next work

1. **Resolve the corpus packaging decision (M-2/R-1)** — decide artifact storage vs. git for the 195 corpus files, or accept the main-worktree-only convention and document it as the source of truth.
2. **Add measured-occurrence context to terpene records** — the dossiers carry primary-sourced cannabis concentration ranges (e.g., α-bisabolol typically <1 mg/g dry flower per Joy et al. 2025) that could strengthen the "Cannabis laboratory results" sections once verified against the primary text.
3. **Consider a `TTRP` record for α-ocimene** — currently only the β-form has a page; the corpus keeps the isomers distinct.
4. **Track the cis-nerolidol CAS number** at next ingestion (the mixed CAS 7212-44-4 covers both isomers in common catalogs; the cis-specific registry entry remains ambiguous across sources).
