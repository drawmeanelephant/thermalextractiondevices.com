# Massachusetts CCC Ingestion v2 — Implementation Report

Status: **integrated and published** · Date: 2026-08-09
Generator: `state_ingest-0.1` (schema v1) · Branch: dedicated v2 worktree

## 1. Executive summary

Massachusetts is now the **second serious state adapter** in the repository,
built on the shared `scripts/ingest/` package and coexisting with the existing
California DCC pipeline and content. Real, source-traceable Massachusetts
records were ingested live from the official CCC open-data platform on
2026-08-09 and published as 118 Boris content pages across the canonical
collections. The pipeline preserves measurement semantics (numeric / ND / pass /
fail are never collapsed), protects the corrected 2025 testing release from
silent regression, publishes only allowlisted fields, and regenerates
byte-identically.

## 2. Repository audit (what existed before this task)

The repository already contained a Massachusetts CCC ingestion implementation,
committed at `997139b` ("feat: add Massachusetts CCC state-ingestion pipeline")
and refined at `e4fd49d` (prefix reconciliation). It consisted of:

* Shared ingest package: `scripts/ingest/{core,fetch,storage,schema,diff,ids,markdown,validation}.py`
* State adapter: `scripts/ingest/states/massachusetts.py` (single-file adapter, ~2,400 lines)
* CLI: `scripts/state_ingest.py`
* Tests: `tests/test_massachusetts.py`, `test_state_ingest.py`, `test_live_smoke.py`,
  plus unit tests for every shared module (78 tests at the start of this task)
* Fixtures: `tests/fixtures/massachusetts/` (19 files + `README.md` + `PROVENANCE.md`)
* Docs: `docs/ingest/{audit.md,OPERATOR.md,implementation-report.md}`

The prior implementation was explicitly **test-only**: its own report said
"no Massachusetts content is published" and described the work as blocked on a
reconciliation onto a California-containing `main` that was, at the time,
unreachable from the stale baseline. The audit documents from that period
incorrectly concluded California ingestion did not exist. **On the current
tree, California exists** (commit `3628c641`: `scripts/dcc_ingest.py`,
`scripts/dcc_sync.py`, `data/dcc/`, and committed California collections).

Answers to the audit questions:

1. **Is Massachusetts code already present?** Yes — committed and integrated.
2. **Is it merged or abandoned?** Merged into the current branch's history; it was complete but unexercised (never run live, never published).
3. **Is a shared state ingestion core already present?** Yes — `scripts/ingest/`.
4. **Are Massachusetts tests present?** Yes (89 after this task).
5. **Are Massachusetts fixtures present?** Yes, with provenance labels.
6. **Are any Massachusetts generated pages currently public?** No — none existed before this task.
7. **Are any generated Massachusetts records fixture-derived?** No — the fixture-content hard guard blocks it, and no fixture-derived content was ever committed.
8. **Are any Massachusetts raw or normalized datasets committed?** No — `var/` is gitignored; only small durable records are committed (now, under `data/massachusetts-ccc/`).
9. **Are IDs already reserved or allocated?** Prefixes were registered in `scripts/ted_ids.py`; no `id-map.json` had been persisted.
10. **Retain / rewrite / deprecate?** Retain the shared core and the adapter's domain logic; rewrite the integration seams (ID allocation, trunk handling, duplicate-key policy, source-update provenance, advisory extraction); deprecate the stale audit/report documents.

## 3. Reused code

* `scripts/ingest/` core, fetch, storage, schema, diff, ids, markdown, validation modules — extended, not replaced.
* `scripts/state_ingest.py` CLI — extended with content-tree ID seeding.
* The adapter's dataset catalog, normalizers, aggregators, privacy spec, content writers, and fixture guards.
* All 19 existing fixtures (plus provenance docs).

## 4. Replaced / added code (v2 changes)

* **ID allocation seeding** (`scripts/ingest/ids.py::seed_from_entity_ids`,
  `scripts/state_ingest.py`): the allocator now seeds per-collection counters
  from the combined content tree, so Massachusetts IDs start above California's
  maxima instead of colliding (`TJUR-0001` stays California; Massachusetts is
  `TJUR-0002`, first MA lab `TSTL-0019`, first MA dataset `TDTS-0005`, …).
  This was the single most important v2 fix: the unseeded allocator would have
  written Massachusetts pages over California's `TJUR-0001`, `TDTS-0001`, etc.
* **Trunk preservation** (`_write_trunks`): existing trunk pages are preserved;
  only the missing trunks (`safety-advisories.md`, `affected-products.md`) are
  created, so California/editorial trunk copy is never clobbered.
* **Clobber guard** (`_write_page`): refuses to overwrite a file whose existing
  frontmatter `id` differs from the one being written.
* **Duplicate-key policy** (`scripts/ingest/schema.py`): testing-result datasets
  now warn on partial-key duplicates (the source's columns are not a true
  primary key) and still hard-fail on exact full-row duplicates. The original
  hard-fail made the two large testing datasets uningestable (95 and 5,567
  legitimate partial-key repeats).
* **Stale-source regression guard** (`check_source_staleness`): an incoming
  payload whose HTTP `Last-Modified` is older than the accepted snapshot by
  >30 days fails closed unless the dataset carries a recognized source
  clarification. Together with immutable checksummed snapshots and
  `prior_snapshot_checksum` in the manifest, an obsolete pre-correction 2025
  testing release cannot silently replace the corrected one.
* **Manifest-backed update dates**: `source_last_updated` is now recorded from
  the source file's actual `Last-Modified` header (verified values like
  `Fri, 31 Jul 2026 14:38:21 GMT` for licenses), falling back to the catalog
  annotation.
* **New dataset**: `applications_details` (`l_applications_all_details.csv`,
  1,983 rows) — the one catalog table missing from the original adapter. It is
  heavily PII-laden (EIN/TIN, contacts, addresses), so only aggregate counts by
  license type/status are ever rendered; raw rows never reach content.
* **Advisory extraction** (`parse_advisory_page`): title/date are anchored on
  the page's own `<h1>` (nav/related-post sections no longer leak into them),
  and concern/instruction extracts are bounded to sentence windows (no more
  mid-word fragments).
* **Live smoke suite** (`tests/test_live_smoke.py`): rewritten to actually run
  against the live sources — catalog reachability, every dataset URL, required
  columns, streaming probe for the large testing files, advisory parsing, and
  source-update staleness vs. the committed manifest. The old suite could not
  run (its fetcher rejected the HTML pages it fetched). `Fetcher` gained
  `allow_html` and `probe()` for this.
* **Fixture**: `tests/fixtures/massachusetts/l_applications_all_details.csv`
  (20 redacted rows) so offline tests cover the new dataset.

## 5. Deprecated code

* `docs/ingest/audit.md` and `docs/ingest/implementation-report.md` — their
  conclusions (California unreachable, Massachusetts test-only) describe a stale
  baseline. Both now carry superseded banners pointing at this report.
* Nothing in `scripts/` was deleted; no competing ingestion framework exists.

## 6. Official source inventory (verified live 2026-08-09)

Discovery surfaces fetched: `https://masscannabiscontrol.com/open-data/data-catalog/`,
`…/news/public-health-and-safety-advisories/`, `…/public-documents/regulations/`,
and the testing-data correction notice. The catalog lists **15 downloadable
tables** (all present in the adapter now) plus an Industry-Report section of R
scripts / source data (documented, not directly downloadable via stable URLs).

| Dataset | Official URL (csv) | Source updated (Last-Modified) | Coverage | Format / size | Schema status | Ingested | Published |
| --- | --- | --- | --- | --- | --- | --- | --- |
| licenses | `/resource/l_licenses_all_details_public.csv` | 2026-07-31 | point-in-time | CSV / 479 KB | ok | yes (955 rows) | yes |
| commence_ops | `/resource/l_licenses_commence_ops.csv` | 2026-07-31 | point-in-time | CSV / 394 KB | ok | yes (782) | yes |
| mtc_licenses | `/resource/l_licenses_mtc.csv` | 2026-07-31 | point-in-time | CSV / 55 KB | ok | yes (104) | yes |
| testing_2025 | `/resource/CCC_Testing_Results_2025.csv` | 2026-04-10 | 2025-01-01..11-30 | CSV / 70 MB (streamed) | ok; partial-key dups warn | yes (354,562) | yes |
| testing_2024 | `/resource/Testing_Results_2024_20260415_OpenData.csv` | 2026-04-15 | 2024-01-01..12-31 | CSV / 105 MB (streamed) | ok; partial-key dups warn | yes (440,545) | yes |
| sales_gross | `/resource/a_sales_au_gross.csv` | 2026-07-31 | 2018-… | CSV / 7.6 MB | ok | yes (69,816) | yes |
| sales_deliveries | `/resource/a_sales_au_deliveries.csv` | 2026-07-31 | 2018-… | CSV / 3.7 MB | ok | yes (33,651) | yes |
| price_per_gram | `/resource/a_sales_au_price_per_gram.csv` | 2026-07-31 | 2018-11..2026-06 | CSV / 2 KB | ok | yes (92) | yes |
| mtc_sales | `/resource/a_sales_mtc_gross.csv` | 2026-07-31 | 2018-… | CSV / 5.2 MB | ok | yes (50,203) | yes |
| plant_activity | `/resource/a_sales_au_activityvolume.csv` | 2026-07-31 | 2018-11.. | CSV / 56 KB | ok | yes (825) | yes |
| applications_totals | `/resource/a_applications_all.csv` | 2026-07-31 | point-in-time | CSV / 1 KB | ok | yes (14) | yes |
| applications_dbe | `/resource/a_applications_dbe.csv` | 2026-07-31 | point-in-time | CSV / 0.4 KB | ok | yes (7) | yes |
| applications_details | `/resource/l_applications_all_details.csv` | 2026-08-03 | point-in-time | CSV / 2.0 MB | ok (PII columns excluded) | yes (1,983) | aggregate only |
| agents_gender | `/resource/a_agents_gender.csv` | 2026-07-31 | point-in-time | CSV / 0.1 KB | ok | yes (4) | yes |
| agents_raceethnicity | `/resource/a_agents_raceethnicity.csv` | 2026-07-31 | point-in-time | CSV / 0.4 KB | ok | yes (10) | yes |

The catalog's testing section advertises "Last update: 3/19/2026" (2025) and
"4/15/2026" (2024), matching the correction notice and the file suffix. The
2024 table's "Click here for a data clarification" link is documented on the
Testing Corrections page.

## 7. Data volume

* Downloaded: **193,968,011 bytes (~185 MB)** across 15 datasets; the two
  testing files (70 MB + 105 MB) were streamed to disk, never held in memory.
* Source rows: **953,553**; normalized rows: same (one normalized artifact per
  dataset, checksum-named, in the gitignored working dir; ~202 MB on disk).
* Generated entities: **116** (id-map mappings); generated pages: **118**
  content files across 9 collections plus 2 trunks and the reference page.
* Ignored private fields: see §8.

## 8. Privacy

The source schemas carry substantial PII. Excluded fields (never published,
never retained in committed data): `EIN_TIN`, `FEIN`, `BUSINESS_EMAIL`,
`BUSINESS_PHONE`, `BUSINESS_ADDRESS_1/2`, `MAILING_ADDRESS_1/2`,
`MAILING_CITY/STATE/ZIP`, `ESTABLISHMENT_ADDRESS_1/2`, `ESTABLISHMENT_ZIP`,
agent-name/email columns, `APPROVED_SE_NUMBER`, `EE_PRIORITY_NUMBER_*`,
`RMD_PRIORITY_NUMBER_*`, `FEE_WAIVER_*`, `LIC_FEE_AMOUNT`, `PMT_AMOUNT`,
`LATITUDE`/`LONGITUDE`, and `NOTES/COMMENTS` where it carries reviewer notes.
The privacy gate combines **structured allowlists** (per-entity `public_fields`
in `PRIVACY_SPEC`) with regex scanning (EIN/TIN, email, phone, street address,
coordinates) over generated Markdown. Result: **0 findings** on generated
Massachusetts content, and **0 findings** on the redacted fixtures. Raw local
snapshots retain source fields for fidelity only inside the gitignored
`var/ingest/massachusetts-ccc/`.

## 9. Testing data

| | 2024 release | 2025 release |
| --- | --- | --- |
| Official file | `Testing_Results_2024_20260415_OpenData.csv` | `CCC_Testing_Results_2025.csv` |
| Coverage | 2024-01-01 .. 2024-12-31 | 2025-01-01 .. 2025-11-30 |
| Schema | `Date, METRC ID, …, Test ID, Strain, Lab performing the test, TestCategory, Analyte/Test ID, Result, Quantity, UnitOfMeasure, TestPassed, ProductCategoryTypeName, Notes/comments` | `DATE, METRC ID, METRC SOURCE TAG, ANALYTE/TEST ID, RESULT, TESTPASSED, LAB PERFORMING THE TEST, NOTES/COMMENTS` |
| Rows | 440,545 | 354,562 |
| Analytes | Arsenic, Cadmium, Lead, Mercury, THC, THCA, Total Yeast and Mold (7) | same 7 |
| Status | 437,090 pass / 3,455 fail | 351,346 pass / 3,216 fail |
| Correction notices | File republished 2026-04-15 (suffix) | 2026-03-19/20 correction: Column "F" occasionally carried the package-level status; some passing results appeared failed; **no** failing result was marked pass; numeric values accurate. Verified live on the notice page. |
| Limitation | Labs are anonymized by the Commission (e.g. `Lab_B`); the same package/analyte/lab/value legitimately recurs, so the columns are not a true primary key (partial-key duplicates warn; full-row duplicates fail). | same |

The 2025 corrected release is the current official file (Last-Modified
2026-04-10 > the pre-correction posting). The manifest records raw SHA-256 and
the correction notice; the `check_source_staleness` guard fails closed if an
older copy reappears, and the immutable snapshot store never overwrites an
accepted snapshot. A regression test
(`test_source_staleness_older_copy_fails_closed`) covers the guard.

Measurement semantics are preserved: `RESULT` stays a string in the normalized
artifact with a separate `result_numeric` derived field; blank, `ND`, `<LOD`,
and `<LOQ` are never converted to zero (they are preserved verbatim and simply
fail numeric coercion). `TESTPASSED` is kept verbatim (`True`/`False`).

## 10. Generated entities (counts)

| Entity | Count | Notes |
| --- | --- | --- |
| Jurisdictions | 2 (MA) | `jurisdictions/TJUR-0002` Massachusetts, `TJUR-0003` Data Landscape |
| Licenses | 29 (MA) | 1 overview + 28 advisory-connected licenses (numbers match the tracker) |
| Organizations | 40 (MA) | 10 active ITLs + advisory-connected legal entities (deduplicated by legal name) |
| Testing laboratories | 10 (MA) | The 10 active Independent Testing Laboratories from the current tracker |
| Datasets | 17 (MA) | 9 dataset records + corrections + 3 analyte aggregates + coverage + market + industry-reporting + equity summaries |
| Requirements | 1 (MA) | Testing requirements page (cites 935 CMR 500.160 / 105 CMR 725.100; no numeric action limits republished) |
| Safety advisories | 3 (MA) | The 3 current CCC public health and safety advisories (2025-02-03 ×2, 2025-08-06) |
| Affected products | 5 (MA) | Representative package pages (capped, deterministic selection with cultivar labels) |
| Contaminants | 8 (MA) | THC, THCA, Arsenic, Cadmium, Lead, Mercury, Total Yeast and Mold, Coliforms |
| Reference | 1 (MA) | Privacy & excluded-field specification (`reference/TREF-0004`) |

## 11. Deferred entities (deliberately not modeled)

* **Individual test-result records as pages** — 795k rows are aggregated, never
  one-page-per-result.
* **One page per license** — only advisory-connected licenses and the overview.
* **Cultivar pages from testing `Strain` labels** — reported labels are kept as
  labels (`cultivar-candidates.csv` occurrence report only); no chemistry is
  inferred. The advisory affected-product pages store cultivar text as
  "cultivar candidate" only.
* **Numeric action limits** — not republished; must be confirmed against current
  regulation text (the adapter documents this instead).
* **COA PDFs / product→batch→lab-report chain** — the April 2025 administrative
  order requires ITLs to upload COAs into Metrc, but the CCC open data does not
  expose those COAs publicly; the distinction is documented on the requirements
  page and here, and nothing is fabricated.
* **Per-application detail rows** — PII-laden; aggregate counts only.
* **Industry-report R scripts** — the catalog lists them via an AJAX table with
  no stable direct URL; documented on the industry-reporting page, not fetched.
* **Future analyses** (lab-to-lab, analyte distributions, cultivar-label
  consistency, failure-rate trends) — the normalized layer supports them, but
  none are published in this task.

## 12. Graph relationships

236 pages across the combined tree declare relations; **442 total relation
edges**, including 118 Massachusetts pages. Massachusetts edges connect each
dataset/contaminant/requirement/laboratory/advisory to the Massachusetts
jurisdiction, advisory pages to affected products and contaminants, lab pages
to their organization and the requirements page, and license pages to their
advisory. `validate_relations` reports **0 broken targets**.

## 13. Validation (commands and results)

```bash
python3 -m unittest discover -s tests          # 89 tests OK (5 skipped = live-only)
INGEST_LIVE=1 python3 -m unittest tests.test_live_smoke -v   # 5 tests OK (1 skipped: staleness until manifest existed)
python3 scripts/state_ingest.py massachusetts --skip-publish  # OK: 15 datasets, 116 pages, 0 errors
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl   # validated 284 pages; no files changed
python3 scripts/audit_markdown_links.py content # all local Markdown links resolve
# MA privacy scan (PRIVACY_SPEC over generated collections): 0 findings
# validate_relations(content): 0 broken
SKIP_RELEASE_AUDIT=1 BORIS_BIN=... bash bin/validate_graph.sh   # Boris graph clean; full HTML build; 0 duplicate IDs
SKIP_RELEASE_AUDIT=1 BORIS_BIN=... bash scripts/ted-publish.sh  # site, sitemap, IR, RAG, llms.txt exported
# Determinism: full live re-sync produced byte-identical content (293 files hashed)
# Fixture guard: python3 scripts/state_ingest.py massachusetts --fixtures-only  # exits 2 (refuses)
```

**Pre-existing failure (documented, not a Massachusetts regression):** the
repo-wide public-release audit (`scripts/audit_public_release.py`) reports
blocking PII-001/002 findings on **California's committed `data/dcc/`
license-registry JSON and recall HTML** (added by `3628c64`, ~172k findings).
Massachusetts contributes **zero** findings to that audit (verified:
`data/massachusetts-ccc/` and the MA collections produce no high/medium
findings; the only MA hits are informational REV-001 human-review notices that
also apply to the pre-existing California collections). The build/publish gates
were run with the project's own `SKIP_RELEASE_AUDIT=1` escape hatch (the same
mechanism the deploy workflow uses); resolving the California findings is out of
scope for this task.

**California regression check:** `git diff --name-only -- content/` = **0
files**. No California page, dataset, or ID changed; `metadata/id-map.jsonl`
validates unchanged for the pre-existing 166 records.

## 14. Remaining gaps

* The catalog's Industry-Report R scripts have no stable direct URLs.
* Same-day identical retests can still collide under the partial testing key —
  they warn, and a future release with a stable `Test ID` column (as in 2024)
  can upgrade the key.
* The 2024 vs 2025 testing schemas differ (columns/casing); both are handled,
  and a future drift is caught by the required-column guard.
* `applications_details` date columns use a JS timestamp format that is not
  parsed as dates (avoided by not declaring them); a future migration could add
  a dedicated parser.
* The concern/instruction text on advisory pages is extracted to sentence
  boundaries from the article body — good but still a heuristic; manual review
  of the three live notices is recommended before any advisory is treated as a
  legal record.
* Numeric action limits remain unpublished pending a regulatory-text pass.
