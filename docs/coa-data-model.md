# COA, Batch & Analyte Knowledge-Graph Foundation — Canonical Data Model

**Status:** Established · **Scope:** the canonical data model that lets
thermalextractiondevices.com represent real cannabis laboratory reports without
incorrectly attaching measured chemistry directly to cultivar names. This is
the archive-facing foundation for ingesting hundreds of thousands of reports
and millions of analyte observations with full source provenance.

**Companion documents:** `docs/graph/coa-lab-data-model.md` (measurement
normalization, units, comparability grading), `docs/graph/coa-migration.md`
(migration path), `docs/graph/coa-examples.md` (real-data examples),
`docs/graph/cultivar-chemotype-model.md` (derived batch profiles).
**Implementations:** `scripts/coa_model.py`, `metadata/coa-measurement.schema.json`,
`scripts/audit_coa_content.py`, `bin/validate_graph.sh`.

---

## 1. Core principle

**Measurements belong to reports/batches — never intrinsically to cultivar
names.**

```text
Wrong:
  Blue Dream
    THC: 22%
    Myrcene: 0.8%

Correct:
  Cultivar entity  ── claimed identity ──►  Product  ──►  Batch
                                                          │ tested by
                                                          ▼
                                                     LabReport
                                                          │ reports
                                                          ▼
                                                     AnalyteResult
                                                          │ analyte
                                                          ▼
                                              THCA / Δ9-THC / β-myrcene / …
```

Every number in the archive answers the question *"where exactly does this THC
number come from?"* by traversing:

```text
canonical compound  ←  analyte result  ←  laboratory report  ←  batch/product  ←  source document
```

and no measurement ever claims to describe every product sold under the same
cultivar name.

---

## 2. Entity model

| Entity | Representation | Required? | Notes |
| --- | --- | --- | --- |
| Cultivar | `content/cultivars/` (`cultivars/TCUL-XXXX`) | n/a | Canonical informational cultivar entity. Stores identity/genetics, **never** universal chemistry values. |
| CultivarClaim | `batch.cultivar_claims[]` (`CultivarClaim`) | no | The name/identity **claimed** for a product or batch, plus an explicit resolution grade. |
| Product | `content/products/` (`products/TPRD-XXXX`) | via `batch.product_id` | Commercial product identity (flower, pre-roll, concentrate, vape…). Distinct from batch identity. |
| Batch | `batch` (`Batch`) | yes | Production/lot/batch identity: `batch_id` (natural key), `lot_number`, `metrc_tag`, dates, producer, product, claims. |
| LabReport / COA | `content/lab-results/` (`lab-results/TLAB-XXXX`) | yes | One laboratory report document with identity, dates, laboratory, jurisdiction, panels, provenance. |
| AnalyteResult | `measurements[]` (`AnalyteMeasurement`) | ≥1 per report | One observation of one analyte in one report. |
| TestingLaboratory | `content/testing-laboratories/` (`testing-laboratories/TSTL-XXXX`) | via `report.laboratory` | Existing collection reused. |
| Compound | `cannabinoids/TCBN-*`, `terpenes/TTRP-*`, `contaminants/TCNT-*`, `botanicals/TBOT-*` | via `compound_id` | Canonical compound identity; set only when a record exists. |
| Jurisdiction | `content/jurisdictions/` (`TJUR-*`) | via `jurisdiction` field | Regulatory context as metadata. |
| Organization / License | `organizations/TORG-*`, `licenses/TLIC-*` | via `producer_id` / `license_references` | Producer and license references. |
| Dataset / Source | `content/datasets/` (`TDTS-*`) + `report.provenance` | via provenance | Bulk-source registration and per-report retrieval metadata. |

### 2.1 ID discipline

No new collections or ID prefixes are introduced by this model. The existing
families in `scripts/ted_ids.py` / `metadata/id-map.jsonl` are reused:
`lab-results/TLAB`, `products/TPRD`, `cultivars/TCUL`, `testing-laboratories/TSTL`,
`organizations/TORG`, `licenses/TLIC`, `cannabinoids/TCBN`, `terpenes/TTRP`,
`contaminants/TCNT`, `botanicals/TBOT`, `jurisdictions/TJUR`, `datasets/TDTS`.
IDs are immutable: a retest or correction is a **new** report record
(`revision` / `supersedes`), never a renumber or an edit of history. Global
multi-jurisdiction ID allocation is not solved here; provisional natural keys
(e.g. `ma-ccc:<metrc tag>`) are legal for non-verified records and must be
replaced by canonical `lab-results/TLAB-XXXX` ids before verification.

---

## 3. Relationship model

```text
CultivarClaim ──► Product ──► Batch ──► LabReport ──► AnalyteResult ──► Compound
                      ▲            ▲            ▲             ▲
                      │            │            │             └─ testing-laboratory
                 producer     producer    laboratory       jurisdiction
                 (TORG)      (TORG)      (TSTL)              license (TLIC)
```

- **CultivarClaim → Cultivar.** A claim *may* resolve (`resolution`:
  `resolved` / `tentative` / `ambiguous` / `unresolved`) to a canonical
  `cultivars/TCUL-XXXX` record. Resolution is **never forced**: an unknown
  label stays unresolved with `cultivar_id: null`, and `candidate_ids` lists
  the several possibilities for an ambiguous label.
- **Batch → Product / Producer.** `batch.product_id` /
  `batch.producer_id` are canonical ids when records exist, else `null` —
  never invented identities.
- **Batch → LabReport.** One batch may have retests, corrected reports,
  multiple panels, or reports from different laboratories. Each is a separate
  report sharing the same `batch_id`.
- **LabReport → AnalyteResult.** Measurements exist only inside a report;
  the content audit (`COA-05`) rejects report pages that cannot be traced to a
  batch/product/cultivar.
- **AnalyteResult → Compound.** `compound_id` is set only when a canonical
  record exists (`cannabinoids/TCBN-0007` for THCA, `contaminants/TCNT-0007`
  for Lead). Unknown analytes keep their parsed `compound_name` and
  `compound_id: null` — identity is never invented.
- **LabReport → Provenance.** Every report carries retrieval metadata
  (source URL, document hash, retrieval date, upstream record id, parser
  version); verified records **require** at least one of
  `source_url` / `document_hash` / `upstream_record_id`.

---

## 4. Measurement semantics

| Capability | Field |
| --- | --- |
| Analyte identity | `compound_id` (canonical when mapped) + `compound_name` (as parsed) |
| Reported value | `reported_value` — exact printed string, never rounded |
| Reported unit | `reported_unit` — exact printed unit |
| Normalized value / unit | `value` / `unit` (audited conversion; see §6) |
| Result qualifier | `state` — eight distinct states (§5) |
| LOD / LOQ | `lod` / `loq` (per measurement, same unit) |
| Method | `method` (report- or measurement-level `MethodMetadata`) |
| Measurement basis | `batch.basis` (`dry-weight` / `as-received` / `unknown`) |
| Test / sample date | `report.test_date` / `report.sample_date` (+ per-measurement `test_date`) |
| Calculated quantity | `calculation_formula` — set when the row is report-derived (e.g. Total THC) |

### 4.1 Cannabinoid semantics

THCA, Δ9-THC, Δ8-THC, CBDA, CBD, CBGA, CBG, CBN, CBC, THCVA, THCV, etc. are
kept chemically distinct; acid and neutral forms are **never** collapsed.
Calculated values such as *Total THC* / *Total CBD* are represented as
calculated/report-derived quantities (`calculation_formula` retains the
source's formula, e.g. `d9-THC + THCA * 0.877`), not as independent chemical
compounds — a calculated row should not carry a `compound_id` (soft warning).

### 4.2 Terpene semantics

Reported names are preserved verbatim (`compound_name`). Canonical terpene
records are resolved by `compound_id` where unambiguous (β-myrcene →
`terpenes/TTRP-0005`, D-limonene → `terpenes/TTRP-0004`). Ambiguity —
nerolidol isomers, ocimene isomers, limonene stereochemistry, α/β pinene — is
**not** resolved by inference: the model records what the laboratory printed
and never invents stereochemistry the lab did not report.

### 4.3 Contaminant semantics

The panel vocabulary supports pesticides, heavy metals, microbial analytes,
mycotoxins, residual solvents, foreign material, water activity, moisture, and
other jurisdiction-specific panels (`report.test_panels`). Jurisdictions are
not assumed to test the same analytes: absence of an analyte from a panel is
`not_tested`, which is a different fact from `nd`, `missing`, or `zero`.

---

## 5. Qualifier (result state) semantics

| State | Meaning | Stored as |
| --- | --- | --- |
| `numeric` | Fully quantified (≈ "detected" with a number) | `value` required; `reported_value` required |
| `nd` | Tested; not detected above detection capability | `value` null, optional `lod` |
| `below_lod` | Detected signal below the limit of detection | `value` null, `lod` **required** |
| `below_loq` | Quantified but below reliable quantitation limit (≈ "<LOQ") | `value` null, `loq` **required** |
| `zero` | Explicit `0`/`0.0` as printed | `value` = 0.0, flagged for review |
| `missing` | Source record exists but result field blank (≈ "not reported") | `value` null |
| `not_tested` | Analyte absent from the panel | `value` null |
| `invalid` | Result string present but unparseable | `value` null; string preserved in `reported_value` |

Mandatory rules, enforced by `measurement_problems` / `coa_problems`:

- **ND is never converted to zero.**
- **<LOQ / <LOD are never converted to zero.**
- **A missing analyte is never inferred to be not detected.**
- **`below_lod` requires an `lod`; `below_loq` requires an `loq`.**
- **An explicit printed zero stays `zero`** (flagged for review) — it is never
  silently rewritten as `nd` or `missing`.

Decoding from printed strings is the pure function `decode_result`
(`"ND"`, `"<LOD"`, `"<LOQ"`, `"<0.05"`, `"0.0"`, `"not tested"`, blank,
unrecognized). No substitution routine exists in the model: `LOQ/2`,
`LOD/√2`, and zero-replacement are explicit data-product decisions deferred to
the future analysis engine, where they must be dataset-labeled.

---

## 6. Unit handling

Reported representation is **always preserved**: `reported_value` /
`reported_unit` keep the exact printed string and unit (`%`, `ppm`, `CFU/g`,
`<0.05`, …). `value` / `unit` carry the normalized representation.

| From → To | Rule | Condition |
| --- | --- | --- |
| `% w/w` ↔ `mg/g` | ×10 / ÷10 | Same basis |
| `% w/w` ↔ `ug/g` | ×10⁴ / ÷10⁴ | Same basis |
| `mg/g` ↔ `ug/g` | ×10³ / ÷10³ | Same basis |
| `ppm` ↔ `ug/g` | identity (mass/mass) | Same basis |
| `ppb` ↔ `ug/g` | ÷10³ | Same basis |
| `mg/mL`, `ug/mL` ↔ mass/mass | via density | **Verified density required**; never a bulk-density guess |
| `CFU/g` ↔ `CFU/mL` | via density | Density required |
| dry-weight ↔ as-received | via moisture fraction | **Moisture required**; else `MoistureRequiredError` |

Every conversion produces a `ConversionAudit` (formula, parameters, added
uncertainty) — conversions never happen silently. Values are never rounded
during ingestion; rounding is a display-time decision via `round_to_sigfigs`
with the recorded `rounding_rule`. Values with incompatible measurement bases
are never silently compared.

---

## 7. Cultivar identity rules

1. A cultivar entity stores identity (lineage, origin, genetics), not chemistry.
2. Chemistry is attached to `AnalyteResult`s under `LabReport`s under
   `Batch`es. A batch's cultivar identity is a **claim** (`CultivarClaim`)
   with an explicit resolution grade.
3. Resolution is optional and graded: `resolved` (confident, requires
   `cultivar_id`), `tentative` (leaning, may name `cultivar_id`), `ambiguous`
   (several possibilities in `candidate_ids`), `unresolved` (no target).
4. Reported labels are preserved verbatim (`cultivar_labels` on the batch,
   `label` on each claim) and never silently canonicalized.
5. Cultivar pages may list *"Observed laboratory reports associated with
   products carrying this cultivar name"* — never *"typical chemistry of this
   strain"* unless separately supported by an actual statistical dataset.
   The content audit (`COA-04`) rejects cultivar pages that carry numeric
   measurement units.

---

## 8. Provenance rules

Every real observation must be traceable to a source:

```text
AnalyteResult → LabReport → source document / official endpoint → retrieval metadata
```

`SourceProvenance` on the report records: `source_url`, `document_hash`
(sha256), `retrieval_date`, `upstream_record_id`, `parser_version`,
`retrieval_note`. Verified records **require** at least one of
`source_url` / `document_hash` / `upstream_record_id` — a verified record
without provenance is rejected (`coa_problems`). An internal research note is
never terminal evidence; the terminal evidence is the source document or
official endpoint, and `parser_version` lets reprocessing audits trace how the
record was produced.

---

## 9. Examples

### 9.1 The demonstration fixture (`lab-results/TLAB-0001`)

`content/lab-results/example-producer-blue-dream-batch-123.md` is the ONE
synthetic fixture that exercises the model end to end. It is unmistakably
labeled **DEMONSTRATION / SYNTHETIC DATA** (frontmatter tags + the
`includes/demo-sample-record-warning.md` include) and is excluded from all
derived statistics by `record_kind`. It demonstrates:

- one product (`products/TPRD-0001`), one batch, one lab report;
- several cannabinoid results (THCA, Δ9-THC, CBGA — acid/neutral distinct);
- several terpene results (β-myrcene, α-pinene, D-limonene, β-caryophyllene);
- a calculated Total Active Cannabinoids row with its formula;
- an `ND` row (Lead), a `<LOQ` row (Ochratoxin A), a `missing` row
  (Bifenthrin, blank result), and a `not_tested` row (Spinosad);
- a cultivar claim section (label "Blue Dream", resolution `unresolved`);
- a source/provenance placeholder section.

### 9.2 Real-data examples

`docs/graph/coa-examples.md` maps **real** Massachusetts CCC testing rows
(THCA `29.05 %`, Lead `0.0 ppm` → `zero`, Arsenic `0.0 ppm` → `zero`,
cross-lab THC spread 0.0–3.26 %) through `decode_result`,
`from_massachusetts_normalized`, and `comparability_grade`.

**The first verified record** — `lab-results/TLAB-0002` — is a real published
COA walked through the model end to end by `scripts/coa_verify_example.py`:
InfiniteCAL (CA) report for Powered By Plants "Dragonberry 750ml (10mg)"
(batch 250410-37-002, produced 2025-07-11). It exercises the full chain
(compound ← analyte result ← report ← batch/product ← source document):
numeric + ND + `<LOQ` + calculated rows, the per-package `mg/pkg` unit escape
hatch, LOD/LOQ fidelity, method overrides (UHPLC-DAD / ICP-MS / GC-MS / PCR),
and provenance (official TagLeaf verification URL, PDF sha256, retrieval
date, upstream id, parser version).

---

## 10. Ingestion expectations

1. **Capture the artifact.** A real COA (PDF/CSV from a laboratory or
   regulator portal) is snapshotted, checksummed, and registered in a
   `datasets/TDTS-*` record.
2. **Allocate identities.** `NaturalKeyRegistry` allocates
   `lab-results/TLAB-XXXX` (report) and reuses existing
   `testing-laboratories/TSTL-*`, `organizations/TORG-*`, `products/TPRD-*`,
   `cultivars/TCUL-*`; unknown identities stay `null`.
3. **Map measurements.** Each printed analyte row becomes an
   `AnalyteMeasurement` via `scripts/coa_model.py`: verbatim
   `reported_value`/`reported_unit`, decoded `state`, normalized `value`/`unit`
   with audit, per-analyte `lod`/`loq` when printed, method metadata when a
   method section exists. Missing metadata is recorded as unknown/soft
   warnings — never invented.
4. **Record provenance.** `source_url`, `document_hash`, `retrieval_date`,
   `upstream_record_id`, `parser_version` are set from the ingestion run.
5. **Publish + validate.** Records generate into `content/lab-results/` with
   the closed Boris frontmatter schema; `bin/validate_graph.sh` (which now
   includes the COA content audit) gates publication.

The model tolerates incomplete historical data: optional dates, missing
method sections, unknown analytes, and provisional ids are all representable.
It rejects only what corrupts the graph (see §11).

---

## 11. Graph validation (what is prevented)

Model-level (`scripts/coa_model.py`, hard unless noted):

- AnalyteResult with no LabReport — measurements exist only inside `CoaRecord`.
- LabReport with no source/provenance — verified records require provenance.
- Duplicate report identity — IDs are immutable and unique; `ted_ids.py`
  rejects duplicate entity ids.
- Invalid analyte target — `compound_id` must match a canonical compound
  pattern when set.
- Unknown unit vocabulary — non-canonical units are soft warnings.
- ND with numeric zero substituted — `nd` must not carry a value; explicit
  zeros stay `zero`.
- `<LOD` / `<LOQ` missing threshold — `below_lod` requires `lod`,
  `below_loq` requires `loq`.
- Chemistry attached directly to Cultivar — `COA-04` content audit.
- Broken batch/product/report relations — `COA-05`/`COA-06` content audit.

Content-level (`scripts/audit_coa_content.py`, wired into
`bin/validate_graph.sh`): see the script's docstring for rules COA-01…07.

---

## 12. Known unresolved questions

- **Global multi-jurisdiction ID allocation** is not solved here; the
  repository's existing `NaturalKeyRegistry` approach (provisional natural
  keys → canonical `TLAB-*` at verification) is the approved mechanism.
- **Massachusetts limits.** CCC open data publishes no LOD/LOQ, method, or
  basis; per-analyte limits must come from laboratory method summaries or
  regulator PT guidance before `below_lod`/`below_loq` states can be populated
  for that jurisdiction.
- **THC canonical record.** Δ9-THC has no `cannabinoids/TCBN-*` record yet;
  MA THC rows map to `compound_id: null` until the compound corpus creates one.
- **Analysis engine.** Graded pooling, censored-data estimators, and
  uncertainty propagation are deferred until real verified batch data exists.
- **Claim resolution corpus.** Cultivar name resolution (aliases like
  "GG4" → "Original Glue") needs a curated alias table before
  `resolved`/`tentative` claims can be produced at scale; until then claims
  stay `unresolved`, which the model fully supports.

---

*Compiled 2026-08-09. Implementations: `scripts/coa_model.py`,
`metadata/coa-measurement.schema.json`, `scripts/audit_coa_content.py`,
`bin/validate_graph.sh`. Companion: `docs/graph/coa-lab-data-model.md`,
`docs/graph/coa-migration.md`, `docs/graph/coa-examples.md`.*
