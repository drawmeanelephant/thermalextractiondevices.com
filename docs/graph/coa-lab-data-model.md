# COA & Laboratory Measurement Model — Design Document

**Status:** Established (durable model + normalization + comparability primitives landed) · **Scope:** the archive-facing data model for laboratory reports and analyte measurements at the scale of hundreds of thousands of reports and millions of measurements.

**Research inputs:** `research/cannabis/laboratory-comparability/source/2026-08-08-perplexity.md`, `research/cannabis/batch-variability/source/2026-08-08-perplexity.md`, `research/cannabis/chemotype-analysis/source/2026-08-08-perplexity.md`, `research/jurisdictions/united-states/national-data-surveys/artifact.md`. The `research/cannabis/analytical-chemistry/` directory named in the task brief is not present in the corpus; its subject matter is covered here by the laboratory-comparability report (method differences, detection limits, calibration) and is flagged as a research gap in §9.

**Companion model:** `docs/graph/cultivar-chemotype-model.md` owns the *derived* normalized batch-profile representation (`metadata/cultivar-batch-profile.schema.json`, `scripts/cultivar_profiles.py`). This document owns the *durable* measurement layer (`metadata/coa-measurement.schema.json`, `scripts/coa_model.py`): the report document, its batch, and every analyte measurement with full censoring, unit, method, and comparability metadata. Batch profiles are built from verified COA records — never the reverse.

**Guiding failure mode this design prevents:** treating "0", "ND", "<LOQ", "missing", and "not tested" as the same value, and treating one laboratory's number as interchangeable with another's when the methods, reporting bases, and limits differ.

---

## 1. Design principles

1. **Result states are never collapsed.** `numeric`, `nd`, `below_lod`, `below_loq`, `zero`, `missing`, and `not_tested` are seven distinct states with distinct allowed uses (see §5). The mission-level prohibition — never turn `ND` / `<LOQ` / `0` / `missing` / `not tested` into the same value — is enforced by the state enum and its value contracts, not by convention.
2. **Reported values are preserved verbatim.** `reported_value` / `reported_unit` keep the exact printed string and unit ("0.0", "1.34", "<0.05", "%", "ppm"). `value` / `unit` carry the normalized representation. Nothing is rounded during ingestion; rounding is a display-time decision via the recorded `rounding_rule` (measured = half-even, calculated = half-up; NIST and the Mississippi hybrid convention — laboratory-comparability report §1.5).
3. **Every conversion is audited.** Unit and basis conversions produce a `ConversionAudit` (formula, parameters, added uncertainty). Mass/volume conversions require a verified density; dry-weight ↔ as-received requires a moisture fraction. Conversions never happen silently, and the model refuses to guess: `DensityRequiredError`, `MoistureRequiredError`, and `UnitConversionError` are raised rather than approximated.
4. **Batch identity and report identity are distinct.** `batch_id` is the producer/operator batch identifier (stable across retests); `report_id` is the archive record (`lab-results/TLAB-XXXX`). One batch may have retests, corrected reports, multiple panels, or reports from different laboratories — each is a separate report sharing `batch_id`. `revision` / `supersedes` capture corrected-report history.
5. **Comparability is graded, never assumed.** Cross-lab and cross-jurisdiction pooling is gated by `comparability_grade` (A–F with reason codes, §7), which requires method, basis, moisture, PT, and uncertainty metadata that most public state datasets do not carry. Missing metadata lowers the achievable grade; the model never pretends unknown metadata away.
6. **No fabricated identities.** `compound_id` is set only when a canonical archive record exists (`cannabinoids/TCBN-0007` for THCA, `contaminants/TCNT-0007` for Lead). Unmapped analytes keep their parsed name and remain unmapped — the Massachusetts heavy-metal and yeast/mold analytes that lack canonical records stay `compound_id: null` rather than inventing entities.
7. **Only `record_kind == verified` records are analysis data.** `demonstration` and `unverified` records are never derived-layer inputs (matches the cultivar chemotype model). Fixture or synthetic data can never become publication data; the state-ingest CLI's `--allow-fixture-content` guard is the hard boundary.
8. **Batch-to-batch variability is expected, not an error.** The batch-variability research shows no single "canonical" chemotype represents a cultivar; the model therefore stores measurements per batch and never folds multiple batches into a fictional profile.

---

## 2. Canonical chain and entity inventory

```text
producer ──► product ──► batch/lot/package ──► laboratory ──► report ──► analyte measurements
    │            │              │                  │            │
 organizations/TORG-*   products/TPRD-*   batch_id + metrc_tag   testing-laboratories/TSTL-*   lab-results/TLAB-*
```

| Entity | Site collection / field | Notes |
| --- | --- | --- |
| Producer | `organizations/TORG-*` | Licensed/registered producer or brand owner |
| Product | `products/TPRD-*` | SKU/package tied to a producer |
| Batch/lot/package | `batch_id` (natural key) + `metrc_tag` (state traceability tag) | Stable across retests; one batch may map to several reports |
| Testing laboratory | `testing-laboratories/TSTL-*` | License, accreditation, method panels; `Laboratory` in the model |
| Laboratory report | `lab-results/TLAB-*` (`report_id`) | The COA document; `revision`/`supersedes` capture corrections |
| Analyte measurement | one `AnalyteMeasurement` per compound per report | State, reported + normalized value/unit, LOD/LOQ, method, conversion audit |
| Compound identity | `cannabinoids/TCBN-*`, `terpenes/TTRP-*`, `contaminants/TCNT-*`, `botanicals/TBOT-*` | Canonical entity ids; acid/neutral and isomer distinctions never collapsed |

No new collection or ID prefix is required; `metadata/id-map.jsonl` is unchanged by this model (`lab-results/TLAB` is already allocated in `scripts/ted_ids.py`).

### 2.1 Report revisions

A corrected COA is a new report record, not an edit of the old one: `revision` increments and `supersedes` names the prior `report_id`. Consumers that must not double-count corrected data filter to the latest revision per `batch_id`. Because IDs are immutable, a retest/correction never reuses an existing `lab-results/TLAB-*` id.

---

## 3. The measurement record

Full schema: `metadata/coa-measurement.schema.json`. Python: `scripts/coa_model.py`.

```text
CoaRecord {
  schema_version,
  report:   { report_id, revision, supersedes?, source_reference,
              report_date?, test_date?, sample_date?, laboratory?, jurisdiction, method? },
  batch:    { batch_id, metrc_tag, producer_id?, product_id?, cultivar_labels[],
              sample_type, matrix_detail, basis, decarb_convention, record_kind,
              jurisdiction, harvest_date? },
  measurements: [ AnalyteMeasurement, ... ]
}

AnalyteMeasurement {
  compound_id?, compound_name, compound_cas?,
  reported_value, reported_unit,       # exactly as printed
  state,                               # numeric|nd|below_lod|below_loq|zero|missing|not_tested
  value?, unit,                        # normalized representation
  lod?, loq?,                          # method limits, same unit
  method?, test_date?, quantitation_note?, conversion?
}
```

Every mission-required measurement field maps directly:

| Required capability | Model field |
| --- | --- |
| analyte identity | `compound_id` (canonical id when mapped) + `compound_name` |
| reported value | `reported_value` (verbatim string) |
| normalized value | `value` |
| original unit | `reported_unit` |
| normalized unit | `unit` |
| result qualifier | `state` |
| ND / <LOD / <LOQ | `state` = `nd` / `below_lod` / `below_loq` + `lod` / `loq` |
| LOD / LOQ | `lod`, `loq` (per measurement, same unit) |
| method where available | `method` (report- or measurement-level `MethodMetadata`) |
| test date / sample date | `report.test_date` / `report.sample_date` (+ per-measurement `test_date`) |
| laboratory | `report.laboratory` |
| source report | `report.report_id` + `report.source_reference` |
| report revision | `report.revision` / `report.supersedes` |

---

## 4. Method metadata and stratification

`MethodMetadata` (optional, report- or measurement-level) carries the minimum-viable-comparability fields from laboratory-comparability report §3: `instrument_technique`, `derivatization`, extraction/homogenization detail, `calibration_type`, `matrix_matched_calibration`, `calibration_range`, CRM vendor/lot, `moisture_method`, `moisture_content_pct`, `rounding_rule`, `significant_figures`, `measurement_uncertainty` (k=2), `uncertainty_method`, accreditation, and `pt_z_score`.

These fields are the raw material for the four stratified analyses named in the task:

- **lab-stratified** — every measurement is attached to `report.laboratory`;
- **jurisdiction-stratified** — `report.jurisdiction` / `batch.jurisdiction` (e.g. CA, MA) with the regulatory context as metadata, not a filter;
- **method-stratified** — `instrument_technique` + `derivatization` (GC vs LC is the largest documented bias: underivatized GC underestimates acidic cannabinoids by ~40–54%, laboratory-comparability report §1.1);
- **comparability grading** — §7.

The model never rejects mixed units or mixed matrices within a batch; it records them and leaves comparison to explicit, graded normalization. State datasets that omit method, LOD/LOQ, or basis (the CCC testing files carry none of these) are recorded with explicit unknowns and soft warnings — never with invented method sections.

---

## 5. Result states (censoring discipline)

| State | Meaning | Stored as | Allowed uses |
| --- | --- | --- | --- |
| `numeric` | Fully quantified | `value` required; `reported_value` required | Direct use |
| `nd` | Tested; not detected above detection capability | `value` null, optional `lod` | Detection indicators; censored-data estimators |
| `below_lod` | Detected signal below limit of detection | `value` null, `lod` required | Censored-data estimators; never a zero |
| `below_loq` | Quantified but below reliable quantitation limit | `value` null, `loq` required | Range-bounded value; never a zero |
| `zero` | Explicit zero as printed | `value` = 0.0, flagged for review | Review; chemically implausible for cannabinoids, common ND convention for contaminants |
| `missing` | Source record exists, result blank | `value` null | Exclude; document reason |
| `not_tested` | Analyte absent from the panel | `value` null | Reporting-rate denominator; never a zero |

Decoding from printed strings (`"ND"`, `"<LOD"`, `"<LOQ"`, `"<0.05"`, `"0.0"`, `"not tested"`, blank) is a pure function — `decode_result` — so the same input always maps to the same state, and unrecognized strings are preserved with a note rather than guessed. No substitution routine exists in v1: `LOQ/2`, `LOD/√2`, and zero-replacement are explicit data-product decisions deferred to the future analysis engine, where they must be dataset-labeled.

---

## 6. Normalization rules

### 6.1 Units

| From → To | Rule | Condition |
| --- | --- | --- |
| `% w/w` ↔ `mg/g` | × 10 / ÷ 10 | Same reporting basis |
| `% w/w` ↔ `ug/g` | × 10⁴ / ÷ 10⁴ | Same reporting basis |
| `mg/g` ↔ `ug/g` | × 10³ / ÷ 10³ | Same reporting basis |
| `ppm` ↔ `ug/g` | identity (mass/mass) | Same basis |
| `ppb` ↔ `ug/g` | ÷ 10³ | Same basis |
| `mg/mL` ↔ mass/mass | via density: `value_mass_per_g = value_mass_per_mL / density` | **Verified density (g/mL) required**; flower bulk density is never a valid factor |
| `CFU/mL` ↔ `CFU/g` | via density | Density required |

All mass/mass conversions are exact-factor audited conversions (`convert_unit`); mass/volume conversions raise `DensityRequiredError` without a verified density. `convert_basis` handles dry-weight ↔ as-received and requires `moisture_fraction ∈ [0, 1)`, raising `MoistureRequiredError` otherwise.

### 6.2 What is never normalized together

- GC-underivatized vs LC values for acidic cannabinoids (systematic 40–54% bias);
- dry-weight vs as-received values without moisture;
- different terpene panels (summing a 4-analyte panel against a 39-analyte panel is meaningless);
- different matrices (flower vs concentrate) without method validation;
- mass/mass vs mass/volume without density.

### 6.3 Rounding

Full precision is stored; `round_to_sigfigs(value, sig_figs, rule)` applies half-even / half-up / truncate only at export time.

---

## 7. Comparability grading

`comparability_grade(a, b)` returns `(grade, reasons)` for a pair of measurements, following the laboratory-comparability report §6.2 algorithm:

| Grade | Meaning | Trigger |
| --- | --- | --- |
| **A** | Directly comparable | Same technique, basis (+moisture known), calibration type, PT `|z|<2` both, MU reported, rounding known, same matrix — no reasons |
| **B** | Comparable with documented conversion | Exactly one non-critical difference (e.g. basis differs but moisture is known) |
| **C** | Conditionally comparable | More than one non-critical difference |
| **D** | Not comparable | Any critical reason: underivatized GC vs LC on acidic cannabinoids; `|z| ≥ 3` (ISO 13528) for either lab; moisture unknown for a basis conversion; calibration-type mismatch; terpene-panel overlap < 50% |
| **F** | Incomparable / invalid | Different analyte or different matrix class |

Reason codes are returned alongside the grade so downstream consumers can show *why* (e.g. `moisture_unknown_for_conversion`, `missing_MU`, `terpene_panel_overlap_lt_50`). Grades are pairwise, per-analyte, and versioned: they must be recomputed when PT results, method metadata, or corrections arrive. The engine that aggregates graded subsets (PT-weighted meta-analysis, censored-data estimators, uncertainty propagation) is deferred until real verified batch data exists.

---

## 8. Massachusetts CCC mapping (real-data adapter)

`from_massachusetts_normalized` / `massachusetts_rows_to_record` map the CCC testing CSV rows (as normalized by `scripts/ingest/states/massachusetts.py`) into `AnalyteMeasurement` / `CoaRecord`:

- rows are grouped by Metrc package tag (`METRC SOURCE TAG`) into one provisional record with `report_id = "ma-ccc:<tag>"`;
- `"THC (%) Raw Plant Material"` → compound name `THC`, unit `% w/w`, reported value verbatim (`"1.34"` → `numeric`; `"0.0"` → `zero`, flagged);
- `"THCA (%) Raw Plant Material"` → `cannabinoids/TCBN-0007`; `"Lead (ppm) …"` → `contaminants/TCNT-0007`;
- the CCC CSVs carry **no method, LOD/LOQ, basis, or moisture** — these are recorded as unknown and surfaced as soft warnings, and the batch `basis` stays `unknown` (the CCC's March 2024 guidance recommends as-received reporting for flower, but the CSV itself does not encode basis, so the model does not assume it);
- provisional report ids are legal only for non-verified records; verification requires a canonical `lab-results/TLAB-XXXX` id allocated through the ingest pipeline's `NaturalKeyRegistry` (see `docs/graph/coa-migration.md`).

This adapter is deliberately a thin read-only mapping over the existing state pipeline: it changes nothing in `scripts/ingest/` (merge-sensitive) and consumes only rows the pipeline already normalizes.

---

## 9. Implementation status and open questions

| Deliverable | Status |
| --- | --- |
| Design document | This document |
| JSON Schema v1 | `metadata/coa-measurement.schema.json` |
| Durable model + normalization + grading | `scripts/coa_model.py` (entities, result states, audited unit/basis conversion, display rounding, comparability grading A–F, MA CCC adapter) |
| Tests | `tests/test_coa_model.py` (unit + real-data mapping from the verbatim CCC fixture rows) |
| Migration path for existing demo COA content | `docs/graph/coa-migration.md` |
| Analysis engine (graded pooling, censored-data estimators, uncertainty propagation) | **Deferred** until real verified batch data exists |

Open questions / research gaps:

- `research/cannabis/analytical-chemistry/` is absent from the corpus; method-level detail (derivatization, calibration ranges per lab) must come from primary sources (method validation docs, accreditation scopes, AOAC SMPRs) as real reports are ingested.
- Massachusetts CCC open data does not publish LOD/LOQ, method, or basis; per-analyte limits must be sourced from laboratory method summaries or regulator PT guidance before any `below_lod` / `below_loq` states can be populated for that jurisdiction.
- The comparability criteria in §7 follow the laboratory-comparability research report and ISO 13528; the report's grade table and algorithm are the reference until validated against real proficiency-testing data.
- THC (Δ9-tetrahydrocannabinol) has research exports but no canonical `cannabinoids/TCBN-*` record yet; MA THC measurements therefore map to `compound_id: null` until a record is created by the compound corpus.

---

*Compiled 2026-08-08. Companion documents: `docs/graph/cultivar-chemotype-model.md`, `docs/graph/coa-migration.md`, `docs/graph/coa-examples.md`.*
