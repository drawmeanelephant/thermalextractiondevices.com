# COA Knowledge-Graph Foundation — Implementation Report

**Status:** Implemented · **Date:** 2026-08-09 · **Branch worktree:** COA data-model foundation wave.

**Mission:** design and implement the canonical data model so
thermalextractiondevices.com can represent real laboratory reports without
attaching measured chemistry directly to cultivar names — with provenance, a
defensible "where does this THC number come from?" chain, validation, rendering
strategy, a demonstration fixture, and a migration path. **No Massachusetts
data was ingested, altered, or activated.** Massachusetts work continues
concurrently; the model is built to be *used by* Massachusetts later, and the
existing CCC adapter (`from_massachusetts_normalized`,
`massachusetts_rows_to_record`) was left untouched and its tests green.

---

## 1. What already existed (inspected, reused, not re-invented)

| Asset | Role |
| --- | --- |
| `scripts/coa_model.py` | Durable model: `AnalyteMeasurement`, `Report`, `Batch`, result states, audited unit/basis conversion, comparability grading A–F, MA CCC adapter |
| `metadata/coa-measurement.schema.json` | JSON Schema mirroring the model |
| `docs/graph/coa-lab-data-model.md`, `coa-migration.md`, `coa-examples.md` | Existing design/migration/example docs |
| `scripts/cultivar_profiles.py`, `metadata/cultivar-batch-profile.schema.json` | Derived batch-profile layer (untouched) |
| `content/lab-results/TLAB-0001` + `products/TPRD-0001` + `cultivars/TCUL-0001` | Existing demonstration fixture (extended, not replaced) |
| `scripts/ted_ids.py`, `metadata/id-map.jsonl` | ID system (no new prefixes, no renumbering) |
| `bin/validate_graph.sh` | Validation gate (new audit step added) |

The existing model already enforced the mission's hardest rules (ND/<LOQ/0/missing/not-tested never conflated, verbatim reported values, audited conversions, no fabricated identities). This wave filled the gaps: cultivar claims, batch identifiers/dates, report provenance, license/panel metadata, an `invalid` state, calculated-quantity representation, content-level graph validation, and the task-named documentation.

---

## 2. Files changed

### New files

| File | Purpose |
| --- | --- |
| `docs/coa-data-model.md` | Canonical COA data-model document (task-required) |
| `reports/coa-model-implementation.md` | This report (task-required) |
| `scripts/audit_coa_content.py` | COA content audit, rules COA-01…07 |
| `tests/test_audit_coa_content.py` | Tests for the audit |

### Modified files

| File | Change |
| --- | --- |
| `scripts/coa_model.py` | `invalid` state; `CultivarClaim` + resolution enum; `SourceProvenance`; Batch `lot_number`/`production_date`/`package_date`/`cultivar_claims`; Report `sample_id`/`license_references`/`test_panels`/`provenance`; `AnalyteMeasurement.calculation_formula`; validation/warnings for all; docstring |
| `metadata/coa-measurement.schema.json` | New definitions `cultivarClaim`/`sourceProvenance`; new fields on report/batch/measurement; `invalid` in state enum; descriptions |
| `bin/validate_graph.sh` | Added the COA content audit step |
| `content/lab-results/example-producer-blue-dream-batch-123.md` | Extended the demonstration fixture: ND, <LOQ, missing, not-tested rows; cultivar claim section; provenance placeholder; calculated Total Active Cannabinoids retained with formula; explicit DEMONSTRATION/SYNTHETIC DATA banner |
| `content/cultivars/blue-dream.md` | Section reworded to "Observed Laboratory Reports…" with the careful claim language |
| `tests/test_coa_model.py` | Updated for `invalid`; new test classes: `CultivarClaimTest`, `BatchAndReportExtensionTest`, `ProvenanceValidationTest`, `CalculatedQuantityTest`; schema-consistency checks for new keys (54 tests, up from 37) |

---

## 3. Schema decisions

- **Additive extension, `schema_version` stays `"1.0"`.** Every new field is
  optional, so existing records (and the MA adapter output) validate unchanged.
- **`invalid` is a new result state, distinct from `missing`.** `missing` =
  blank result field; `invalid` = result string present but unparseable. The
  string is preserved verbatim in `reported_value`. Both must not carry a
  `value`. The MA fixture rows are all numeric, so the adapter's decoded
  states are unchanged.
- **`CultivarClaim` is a claim, not a measurement.** `label` (verbatim),
  `resolution` (`resolved`/`tentative`/`ambiguous`/`unresolved`), optional
  `cultivar_id`, optional `candidate_ids` for ambiguity. `resolved` requires
  `cultivar_id`; everything else tolerates absence. Raw `cultivar_labels` on
  the batch are kept for backward compatibility.
- **`SourceProvenance` is attached to the report**, carrying source URL,
  document hash, retrieval date, upstream record id, parser version. Verified
  records require ≥1 of URL/hash/upstream-id — this is the "LabReport with no
  source/provenance" corruption check. Unverified records only warn.
- **Calculated totals** (`Total THC`, `Total CBD`, `Total Terpenes`) are
  represented by `calculation_formula` on the measurement; carrying a
  `compound_id` on a calculated row is a soft warning (they are not
  independent chemical compounds).
- **License references and test panels** are free-form tuples; non-canonical
  license strings and unknown panel names are soft warnings, never hard
  errors — legitimate historical data must stay representable.
- **Dates** (`harvest_date`, `production_date`, `package_date`, retrieval
  date) are optional; non-ISO values warn instead of failing (incomplete
  historical data is tolerated).

---

## 4. Validation added

### Model-level (hard, `scripts/coa_model.py`)

- verified record without provenance → `ValueError`
- resolved claim without `cultivar_id` → `ValueError`
- `cultivar_id` / `candidate_ids` not canonical `cultivars/TCUL-XXXX` → `ValueError`
- `below_lod`/`below_loq` without threshold (pre-existing, retained)
- ND/`invalid`/`missing`/`not_tested` carrying a value (pre-existing contract, extended to `invalid`)
- `invalid` added to the schema's state enum and its no-value contract

### Content-level (`scripts/audit_coa_content.py`, wired into `bin/validate_graph.sh`)

| Rule | Severity | Meaning |
| --- | --- | --- |
| COA-01 | error | lab-results page lacks canonical `lab-results/TLAB-XXXX` id or `status: published` |
| COA-02 | error | demonstration/synthetic page lacks the demo-sample-record-warning include (unmistakable label) |
| COA-03 | error | non-demonstration report page lacks a Provenance/Sources section with a URL |
| COA-04 | error | cultivar page carries numeric measurement units (chemistry attached to a cultivar name) |
| COA-05 | error | report page has no product/cultivar/organization relation (isolated report) |
| COA-06 | warning | frontmatter relation references an id absent from `metadata/id-map.jsonl` |
| COA-07 | warning | report page has no compound-page relation |

Rules COA-01…05 block; COA-06…07 inform (mirrors the REC-* severity split).

---

## 5. Demonstration fixture

`content/lab-results/TLAB-0001` remains the archive's ONE synthetic COA,
reused rather than duplicated. It now exercises the full qualifier story and
the provenance shape, and is unmistakably labeled:

- frontmatter tags: `demonstration`, `synthetic-data`;
- `{{include includes/demo-sample-record-warning.md}}` plus an explicit
  **DEMONSTRATION / SYNTHETIC DATA** banner;
- one product / one batch / one report; cannabinoid + terpene + contaminant
  panels; ND (Lead), `<LOQ` (Ochratoxin A), `missing` (Bifenthrin),
  `not_tested` (Spinosad); calculated Total Active Cannabinoids with formula;
  cultivar-claim section (`unresolved`); source/provenance placeholder
  section. It is excluded from derived statistics by `record_kind` discipline
  and is never presented as real evidence.

---

## 6. Migration implications

- **No migration of existing content is required.** The demo fixture stays a
  demonstration record; no synthetic value was copied into the model.
- **Verified records now require provenance.** The documented Path A/B
  ingestion (snapshot → checksum → `TDTS-*` dataset record → canonical
  `TLAB-XXXX` → publish) already produces it; the model now enforces it.
- **Massachusetts is unaffected and compatible.** `scripts/ingest/states/massachusetts.py`,
  `tests/fixtures/massachusetts/`, MA jurisdiction content, and the MA adapter
  in `coa_model.py` are unchanged; MA rows decode identically; the model's new
  fields are all optional, so MA records validate as before.
- **No ID changes.** No new collections/prefixes; `metadata/id-map.jsonl` and
  `scripts/ted_ids.py` untouched; `TLAB-0001` keeps its id.
- **Rendering strategy** (documented in `docs/coa-data-model.md` §2/§9): a
  LabReport page shows report identity, laboratory, product, batch, claimed
  cultivar, jurisdiction, dates, panels, and provenance; compound pages derive
  "Measured observations" from graph relations; cultivar pages derive
  "Observed laboratory reports associated with products carrying this cultivar
  name" — never "typical chemistry of this strain".

---

## 7. Remaining blockers

1. **Public-release audit git-history baseline.** `ted-build.sh` now runs the
   release audit unconditionally (main's publication-hardening wave removed the
   `SKIP_RELEASE_AUDIT` bypass and resolved the old `data/dcc/*` PII block). In
   a full-depth clone the audit reports 48 HIGH `PII-001 <history>` findings
   from pre-existing commits (e.g. `beau@boorman.tech`); this reproduces
   **identically on clean `main`** (verified: same 130 findings / 52 high on
   both trees, 0 on this wave's files) and is invisible to CI's shallow clone.
   The documented cleanup path is `reports/publication-hardening.md` +
   `docs/history-cleanup-plan.md`; no history rewrite is authorized here.
2. **Massachusetts merge blocker (concurrent work).** The MA pipeline remains
   fixture-only and merge-blocked by its own guards; out of scope here.
3. **Analysis engine** (graded pooling, censored-data estimators, uncertainty
   propagation) is deferred until real verified batch data exists.
4. **THC canonical record** — Δ9-THC still lacks a `cannabinoids/TCBN-*`
   record, so THC rows map to `compound_id: null` (existing open question).
5. **Cultivar claim-resolution corpus** — alias tables for confident
   `resolved` claims are future work; claims stay `unresolved` until then.
   Note: main's cultivar-identity wave (`metadata/cultivar-claims.jsonl`,
   `docs/cultivar-identity-model.md`) is the content-level claim registry;
   `CultivarClaim` in this COA model is the in-record representation of those
   claims (resolution grade on a batch/product). The two are complementary
   layers of one concept, not competing schemas.

---

## 8. Recommended ingestion sequence

1. Resolve the remaining release-audit git-history baseline (see blocker 1,
   `docs/history-cleanup-plan.md`) so the full-depth local gate and any
   non-shallow CI pass cleanly — independent of this model.
2. Land the first **verified** COA from any jurisdiction via Path A
   (snapshot → checksum → `TDTS-*` → canonical `TLAB-XXXX` → publish), which
   exercises provenance requirements against real data.
3. Unblock Massachusetts: complete the live CCC snapshot verification, then
   run Path B (`massachusetts_rows_to_record` → canonical ids). The model and
   its validation are ready; the CCC CSVs' missing method/LOD/LOQ metadata
   stays as documented soft warnings.
4. Add the compound-corpus records the model already resolves to
   (`THC`, more contaminants), then begin cultivar claim resolution with an
   alias table.
5. Build the analysis engine on verified records only, with explicit
   dataset-labeled substitution policies (LOQ/2, LOD/√2) as data-product
   decisions.

---

## 9. Validation runs

```text
python3 -m unittest discover -s tests        → OK (tests/test_coa_model.py: 54 tests, 1 skipped[jsonschema not installed, fallback runs]; tests/test_audit_coa_content.py: 9 tests)
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl   → validated N pages; no files changed
python3 scripts/audit_markdown_links.py content                        → pass
python3 scripts/audit_coa_content.py content --map metadata/id-map.jsonl → 0 errors, 0 warnings
./bin/validate_graph.sh                                                → pass (see below)
```

The release audit runs inside `scripts/ted-build.sh` (invoked by
`validate_graph.sh`) with no bypass now that main removed `SKIP_RELEASE_AUDIT`.
In a full-depth clone it fails on the pre-existing `<history>` PII baseline
(48 HIGH, identical on clean `main`; see blocker 1). All other gate steps pass
and CI's shallow clone is unaffected. Post-rebase totals: 254 tests OK
(6 skipped), ted_ids validates 415 pages, COA audit 0/0, markdown links
resolve, Boris graph clean, Cantilever build + HTML ID checks green.
