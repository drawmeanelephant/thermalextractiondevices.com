# Cultivar / Chemotype Graph Model — Design Document

**Status:** Established (minimal implementation landed) · **Scope:** connect cultivar labels to measured chemistry without pretending cultivar names are chemical identities.

**Research inputs:** `research/cannabis/cultivar-identity/artifact.md`, `research/cannabis/chemotype-analysis/`, `research/cannabis/batch-variability/`, `research/cannabis/terpene-cooccurrence/artifact.md`, `research/cannabis/laboratory-comparability/`. The `research/cannabis/profile-similarity/` directory referenced in the task brief is not yet present in the corpus; its subject is covered here as a derived-layer design and flagged as a research gap.

**Guiding failure mode this design prevents:** treating "Blue Dream contains X" as a statement about a chemical identity. Cultivar names are *labels*; chemistry is *measured per batch*.

---

## 1. Design principles

1. **Entities are stable; claims are versioned and multi-valued.** Competing lineage claims coexist as claims with graded source authority (ranks A–G from the cultivar-identity research artifact: legal/institutional, primary breeder records, genetic/chemotypic studies, historical publications, structured community databases, forums/oral tradition, retail/menu labels). Never silently drop a lower-rank claim; mark it `superseded_by` or `conflicts_with`.
2. **Chemical identity is never inferred from a label.** A cultivar page is an index; only batch laboratory reports carry measured values.
3. **No fabricated scientific thresholds.** Verbal categories such as *consistent / moderately variable / highly heterogeneous* are explicitly editorial or data-product choices unless validated by literature. The model defines *metrics*; thresholds are decided at query/report time.
4. **Missing is not zero.** Not-tested, ND, <LOD, and <LOQ are distinct states and are never collapsed or imputed silently.
5. **Acid/neutral, isomer, and enantiomer identities are never collapsed** (matches the compound corpus rules, e.g., THCA ≠ THC, α-pinene ≠ β-pinene).
6. **No causal edges from observational data.** Co-occurrence and correlation edges carry evidence classes and are never promoted to causation.

---

## 2. Target graph

```text
cultivar label ──► producer ──► commercial product ──► batch ──► laboratory report ──► measured analytes
     │               │                 │                 │              │
     │               └──── organization ┘                 │              └──► testing laboratory
     │                                                    │
     └──► claimed lineage edges (claim-backed)            └──► product form (flower, extract, …)
```

Derived layer (built only when batch data exists):

```text
batch profiles ──► normalized chemical profiles ──► chemotype / profile clusters ──► cultivar-label distributions
```

The derived layer is **not** built into the site until real batch data exists (see §9). The current archive holds label-level cultivar records and demonstration records only, so this wave lands the model, the normalized representation, and the ingestion primitives — not an analysis engine.

### 2.1 Entity inventory mapped to existing site collections

| Entity | Site collection | Notes |
| --- | --- | --- |
| Cultivar label | `cultivars/TCUL-*` | A *label*, not a chemical identity |
| Producer | `organizations/TORG-*` | Licensed/registered producer or brand owner |
| Commercial product | `products/TPRD-*` | SKU/package tied to a producer |
| Batch | `lab-results/TLAB-*` | Batch-level COA record |
| Laboratory report | `lab-results/TLAB-*` | The COA itself (report and batch are one record for now) |
| Testing laboratory | `testing-laboratories/TSTL-*` | Accreditations and method panels |
| Measured analytes | `cannabinoids/TCBN-*`, `terpenes/TTRP-*` | Canonical compound records |
| Dataset snapshot | `datasets/TDTS-*` | Bulk COA datasets, dated and source-traceable |

The chain **cultivar label → producer → product → batch → report → analytes** maps to existing collections; no new collection or ID prefix is required. `metadata/id-map.jsonl` is unchanged by this model.

---

## 3. Relation vocabulary

The site's Boris frontmatter currently exposes a single `relates_to` verb. The vocabulary below is the **semantic target layer**: each semantic edge is materialized today as a `relates_to` edge plus a qualified, evidence-labeled statement in page narrative, and can be lifted into a typed graph store later without changing page content.

### 3.1 Measurement chain (defensible, batch-attached)

| Relation | Subject → Object | Evidence requirement |
| --- | --- | --- |
| `produced_by` | product/batch → producer organization | Registry/product record |
| `sold_under` | product → cultivar label | Producer/brand claim (rank B/G) |
| `measured_in` | compound → batch | Analyte measurement in a COA |
| `reported_by` | batch/report → testing laboratory | COA issuer |
| `measured_with` | batch → method/instrument | COA method section |
| `analyzed_in` | batch → jurisdiction | Report jurisdiction; license context |
| `consistent_with` | batch → chemotype cluster | Derived-layer output (no causation) |

### 3.2 Identity and lineage (claim-backed)

| Relation | Semantics | Multiplicity |
| --- | --- | --- |
| `claimed_parent` | asserted dam/sire/pollen pool; role = maternal\|paternal\|unspecified | Many |
| `breeder_claimed_by` | who claims creation/selection; role = creator\|selector\|popularizer\|marketer | Many |
| `alias_of` | same market/genetic identity under another name | Sparse; prefer alias strings |
| `possibly_related_to` | soft genetic/historical link (method = genetic_cluster\|shared_clone_story\|name_family) | Many |
| `phenotype_of` | numbered/named selection from a seed lot or clone line | Many |
| `clone_of` | asserted asexual identity to a mother plant | Rare; strong evidence only |
| `renamed_to` | commercial/legal rename event (temporal) | Few |
| `derived_seed_line_of` | S1/BX/F2 etc. from a named line; generation code attached | Many |

Every lineage edge carries a claim record (see §3.4 of the cultivar-identity artifact): claim type, subject, predicate, object, polarity, confidence, status, valid-from/to.

### 3.3 Chemistry (evidence-classed)

| Relation | Semantics | Constraint |
| --- | --- | --- |
| `isomer_of` / `enantiomer_of` / `geometric_isomer_of` | identity relationships | Established structural chemistry only |
| `biosynthesized_from` | precursor → product (e.g., CBGA → THCA/CBDA/CBCA) | Established pathway literature |
| `degrades_to` | thermal/oxidative product | Analytical/kinetic evidence; temperature- and pressure-labeled |
| `co_occurs_with` | measured co-detection (compound↔compound, batch-level) | Observational; no causation |
| `interacts_with` | compound → biological target | In vitro/mechanistic class only |
| `investigated_for` | compound → effect | Evidence class always attached (human clinical / human observational / preclinical / in vitro / mechanistic / traditional / industry) |

### 3.4 Derived layer (analysis outputs, never raw facts)

`belongs_to_cluster`, `label_distribution_over`, `profile_similar_to` — these are products of the derived layer with an explicit method string, parameter set, and dataset snapshot reference; they are recomputable and never stored as immutable facts.

---

## 4. Normalized analyte-profile representation

A **batch profile** is the unit of truth. Representation in JSON (schema: `metadata/cultivar-batch-profile.schema.json`; Python: `scripts/cultivar_profiles.py`):

```text
BatchProfile {
  batch_id, lab_report_id, producer_id, product_id,
  cultivar_labels: [label, ...],          # as printed; never collapsed
  jurisdiction, sample_type,              # flower, extract, concentrate, …
  basis,                                  # dry-weight | as-received
  decarb_convention,                      # native | total-potential (e.g., THCA×0.877+THC)
  harvest_date?, report_date,
  analytes: [ AnalyteMeasurement, ... ]
}

AnalyteMeasurement {
  compound_id,                            # canonical entity id (TCBN/TTRP)
  compound_name,
  value?, unit,                           # mg/g | % w/w | mg/mL | …
  censoring,                              # numeric | nd | below_lod | below_loq | not_tested
  lod?, loq?, method, quantitation_note?
}
```

Rules:

- **One row per compound per batch.** No denormalized cultivar×compound matrices in the raw layer.
- **`censoring` is mandatory.** A numeric `value` requires `censoring == numeric`.
- **Basis and units must be consistent within a batch**; cross-batch comparison requires explicit basis normalization (dry-weight), never implicit.
- **`decarb_convention` is mandatory** for cannabinoid profiles because GC-total vs LC-native numbers are not comparable.
- **Compound identity keys on canonical entity IDs**, never on display names, so acid/neutral and isomer distinctions survive.

---

## 5. Strategy for missing / not-tested / ND / <LOD / <LOQ

| State | Meaning | Stored as | Allowed uses |
| --- | --- | --- | --- |
| `not_tested` | Analyte not on the panel | `censoring=not_tested`, no value | Reporting-rate denominator; **never** a zero |
| `nd` | Tested; not detected above the method detection capability | `censoring=nd`, `value` absent, optional `lod` | Detection indicators; censored-data estimators |
| `below_lod` | Detected signal below the limit of detection | `censoring=below_lod`, `lod` set | Censored-data estimators; never a zero |
| `below_loq` | Quantified but below the reliable quantitation limit | `censoring=below_loq`, `loq` set | Range-bounded value; never a zero |
| `numeric` | Fully quantified | `value` required | Direct use |

- **No silent imputation.** Converting <LOD/<LOQ to 0 (or to LOD/2, or to LOQ) is a **data-product decision** that must be labeled on every derived output. The default in `scripts/cultivar_profiles.py` is to *refuse* implicit substitution and require an explicit `zero_strategy` argument.
- Derived summaries report **censorship rates** alongside any statistic (`n_tested`, `n_detected`, `n_below_loq`, `n_not_tested`) so a 0.02% mean with 90% <LOQ is visibly different from a 0.02% mean with 90% quantified.
- Future work: Kaplan–Meier-style or MLE censored estimators for label-level summaries when sample counts justify them (n ≥ 30 per label per the co-occurrence artifact's minimum-subgroup guidance).

---

## 6. Metrics (defined; thresholds deferred)

Definitions only — the model stores/derives these; *cutoffs are editorial choices*:

| Metric | Definition | Notes |
| --- | --- | --- |
| Sample count | number of batch profiles per label/producer/jurisdiction | Always reported with any other metric |
| Within-label similarity | distribution of pairwise profile distances among batches sharing a label | Distance metric recorded (see §7) |
| Dominant chemotype prevalence | share of a label's batches in the modal chemotype cluster | Depends on cluster method + k |
| Terpene-profile entropy | Shannon entropy over CLR-transformed mean relative abundances | Zero-handling strategy must be recorded |
| Producer dependence | variance partition of a label's profiles explained by producer | ANOVA/mixed-model; requires ≥2 producers × ≥2 batches |
| Jurisdiction dependence | same, by jurisdiction | Confounded with producer; report both |
| Batch variance | within-product batch-to-batch dispersion | Same product, same producer |
| Profile similarity | pairwise distance (e.g., Aitchison distance on CLR) | See §7 |

Verbal labels ("consistent", "moderately variable", "highly heterogeneous") are **editorial/data-product choices** and must be published with their numeric cutoffs; none are hard-coded in this model.

---

## 7. Distance and normalization

- **Compositional data discipline:** terpene and cannabinoid abundances are compositions (parts of a whole). Raw Euclidean distance on untransformed percentages is misleading. The model normalizes to dry-weight basis, then supports centered-log-ratio (CLR) transformation for distances (Aitchison geometry).
- **Zero handling:** CLR requires positive values. The implementation exposes an explicit `zero_strategy` parameter (`multiplicative_replacement_<delta>` is the suggested default when a strategy must be chosen) and refuses to guess.
- Co-detection structure (Jaccard on detection indicators) is kept separate from abundance structure — the two answer different questions.

---

## 8. Migration impact assessment

**Current archive state (verified this wave):** `cultivars/TCUL-0001` (Blue Dream, label + demo records), `TCUL-0002…0009` (label-only overviews), `products/TPRD-0001` (demo), `lab-results/TLAB-0001` (demo COA), guides `TGDE-0003`/`TGDE-0005`, reference `TREF-0002`. No verified batch COAs exist in the archive; the demo records are explicitly labeled non-evidence.

**Impact of this model:**

| Area | Impact |
| --- | --- |
| Content structure | **None forced.** Existing cultivar/product/lab-result pages stay put; new batch records land under `lab-results/TLAB-*`, products under `products/TPRD-*`, producers under `organizations/TORG-*`. |
| IDs / id-map | **None.** No new collection, no renumbering. `ted_ids.py` unchanged by this model (already immutable-safe after the compound wave). |
| Relations | Batch records add `relates_to` edges to cultivar/product/organization/compound records. Semantic verbs documented here (not in frontmatter). |
| Validation | `audit_markdown_links.py` and Boris graph checks unchanged; new unit tests cover the profile module. |
| Data | Bulk COA datasets are ingested as dated, source-traceable `datasets/TDTS-*` snapshots, never edited in place. |
| Existing demo records | Remain labeled demonstration; they are excluded from derived-layer statistics by an explicit `record_kind != verified` filter. |

**Risk register:** (1) treating demo/placeholder batches as evidence — prevented by `record_kind`; (2) silent renumbering during bulk ingest — prevented by `NaturalKeyRegistry`-style keyed allocation in the ingest pipeline; (3) mixing native vs total-potential cannabinoid figures — prevented by the mandatory `decarb_convention` field.

---

## 9. Implementation status

| Deliverable | Status |
| --- | --- |
| Schema design document | This document |
| Normalized profile schema | `metadata/cultivar-batch-profile.schema.json` |
| Minimal implementation | `scripts/cultivar_profiles.py` (profile model, censoring, validation, censorship summary, explicit zero-handling, similarity primitive) |
| Tests | `tests/test_cultivar_profiles.py` |
| Analysis engine (clustering, entropy, variance partition) | **Deferred** until real batch data exists (n ≥ 30 per label) |

## 10. Open questions / research gaps

- `research/cannabis/profile-similarity/` directory absent from the corpus; profile-similarity methodology in §7 is synthesized from the terpene-cooccurrence artifact and general compositional-data practice.
- No public canonical reference panel of verified cultivar→genetics mappings exists; genetic identity edges remain claim-backed.
- Threshold validation ("consistent/variable") needs literature citation before any verbal labeling is published.

---

*Compiled 2026-08-08. Companion reports: `reports/compound-dossier-wave-01.md` (compound side), `research/cannabis/cultivar-identity/artifact.md` (authority ranking).*
