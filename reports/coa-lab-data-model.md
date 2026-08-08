# COA & Laboratory Data Model — Agent Report

**Branch:** `freebuff/make-sure-you-have-newest-git-ce493edf-ebeb-4800-9ba7-3ae55afabea1` (Freebuff worktree; mission branch `agent/coa-lab-data-model` does not exist in any reachable ref — see Validation Results §3)
**Base:** `7b02922` (`github/main`, newest available; fast-forwarded from `62dc890` at start of wave per the "newest git" instruction)
**Date:** 2026-08-08

## Summary

Established the durable COA & laboratory measurement model: the archive-facing data layer for laboratory reports and analyte measurements (producer → product → batch/lot/package → laboratory → report → analyte measurements). The model preserves reported values verbatim, keeps `ND` / `<LOQ` / `<LOD` / `0` / `missing` / `not tested` as distinct, non-collapsible states, audits every unit/basis conversion, and grades cross-lab comparability A–F. It is the measurement-level extension of the cultivar chemotype model (`docs/graph/cultivar-chemotype-model.md`), which remains the derived profile layer.

No content pages, collections, or id-map rows were added: the durable model is schema + implementation + tests + documentation, consistent with the repository rule that fixture or synthetic data must never become publication data (no verified COA exists in the archive yet).

## Files added

| File | Purpose |
| --- | --- |
| `scripts/coa_model.py` | Durable model: result states, unit/basis normalization with conversion audits, display rounding, record validation, comparability grading A–F, Massachusetts CCC adapter |
| `metadata/coa-measurement.schema.json` | JSON Schema v1 (draft-07) for the measurement layer, mirroring `metadata/cultivar-batch-profile.schema.json` conventions |
| `docs/graph/coa-lab-data-model.md` | Architecture & schema design document |
| `docs/graph/coa-migration.md` | Migration path for the existing Blue Dream / sample COA content and for future state-data ingestion (MA CCC bulk path) |
| `docs/graph/coa-examples.md` | Representative real-data examples derived from the verbatim CCC 2025 fixture rows, with provenance |
| `tests/test_coa_model.py` | 37 unit tests (1 skipped: `jsonschema` not installed): state distinctness, unit/basis conversions, rounding, record validation, comparability grades, real-data MA mapping, schema consistency |
| `reports/coa-lab-data-model.md` | This report |

## Files modified

None. `scripts/ingest/` (merge-sensitive state pipeline), `metadata/id-map.jsonl`, `scripts/ted_ids.py`, and all content were intentionally untouched.

## Entities created

None in the Boris graph. The model defines entity types (Report, Batch, Laboratory, AnalyteMeasurement, MethodMetadata) and entity-ID contracts (`lab-results/TLAB-*`, `testing-laboratories/TSTL-*`, `organizations/TORG-*`, `products/TPRD-*`, `cannabinoids/TCBN-*`, `terpenes/TTRP-*`, `contaminants/TCNT-*`) that map onto existing collections; no new collection or ID prefix is required.

## Graph relationships created

None (no content pages). The design doc (§2, §3.1 of the chemotype companion) specifies the relation vocabulary the model expects on real records: batch → report (`report_id`), report → laboratory, batch → producer/product/cultivar, measurement → compound entity.

## Primary sources verified

- **USDA Laboratory Testing Guidelines** (dry-weight basis, measurement-of-uncertainty reporting) — cited in the laboratory-comparability report and reflected in the basis/MU model fields.
- **Massachusetts CCC Letter (2024-03-08)** — as-received reporting recommendation for flower; the model records `basis: unknown` for CCC data because the CSV does not encode basis, and flags the policy note rather than assuming it.
- **Massachusetts CCC Open Data** — `CCC_Testing_Results_2025` dataset (real rows used for the adapter examples; provenance in `tests/fixtures/massachusetts/PROVENANCE.md`).
- **ISO 13528** — |z| ≥ 3 unsatisfactory PT performance, used as the Grade-D threshold (via the laboratory-comparability report).
- AOAC SMPR 2019.003, NY OCM laboratory quality standards, Mississippi significant-figure guidance, WSLCB CSWG recommendations — referenced by the research report; per mission rule 7/8, these remain research-report-sourced claims (see unresolved §1) until the source ledger is walked to the primary documents.

## Uncertain claims left unresolved

1. **Analytical-chemistry research input absent.** `research/cannabis/analytical-chemistry/` (named in the task brief) does not exist in the corpus; method-level guidance was taken from `laboratory-comparability`. Flagged as a research gap in the design doc §9.
2. **Comparability criteria provenance.** The A–F grade table/algorithm follow the laboratory-comparability research report §6.2 and ISO 13528. The report itself is a Perplexity synthesis; per mission rule 7, the grade criteria should be re-verified against primary sources (NY/MA/CO method-validation guidance, AOAC SMPRs) before the grading engine gates real pooling.
3. **CCC data lacks method/LOD/LOQ/basis.** These are recorded as unknown with soft warnings; per-analyte limits must come from laboratory method summaries or regulator PT guidance before `below_lod`/`below_loq` states can be populated for MA.
4. **THC has no canonical record.** `Δ9-Tetrahydrocannabinol (THC)` has research exports but no `cannabinoids/TCBN-*` record; MA THC measurements map to `compound_id: null` until the compound corpus creates one.
5. **Arsenic/Cadmium/Mercury/yeast-mold lack canonical records.** Only Lead maps to `contaminants/TCNT-0007`.
6. **Zero-vs-ND convention for contaminants.** The CCC prints `0.0` for heavy metals and yeast/mold; the model flags these as `zero` (review) and documents that it is a common ND reporting convention, but the exact regulatory interpretation is left to the regulator's guidance.

## Validation results

1. **Full test suite** — `python3 -m unittest discover -s tests -t .` → **139 tests, OK (4 skipped**: 3 network live-smoke + 1 `jsonschema`-not-installed).
2. **New model tests** — `python3 -m unittest tests.test_coa_model` → 37 tests, OK (1 skipped).
3. **ID policy** — `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl` → unchanged content; no new IDs (no content changes).
4. **Git state** — worktree fast-forwarded `62dc890 → 7b02922` (`--ff-only`) so work is based on the newest `main`; working tree clean except the intended new files and the untracked `research/` symlink (untracked research corpus from the main worktree; never staged).
5. **Fixture/publication guard** — no fixture or synthetic row was used outside tests/docs examples; the 11 synthetic rows in the 2024 MA fixture (including the fabricated "Blue Dream" potency rows) are explicitly excluded and documented as such in `docs/graph/coa-examples.md`.
6. **Boris graph validation** — `BORIS_BIN=bin/boris ./bin/validate_graph.sh`: ted_ids validated 182 pages (no changes), Boris graph diagnostics passed (baseline diagnostics; parent edges valid), and the full Cantilever publication compiled with all markdown links resolving. The final public-release audit step (`audit_public_release.py`) reports blocking findings, but every finding is on **pre-existing base-state files** (`data/dcc/*` license-registry PII, `content/devices|manufacturers/*`, `scripts/dcc_ingest.py`, `tests/fixtures/massachusetts/*`, git history, `docs/audit-config.json`); a full JSON report run confirms **zero findings reference any file added by this wave** (`scripts/coa_model.py`, `metadata/coa-measurement.schema.json`, `docs/graph/coa-*.md`, `tests/test_coa_model.py`, `reports/coa-lab-data-model.md`). This wave adds no content pages, so the graph itself is untouched.

## Research corpus records consumed

- `research/cannabis/laboratory-comparability/source/2026-08-08-perplexity.md` — primary input (metadata §3, normalization §4, comparability §6)
- `research/cannabis/batch-variability/source/2026-08-08-perplexity.md` — batch-to-batch variability as expected state, not error
- `research/cannabis/chemotype-analysis/source/2026-08-08-perplexity.md` — companion cultivar chemistry context
- `research/jurisdictions/united-states/national-data-surveys/artifact.md` + source — cross-state batch-resolved data landscape (NV/ME/NY/VT paths for future bulk ingestion)
- `research/_index/manifest.jsonl`, `research/_index/inventory.md` — corpus index (noted `analytical-chemistry` gap)
- Sibling model for convention alignment: `docs/graph/cultivar-chemotype-model.md`, `metadata/cultivar-batch-profile.schema.json`, `scripts/cultivar_profiles.py`, `tests/test_cultivar_profiles.py`

## Suggested next work

1. Create a canonical `cannabinoids/TCBN-*` record for Δ9-THC and contaminant records for the remaining MA analytes so MA measurements map to entity ids.
2. First verified COA ingest (Path A in the migration doc): allocate `lab-results/TLAB-*` via the NaturalKeyRegistry, publish under the closed Boris schema, and run the full validation/publish gates.
3. Live Massachusetts sync (Path B) once the reconciliation gate is unblocked: group by Metrc package tag, allocate canonical ids, and surface per-analyte LOD/LOQ from regulator PT guidance.
4. Walk the comparability-grade criteria back to primary sources (NY/MA/CO guidance, AOAC SMPRs) before the grading engine gates real pooling.
5. Build the analysis engine (graded pooling, censored-data estimators, uncertainty propagation) only when verified batch data exists (n ≥ 30 per label per the chemotype model's guidance).
