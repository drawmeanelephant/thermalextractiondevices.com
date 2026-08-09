# Jurisdiction Pipeline Audit — Repository State

Status: **completed** · Date: 2026-08-09 · Scope: full repository audit ahead of the
jurisdiction research pipeline build-out (Steps 1–10 of the state-cannabis mission).

This audit documents what already exists, what is reusable, what is state-specific,
what is missing, what should **not** be generalized, and the collision/duplication
risks in the current architecture. It is the input to every later step; no
refactoring was performed except the minimal safety fix required to run the
Massachusetts live sync without corrupting California records (documented in
§7 and in `docs/jurisdiction-evidence-model.md`).

---

## 1. Repository identity

`thermalextractiondevices.com` is a production **Boris** static-site archive
(Zig compiler, `afterparty` branch, pinned commit `9505ec6`; provisioned by
`scripts/ensure-boris.sh`), deployed to Cloudflare Pages. Content lives in
`content/` as Markdown with a **closed frontmatter schema**
(`id, title, parent, status, tags, relations`). Entity IDs follow
`<collection>/<PREFIX>-NNNN` (policy in `metadata/id-policy.json`, enforced by
`scripts/ted_ids.py`). Build/validation gates: `bin/validate_graph.sh`
(→ `ted_ids.py` → `boris check` → `ted-build.sh` → HTML ID audit).

Git history relevant to this mission (newest first):

| Commit | Meaning |
| --- | --- |
| `62dc890` | content: add device corpus wave 1 (HEAD) |
| `f1573f4` | fix: skip release audits during deploy/preview build |
| `ebed39d` | fix: table row highlight contrast (theme) |
| `e4fd49d` | reconcile `testing-laboratories`/`datasets` prefixes to TSTL/TDTS |
| `4b60a29` | merge `source-reliability-hardening` into integration |
| `4bd916b` | merge Massachusetts CCC pipeline branch into integration |
| `9fc5052` | harden source reliability: replace placeholders, label demos |
| `5094c54` | public-release readiness tooling and repository policy |
| `997139b` | Massachusetts CCC state-ingestion pipeline |
| `2ad7d56` | automated Boris compiler resolution/provisioning |
| `3628c64` | **California DCC ingestion workflow** (licenses, labs, recalls, contaminants, datasets) |
| `d9018c9` | Content Truck 01 (cultivars, references, guides, includes) |
| … | earlier editorial/theme/infra work |

**Bottom line:** both California and Massachusetts implementations exist and are
merged. California was implemented first as a monolithic script
(`scripts/dcc_ingest.py`); Massachusetts was implemented second as a
package-based reference adapter (`scripts/ingest/` + `scripts/state_ingest.py`).
The two pipelines are **not yet unified**, and Massachusetts has **no durable
data or generated content in this worktree** (adapter + tests only).

---

## 2. A. What already exists

### 2.1 California (DCC) — implemented and committed

Pipeline: `scripts/dcc_ingest.py` (monolithic, v0.1.0-poc, schema 1.0).
Caches live API payloads to `data/dcc/cache/` (gitignored); archives immutable
dated snapshots to `data/dcc/<dataset>/<YYYY-MM-DD>/`; writes Boris content;
verifies; publishes. `scripts/dcc_sync.py` is a **legacy segmenting variant**
(license-registry subsets → law-and-use pages) still referenced by
`content/law-and-use.md` prose but **not** invoked by `dcc_ingest.py`.

Committed artifacts (`data/dcc/`, retrieved 2026-08-04, all checksummed):

| Dataset | Records | Status |
| --- | --- | --- |
| `license-registry` | 20,821 licenses | synced |
| `testing-labs` | 18 active testing laboratories | synced |
| `recalls-index` | 181 recall notices | synced |
| `recalls-details` | 6 representative details | synced |
| `requirements` | curated panel + citations | synced |
| `harvest`, `monthly-sales` | raw Looker Studio embeds only | unstable / aggregate-only |

Generated content (all under `content/`, provenance blocks on every page):

* `jurisdictions/TJUR-0001` — California jurisdiction profile.
* `licenses/TLIC-0001` — aggregate license counts by status/type.
* `datasets/TDTS-0001..0004` — license-registry dataset record, harvest,
  monthly-sales (aggregate-only), data landscape.
* `requirements/TREQ-0001` — mandatory testing panel (8 categories) + citations.
* `testing-laboratories/TSTL-0001..0018` — one page per active lab (license
  identity + premises + org link).
* `recalls/TRCL-0001..0006` — six representative recall detail pages plus a full
  official index trunk (`content/recalls.md`, 181 rows).
* `organizations/TORG-0001..0022` — legal entities from lab + recall records.
* `contaminants/TCNT-0001..0008` — curated contaminant pages (pyrethrins,
  aflatoxins, ochratoxin A, STEC, salmonella, aspergillus, lead, residual
  solvents).
* `law-and-use/TLAW-0001..0009` — editorial licensing law pages (referencing
  `dcc_sync.py`).

### 2.2 Massachusetts (CCC) — implemented, not yet materialized here

Pipeline: `scripts/state_ingest.py` + `scripts/ingest/` package + state adapter
`scripts/ingest/states/massachusetts.py`. This is the **reference architecture**:
fetch → immutable raw snapshot (SHA-256) → schema guards → normalize → aggregate
→ generate Boris content → publication gates (privacy scan, relation targets,
ID audit, Markdown links, Boris build). Durable records would live under
`data/massachusetts-ccc/` (manifest, id-map, source-catalog, schema-report,
privacy-spec, affected-packages.csv, cultivar-candidates.csv, sync-reports).

Dataset catalog defined in the adapter (all URLs verified 2026-08-05):

* `licenses`, `commence_ops`, `mtc_licenses` — CCC license tracker.
* `testing_2025` (CCC_Testing_Results_2025, ~70 MB) and `testing_2024`
  (Testing_Results_2024_20260415_OpenData, ~100 MB) — test results with
  **anonymized labs**; streamed, never loaded fully into memory.
* `sales_gross`, `sales_deliveries`, `mtc_sales`, `price_per_gram`,
  `plant_activity` — market data.
* `applications_totals`, `applications_dbe`, `agents_gender`,
  `agents_raceethnicity` — equity/applications aggregates.
* Advisories portal — public health and safety advisories (3 published as of
  2026-08-05), parsed into structured records; products + licensees extracted.

Tests: `tests/` — 78 tests, all passing (3 network smoke tests skipped).
Fixtures: `tests/fixtures/massachusetts/` — schema-faithful, privacy-scrubbed,
labeled verbatim/redacted/synthetic in `PROVENANCE.md`.

**Not present in this worktree:** `data/massachusetts-ccc/` (no durable records)
and any Massachusetts content under `content/` (no MA jurisdiction, dataset,
license, lab, advisory, or affected-product pages). The MA pipeline has never
been run live in this tree.

### 2.3 Shared editorial collections (pre-dating both pipelines)

Hand-authored, evidence-structured: `content/terpenes/` (12 terpene records
with NIST sources), `content/cultivars/` (9 cultivar overview pages — all
awaiting verified COAs except the labeled Blue Dream **demonstration**),
`content/botanicals/`, `content/devices/`, `content/manufacturers/`,
`content/lab-results/` (1 **demonstration** COA, `TLAB-0001`),
`content/products/` (1 demonstration product, `TPRD-0001`),
`content/includes/` (provenance/claim warning includes), `content/safety/`,
`content/specs/`, `content/reference/`, `content/guides/`, `content/releases/`,
`content/changelog/`, `content/law-and-use/`.

### 2.4 Trunks

Collection landing pages exist at `content/<collection>.md` for: jurisdictions,
licenses, organizations, testing-laboratories, recalls, contaminants, datasets,
requirements (generated by the CA pipeline / integration), plus the editorial
collections. Trunks are generally **generic** (collection-level), except
`content/recalls.md`, which is a CA-specific full index (181 rows).

---

## 3. B. What is reusable

1. **Shared ingest package** (`scripts/ingest/`): `core.py` (dates, change
   reports, errors), `fetch.py` (Fetcher + FixtureFetcher, content-type guards),
   `storage.py` (ArtifactStore: immutable SHA-256 snapshots, manifest),
   `schema.py` (SchemaSpec guards: required columns, types, row collapse,
   duplicate keys, date regression), `diff.py` (snapshot comparison),
   `ids.py` (NaturalKeyRegistry: stable natural-key → Boris ID with tamper
   digest), `markdown.py` (frontmatter/table/callout/wikilink renderers),
   `validation.py` (privacy allowlists, relation-target validation). **All of it
   is regulator-agnostic and directly reusable by future states.**
2. **ID tooling**: `scripts/ted_ids.py` — prefix table per collection, form-ID
   normalization, collision detection. `metadata/id-policy.json`.
3. **Gates**: `bin/validate_graph.sh`, `scripts/audit_markdown_links.py`,
   `scripts/ted-build.sh`, `scripts/ted-publish.sh`.
4. **CA archived data**: 20,821-license registry (entity-resolution raw
   material), 18 active labs, 181 recalls — all checksummed with provenance.
5. **Editorial evidence conventions**: includes (demo-sample-record-warning,
   cultivar-identity-warning, first-party-provenance-warning, etc.), the
   cultivar-candidate discipline (raw text preserved; no lineage fabrication),
   the analyte normalization already present in the MA adapter
   (`parse_analyte`, `normalize_testing_common`).
6. **Privacy discipline**: PRIVACY_SPEC allowlists; raw coordinates/EIN/email/
   phone/street addresses never published; fixture scrubbing.
7. **Provenance block convention**: every generated page carries official
   source, retrieval date, data-through date, generator + schema version,
   stable entity ID.

---

## 4. C. What is California-specific

* `scripts/dcc_ingest.py` endpoint knowledge: `CANNA_API`
  (`as-dcc-pub-cann-w-p-002.azurewebsites.net`), `recalls.cannabis.ca.gov`,
  Looker Studio dashboard embeds, `search.cannabis.ca.gov` config discovery.
* `content/recalls.md` full index (CA-only collection; MA uses
  "safety-advisories" terminology and does **not** relabel advisories as
  recalls).
* CA license registry schema fields (license_designation, authority_id=BCC/CCL/
  MCSB, parcel_number, premise lat/long, business_owner string).
* MAUCRSA / Business & Professions Code §§ 26000 et seq. citations; CCR Title 4
  Division 42 citations; the 8-category mandatory testing panel as CA defines it.
* The `dcc_sync.py` segmenting workflow and `content/law-and-use/TLAW-*` pages.
* `data/dcc/<dataset>/<date>/` archival layout (dated dirs) — MA uses a
  SHA-256-keyed layout instead. Both are valid; neither is generalized yet.

## 5. D. What is Massachusetts-specific

* Adapter catalog: CCC `masscannabiscontrol.com/resource/<slug>.csv|.json`
  downloads, advisories portal URLs, the 2024/2025 testing-file schema
  differences (casing/columns), anonymized lab column.
* Terminology preservation: **public health and safety advisory** (never
  relabeled "recall"); **potentially contaminated** vs **contaminated**;
  affected products / destruction or return.
* License tracker fields (LICENSE_NUMBER, COMMENCE_OPS, CULTIVATION_TIER, MTC
  rows with raw coordinates excluded).
* `tests/fixtures/massachusetts/` fixtures and PROVENANCE labels.
* MA page-generation policy: one page per active ITL, advisory-connected
  licensees, representative affected products (capped); no per-license pages.

## 6. E. What is missing

1. **Unified jurisdiction model**: jurisdiction/regulator/statute/license-type/
   DBA/brand/parent-company/facility/batch/package/COA/analyte entities have no
   shared schema or IDs across states (CA uses its own scan-and-assign; MA uses
   NaturalKeyRegistry with no cross-state awareness).
2. **Source manifest system**: no reusable, jurisdiction-parametric source
   registry (MA has `source-catalog.json` output; CA has hardcoded URLs in
   `dcc_ingest.py`). No stubs for the other 48 states.
3. **Regulatory/limits data**: CA `TREQ-0001` lists the panel but deliberately
   omits numeric action limits; MA requirements page omits them too. No
   structured analyte→limit→citation→effective-date dataset exists anywhere.
4. **Entity resolution layer**: no duplicate/renamed/shared-address/multi-DBA/
   multi-license-per-premises/transfer/parent-company exception reports.
5. **Lab registry beyond license fields**: no accreditation (ISO/IEC 17025,
   A2LA/PJLA), no website/COA-verification-portal fields, no closure/suspension
   history.
6. **COA pipeline**: no COA source discovery reports, no raw COA artifacts, no
   parser, no normalized COA/analyte evidence records, no relationship graph
   (COA→lab→batch→product→brand→cultivar).
7. **Products/batches/COAs for either state**: `content/products/` and
   `content/lab-results/` contain only the labeled Blue Dream **demonstration**
   records; no real producer product or batch records.
8. **Knowledge summaries**: no "market participants vs COA corpus" distinction,
   no batches-by-lab / by-producer / by-cultivar queries, no terpene/
   cannabinoid distributions, no contaminant-failure summaries.
9. **MA durable data**: `data/massachusetts-ccc/` absent in this worktree.
10. **Stable seed of the shared ID registry across states**: MA id-map.json
    would allocate `TJUR-0001` for Massachusetts and collide with California
    (fix landed as part of this pass — see §7/§10).

## 7. F. What should NOT be generalized

* **State terminology**: "recall" (CA) vs "public health and safety advisory"
  (MA); license class names; testing-file layouts. Forcing one vocabulary flattens
  jurisdiction-specific differences the mission explicitly wants preserved.
* **CA's `dcc_ingest.py` implementation style** (global mutable guards,
  dated-dir archives, cache dir) — new states should follow the package
  architecture; CA may be migrated later, but migrating it *now* risks
  regressing a working, merged pipeline.
* **Anonymized lab columns**: MA testing files anonymize the lab; CA lab pages
  carry license identity. Do not merge these into one "lab" fact.
* **The demonstration COAs/products** (`TLAB-0001`, `TPRD-0001`): must never be
  counted as real evidence (guard already enforced by includes + policy).
* **Cultivar→genetics inference** from strain strings on COAs/advisories
  (already honored; must stay honored).
* **Numeric action limits** until verified against current regulation text with
  citations (both pipelines currently refuse to emit them — that discipline
  stays; Step 4 adds verified values with citations instead of guesses).
* **Privacy exclusions** (EIN, emails, phones, street addresses, coordinates):
  apply to every state regardless of architecture.

## 8. G. Obvious schema collisions and duplication risks

| # | Risk | Detail | Mitigation in this pass |
| --- | --- | --- | --- |
| 1 | **Entity-ID collision across states** | MA `NaturalKeyRegistry` with an empty `data/massachusetts-ccc/id-map.json` allocates `jurisdictions/TJUR-0001` (Massachusetts), colliding with California's `TJUR-0001`; same for every shared collection prefix (TLIC, TSTL, TDTS, TREQ, TCNT, TORG…). | Seed the registry from existing content form IDs per collection before allocation (shared `ids.py` change + test). |
| 2 | **Trunk overwrite** | MA `_write_trunks()` unconditionally rewrites `content/<collection>.md` for 9 shared collections; CA `ensure_trunks()` only creates-if-missing. Running MA sync would clobber CA trunk text. | Make trunk writes create-if-missing and state-neutral; MA trunk prose no longer hardcodes `TJUR-0001` or "Massachusetts" into shared trunks. |
| 3 | **Hardcoded MA→CA ID reference** | MA trunk template referenced `[[jurisdictions/TJUR-0001|Massachusetts]]` — would link the MA trunk to California's page. | Fixed to use the actual MA jurisdiction entity ID (allocated after CA's). |
| 4 | **Two ID allocators** | CA `dcc_ingest.assign_ids()` scans content; MA uses `NaturalKeyRegistry`. Both produce `PREFIX-NNNN`, but neither knows about the other's allocation. | Seed-from-content (fix #1) makes them coexist; a single allocator is a future consolidation item. |
| 5 | **Duplicate collection semantics** | `recalls` (CA) vs `safety-advisories`+`affected-products` (MA) express the same domain with different granularity. | Documented as intentional; relationship layer maps `advisory → affected product → package` without renaming either state's terms. |
| 6 | **`dcc_sync.py` vs `dcc_ingest.py`** | Two CA scripts; `law-and-use.md` references `dcc_sync.py` while `dcc_ingest.py` is the active pipeline. | Flagged for deprecation/consolidation; no change made (out of scope). |
| 7 | **Testing data natural keys** | MA `key_columns=(date, metrc, analyte, lab, result)` can collide on same-day identical retests. | Already flagged in `docs/ingest/implementation-report.md`; verified against first live sync (this pass). |
| 8 | **CA recalls dataset growth** | `data/dcc/recalls-index` archives 31 HTML pages per run; cache dir holds full payloads. Not a collision but a size/duplication concern. | Leave as-is; archive policy noted for wave-next. |
| 9 | **Strain-string normalization** | MA cultivar-candidates.csv normalizes strain text; CA recalls carry cultivar strings in titles. Two different normalization paths for the same concept. | COA evidence model (Step 2) and relationship layer (Step 9) define one raw→candidate policy with confidence; existing artifacts stay untouched. |

---

## 9. Conventions summary (for later steps)

* **IDs**: `<collection>/<PREFIX>-NNNN`; prefixes in `scripts/ted_ids.py`
  (`DEFAULT_PREFIX`); 4-digit numeric segment; never silently renumber.
* **Frontmatter**: only `id, title, parent, status, tags, relations`;
  relations as `relates_to=<entity-id>` lists; unquoted id.
* **Provenance block**: official source URL, jurisdiction, retrieval date,
  data-through date, source-data caveat, record status, generator + schema
  version, stable entity ID.
* **Raw preservation**: raw snapshots immutable by SHA-256 (MA) or dated dir
  (CA); normalized artifacts never overwrite raw; `*_raw` values retained.
* **Fixtures**: `tests/fixtures/<state>/` with PROVENANCE.md labels
  (verbatim / redacted / synthetic / handcrafted).
* **Publication gates**: privacy scan → relation targets → `ted_ids.py` →
  Markdown link audit → Boris graph + full build. Fail closed.
* **Generated vs editorial**: generated pages carry `Generator:` in provenance;
  editorial pages carry none. `metadata/id-map.jsonl` records editorial IDs;
  state id-maps live in `data/<state>-ccc/id-map.json`.

## 10. Minimal safety fix applied this pass

Before the first live Massachusetts sync could run against a tree that already
contains California records, three changes were required (all additive, all
covered by new tests):

1. `scripts/ingest/ids.py` — `NaturalKeyRegistry` can now be seeded with
   already-used form IDs (from existing content) so allocation continues after
   California's IDs instead of colliding.
2. `scripts/ingest/states/massachusetts.py` — `_write_trunks()` now
   create-if-missing and state-neutral; the hardcoded `TJUR-0001` reference was
   replaced with the actual Massachusetts jurisdiction entity ID.
3. `scripts/state_ingest.py` — MA runs seed the registry from
   `content/<collection>/` before allocating.

See `docs/jurisdiction-evidence-model.md` (Step 2) for the evidence model that
this audit's findings drive, and `reports/jurisdiction-wave-next.md` for the
full wave summary.

---

## 11. Addendum — reconciliation with upstream (2026-08-09, PR time)

This audit was written against commit `62dc890`. Before this branch could be
opened, upstream `main` advanced 119 commits and independently landed most of
what §2.2 and §6 marked "missing": the Massachusetts CCC pipeline was run live
(durable records in `data/massachusetts-ccc/`, generated content pages,
`TJUR-0022` as the Massachusetts jurisdiction ID, `TREF-0005` privacy spec),
and the California pipeline was reworked so raw payloads stay in private
unpublished storage (`storage: "private-unpublished"` with checksums in the
manifest) rather than committed dated archives — which supersedes the
redaction-in-place approach this worktree had started.

The reconciliation decisions for this PR:

* **Adopt upstream as canonical** for everything it already materialized
  (MA content and data store, CA storage policy, ID seeding in `ids.py` /
  `state_ingest.py`, `fetch.py` HTML support via `allow_html`, advisory
  parsing, `ted_ids.py` ID preservation, audit-config allowlists).
* **Carry forward what upstream still lacks** — the artifacts of this pass:
  this audit report, `docs/jurisdiction-evidence-model.md` (Step 2),
  `scripts/ingest/evidence.py` + tests, the source-manifest system
  (`scripts/ingest/sources.py`, `scripts/source_manifest.py`, tests,
  `data/source-manifests/` incl. CA + MA manifests and 49 state stubs —
  Step 3), and the normalized testing-requirements datasets with citations
  (`scripts/ingest/testing_requirements.py`, `scripts/testing_requirements.py`,
  `data/testing-requirements/` — Step 4).
* **One behavioral fix**: the MA testing-dataset natural keys (§8 risk 7)
  now include `METRC SOURCE TAG` + `NOTES/COMMENTS` (2025) and
  `METRC source tag` + `Test ID` (2024), making them true primary keys that
  fail closed; upstream's `duplicate_key_policy="warn"` masked the same
  collisions on legitimate distinct rows.
