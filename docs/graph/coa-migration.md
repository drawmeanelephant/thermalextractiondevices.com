# COA Data Model — Migration Path

**Status:** Plan with a first verified record · **Scope:** how existing Blue Dream / sample COA content is handled, and how real laboratory reports (starting with Massachusetts CCC testing data) enter the durable model.

---

## 1. Current archive state

| Record | Kind | Notes |
| --- | --- | --- |
| `lab-results/TLAB-0001` | demonstration | Sample COA "Buckeye Relief Blue Dream Batch 123" — laboratory, producer, batch id, and all quantitative values are **illustrative sample data**; the page itself carries `includes/demo-sample-record-warning.md` and `includes/unavailable-report-disclosure.md` |
| `products/TPRD-0001` | demonstration | Sample product page for the same demo COA |
| `cultivars/TCUL-0001` | label record | Blue Dream cultivar overview; label, not chemistry |
| `lab-results/TLAB-0002` | **verified** | **First verified COA** — InfiniteCAL (CA) report for Powered By Plants "Dragonberry 750ml (10mg)", batch 250410-37-002; full provenance (official TagLeaf verification URL, PDF sha256, retrieval date, upstream id, parser version). Built by `scripts/coa_verify_example.py`; see `docs/coa-data-model.md` §9.2 |
| `products/TPRD-0002` | **verified** | Product record for the same beverage, linked to TLAB-0002 |
| `testing-laboratories/TSTL-*`, `organizations/TORG-*` | verified | California DCC license-derived records (TLAB-0002 reuses `TSTL-0006` / `TORG-0006`, InfiniteCAL San Diego) |

The `content/lab-results.md` trunk describes the collection as "Archive of verified batch-level Certificates of Analysis" — the first verified satellite (TLAB-0002) now exists alongside the demonstration record, which remains explicitly excluded from derived-layer statistics by the `record_kind` discipline shared with the cultivar chemotype model.

---

## 2. Rules that bound the migration

1. **Synthetic values never migrate into the model.** The demo COA's numbers (8.45 mg/g β-myrcene, 24.20% THCA, …) are sample data. They are **not** converted into `CoaRecord`/`AnalyteMeasurement` instances, and no migration step may copy them into a durable or derived dataset. This is the hard boundary: *fixture or synthetic data must never become publication data.*
2. **IDs are immutable.** `TLAB-0001` stays the demonstration record. When the first verified report arrives it receives a new `lab-results/TLAB-*` id allocated from the next unused number via the ingest pipeline's `NaturalKeyRegistry` — never a renumber or reuse.
3. **The demo record keeps its label.** It remains in `content/lab-results/` as a demonstration record (its `summary` and includes already say so); it is excluded from any analysis by `record_kind`.
4. **No new collections or ID prefixes.** `lab-results` (TLAB) already exists in `scripts/ted_ids.py`; the model maps onto existing collections (see `docs/graph/coa-lab-data-model.md` §2).

---

## 3. Path A — first verified report (any jurisdiction)

> **Status:** exercised once by `lab-results/TLAB-0002` (a real InfiniteCAL CA COA, `scripts/coa_verify_example.py`). The steps below remain the canonical path; the walk-through is a hand-transcribed first pass, so a couple of formalities were simplified (the PDF snapshot lives at its public CDN URL with a recorded sha256 rather than in `var/…`, and no `datasets/TDTS-*` row was created). Full Path A compliance for bulk ingestion should add those two steps.

1. **Ingest the source artifact.** A real COA (PDF/CSV from a laboratory or regulator open-data portal) is captured as an immutable raw snapshot in the state ingest working area (`var/…`), checksummed, and registered in a dated dataset record (`datasets/TDTS-*` pattern).
2. **Allocate identities.** `NaturalKeyRegistry` allocates `lab-results/TLAB-XXXX` (report), reuses or allocates `testing-laboratories/TSTL-*` (laboratory), `organizations/TORG-*` (producer), `products/TPRD-*` (product) where they exist; unknown producers/products stay `null` in the model rather than being invented.
3. **Map measurements.** Each printed analyte row becomes an `AnalyteMeasurement` via `scripts/coa_model.py`: verbatim `reported_value`/`reported_unit`, decoded `state`, normalized `value`/`unit`, per-analyte `lod`/`loq` when the report prints them, and the report's `MethodMetadata` (technique, derivatization, calibration, basis, moisture, rounding, uncertainty) when a method section exists.
4. **Publish the content record.** The verified record is generated into `content/lab-results/` with the closed Boris frontmatter schema (`id`, `title`, `parent`, `status`, `tags`, `relations`, `summary`), relations to the cultivar/product/organization/laboratory records, and the standard provenance footer used by state-ingest pages (official source, retrieval date, checksums, generator, stable entity ID).
5. **Run the gates.** `./bin/validate_graph.sh`, `scripts/ted_ids.py`, the markdown-link and privacy audits, and the full test suite — the same validation path every generated collection uses.

## 4. Path B — Massachusetts CCC bulk testing data (incremental, guarded)

The CCC testing CSVs (`CCC_Testing_Results_2025`, `Testing_Results_2024_…`) are large, real, machine-readable, and batch-resolved via Metrc package tags — the natural first bulk source.

1. **Provenance gate first.** The Massachusetts pipeline is currently fixture-only and merge-blocked; the publication guard (`--fixtures-only` without `--allow-fixture-content` exits 2) means **no** Massachusetts content can be generated until a complete verified live snapshot is ingested. That gate is the migration's first step, not an obstacle to it.
2. **Group by package tag.** `massachusetts_rows_to_record` groups rows by `METRC SOURCE TAG` into provisional records (`report_id = "ma-ccc:<tag>"`, `record_kind = unverified`).
3. **Allocate canonical ids.** Once the snapshot is verified, each provisional record gets a `lab-results/TLAB-XXXX` id; the same tag maps to the same batch, so retests across releases stay linked by `batch_id`.
4. **Honor missing metadata.** The CCC CSVs carry no method, LOD/LOQ, basis, or moisture. Those fields stay `unknown`/null with soft warnings; per-analyte limits and methods must come from laboratory method summaries or regulator PT guidance before `below_lod`/`below_loq` states or Grade A/B comparisons are possible for this jurisdiction.
5. **Stratify honestly.** Lab names in the fixtures are anonymized (`Lab_H`, …); real lab names come from the license registry at live-sync time. Until then, no lab-stratified claims are made.

## 5. Path C — the existing demo COA (`TLAB-0001`)

- **No change to its values or id.** It remains a demonstration record with `record_kind: demonstration` semantics (its includes already state this).
- **Optional, low-risk housekeeping** (only if editors confirm): add an explicit note in the page narrative pointing to `docs/graph/coa-lab-data-model.md` and stating that no verified COA has replaced it yet, and that its tables are not input to any analysis. This is narrative only — no frontmatter keys beyond the closed schema.
- **Retirement path:** when the first verified COA for a real Blue Dream batch exists, the demo stays where it is (IDs are immutable) and the new verified record carries the `verified` kind; consumers filter on `record_kind`, exactly as the chemotype model prescribes.

---

## 6. What this wave does NOT do

- Publishes no COA content (no verified data exists; fixtures must never publish).
- Adds no collections, no id-map rows, and no changes to `scripts/ingest/` (merge-sensitive).
- Builds no analysis engine (clustering, censored estimators, PT-weighted pooling) — those land with real verified batch data.
- Imputes no LOD/LOQ, no zeros, and no method metadata anywhere.

---

*Compiled 2026-08-08. Companion: `docs/graph/coa-lab-data-model.md`, `docs/graph/coa-examples.md`.*
