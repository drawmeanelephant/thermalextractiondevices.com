# Massachusetts CCC Ingestion — Implementation Report

Status: **implemented (test-only) · not integrated** · Date: 2026-08-05
Generator: `state_ingest-0.1` (schema v1)

## 0. Executive summary

The Massachusetts CCC ingestion pipeline (shared package + state adapter +
CLI + fixture tests) is implemented and fully validated **as a test-only
capability**. No Massachusetts content is published in this repository, and
none can be until (a) the reconciliation rebase onto the California-containing
`main` completes and (b) a complete verified live snapshot is ingested.

The reconciliation requested by the maintainer **could not be executed**: the
California DCC commit `3628c641af3d262825b11b0baa4db7a304556356` is not
reachable in this environment (evidence in §1). Rather than fabricate a
California implementation, all work is preserved uncommitted and the
boundaries are restored.

## 1. Baseline evidence (stale vs. real main)

* Worktree base (`HEAD`): `2ad7d56` "feat: add automated Boris compiler
  resolution and provisioning system".
* `origin/main` resolves to the same `2ad7d56`; `git log 2ad7d56..origin/main`
  is empty — our base **is** current `origin/main` as visible from this
  repository.
* `git rev-list --all | grep 3628c641` → **0 hits**; `git cat-file -t
  3628c641…` → fatal "could not get object info". The commit is not in this
  repository's object store.
* All four agent branches (`origin/agent-1..4`) point at `2ad7d56` — no
  California work in any reachable ref.
* `git ls-remote origin` → `fatal: '.../thermalextractiondevices.com/.'
  does not appear to be a git repository`. The `origin` path (the maintainer's
  main checkout) is outside the sandbox; direct inspection returns
  "Operation not permitted".

Conclusion: the California-containing `main` is **not obtainable from this
worktree**. A rebase or replay cannot be performed on data we cannot read, and
no California behavior was assumed, cloned, or fabricated. §2 below states the
reconciliation work that remains once the commit is reachable.

## 2. Remaining reconciliation (blocked)

Once `3628c641` (or current `main`) is reachable, the required pass is:

1. Rebase/replay these uncommitted changes onto `main`.
2. Reconcile the shared ingestion architecture: migrate or preserve the
   California `dcc_ingest.py`/`dcc_sync.py` pipeline as documented in the
   original task; verify California regression fixtures; unify stable ID
   allocation across states; agree on one canonical CLI; explicitly deprecate
   obsolete scripts.
3. Revalidate IDs/relations against the combined tree (no collisions, stable
   natural-key reuse, no dangling relations, deterministic regeneration).
4. Re-run the complete combined validation and publish surfaces.

## 3. Files added

* `scripts/ingest/` — shared package: `core.py`, `fetch.py`, `storage.py`,
  `schema.py`, `diff.py`, `ids.py`, `markdown.py`, `validation.py`,
  `states/massachusetts.py`, `__init__.py`.
* `scripts/state_ingest.py` — canonical CLI (flags: `--refresh`,
  `--dataset`, `--artifacts-dir`, `--skip-content`, `--skip-publish`,
  `--fixtures-only`, `--report-only`, `--quiet`, `--allow-fixture-content`).
* `tests/` — 78 tests across 10 modules + `tests/fixtures/massachusetts/`
  (19 fixtures + `README.md` + `PROVENANCE.md`).
* `docs/ingest/` — `audit.md`, `OPERATOR.md`, this report.

## 4. Files modified

* `scripts/ted_ids.py` — added collection prefixes for the Massachusetts
  collections (`TJUR`, `TLIC`, `TORG`, `TSTL`, `TCNT`, `TDTS`, `TREQ`,
  `TSAD`, `TAFP`). **Merge-sensitive**: California `main` may carry its own
  `ted_ids.py` changes that must be reconciled.
* `.gitignore` — ignores `var/` and `.tools/` (large ingest artifacts).

## 5. Files reverted for boundary compliance

Per maintainer instruction (theme/presentation work belongs to another agent):

* `themes/cantilever/layouts/main.html` — reverted to `HEAD`.
* `content/index.md` — reverted to `HEAD`.

Desired navigation change (documented, **not applied**): add a "State
Cannabis Data" nav group linking `jurisdictions`, `datasets`,
`safety-advisories`, `testing-laboratories`, `licenses`, `organizations`,
`contaminants`, `requirements`, `affected-products`, and a matching section in
`content/index.md`. Apply after the rebase and only with the theme owner's
coordination.

## 6. Fixture provenance and the publication guard

* `tests/fixtures/massachusetts/PROVENANCE.md` labels every row set:
  **verbatim source excerpt** (testing-2025 slice, sales/price/activity/
  applications/agents slices), **redacted source excerpt** (license rows with
  EIN/email/phone/address/coords blanked; truncated advisory HTML),
  **synthetic schema fixture** (11 rows in the 2024 testing fixture crafted
  from the official analyte naming convention), and **derived from verbatim
  source** (`advisories.json`, parsed from real advisory HTML).
* **Hard guard**: both `MassachusettsSync.run_dataset` (snapshot/manifest
  writes) and `MassachusettsSync.generate_content` (page writes) raise, and
  the CLI exits 2, when `--fixtures-only` is used without
  `--allow-fixture-content`. With the dev flag, the CLI routes output to the
  isolated, gitignored `var/ingest/<state>-ccc/demo-content/` — never the
  real `content/` tree. Synthetic/verbatim fixture records can never reach
  publishable content or the durable manifest.
* All fixture-derived public content and durable records were **deleted**
  from the working tree (previously generated demonstration output):
  `content/jurisdictions*`, `licenses*`, `organizations*`,
  `testing-laboratories*`, `contaminants*`, `datasets*`, `requirements*`,
  `safety-advisories*`, `affected-products*`, `reference/TREF-0004.md`, and
  `data/massachusetts-ccc/`.

## 7. Source classification (every Massachusetts dataset)

All statuses reflect **no live ingestion completed in this environment**
(endpoints, sizes, and headers were verified; samples captured). One status
each, honest:

| Dataset | Status | Source URL | Size (probed) | Rows (probed) | Content produced? |
| --- | --- | --- | --- | --- | --- |
| licenses | fixture-only implementation | `…/resource/l_licenses_all_details_public.csv` | ~480 KB | header verified | no (guard) |
| commence_ops | fixture-only implementation | `…/resource/l_licenses_commence_ops.csv` | small | header verified | no |
| mtc_licenses | fixture-only implementation | `…/resource/l_licenses_mtc.csv` | small | header verified | no |
| testing_2025 | fixture-only implementation (large; streaming) | `…/resource/CCC_Testing_Results_2025.csv` | ~70 MB | header verified | no |
| testing_2024 | fixture-only implementation (large; streaming) | `…/resource/Testing_Results_2024_20260415_OpenData.csv` | ~100 MB | header verified | no |
| sales_gross | fixture-only implementation | `…/resource/a_sales_au_gross.csv` | ~7.6 MB | header verified | no |
| sales_deliveries | fixture-only implementation | `…/resource/a_sales_au_deliveries.csv` | small | header verified | no |
| price_per_gram | fixture-only implementation | `…/resource/a_sales_au_price_per_gram.csv` | small | 92 months (fixture) | no |
| mtc_sales | fixture-only implementation | `…/resource/a_sales_mtc_gross.csv` | small | header verified | no |
| plant_activity | fixture-only implementation | `…/resource/a_sales_au_activityvolume.csv` | small | header verified | no |
| applications_totals | fixture-only implementation | `…/resource/a_applications_all.csv` | small | 14 rows (fixture) | no |
| applications_dbe | fixture-only implementation | `…/resource/a_applications_dbe.csv` | small | 7 rows (fixture) | no |
| agents_gender | fixture-only implementation | `…/resource/a_agents_gender.csv` | small | 4 rows (fixture) | no |
| agents_raceethnicity | fixture-only implementation | `…/resource/a_agents_raceethnicity.csv` | small | 10 rows (fixture) | no |
| advisories (portal) | fixture-only implementation (real HTML captured) | `…/news/public-health-and-safety-advisories/` | small | 3 advisories | no |
| R industry-report scripts | source discovered but not implemented | catalog AJAX table | n/a | n/a | no |

`live complete ingestion` / `live partial ingestion`: none yet — blocked by
the reconciliation gate. `unstable`: none observed beyond the differing 2024/
2025 testing schemas (handled). Checksums, normalized row counts, and
reporting periods for live runs must be recorded by the first live sync.

## 8. Page and entity counts

* Published Massachusetts pages: **0** (guard + deletion).
* Deterministic dev-mode regeneration (isolated temp dirs, explicit
  `--allow-fixture-content`): **96 files, byte-identical across two runs**;
  id-maps identical. This proves stable allocation, not publishable output.
* Stable-ID machinery: 86-mapping `id-map.json` persists natural keys →
  Boris entity IDs with integrity-digest tamper detection; unit-tested.

## 9. Privacy exclusions

`PRIVACY_SPEC` defines excluded field names and per-entity allowlists; the
gate scans generated Markdown for excluded names and sensitive-value patterns
(EIN/TIN, email, phone, street address, explicit coordinate pairs, standalone
5+ decimal coordinates). Fixture scans: **0 findings**. All sensitive source
columns are blanked in committed fixtures (verified: 0 emails/phones/EIN/
coords).

## 10. Test results

**78 tests, OK (3 skipped** = optional live-smoke tests requiring network).
Coverage: CSV streaming, BOM/truncation/decode guards, content-type guards,
license normalization, lab extraction, privacy allowlists, advisory
discovery/parsing, affected-package natural keys, product-string preservation,
date-range parsing, stable ID reuse + tamper detection, source revision
comparison, schema drift, row-collapse + empty-output guards, backward-date
regression guard, frontmatter/table escaping, relation-target validation,
fixture-content guard, and end-to-end fixture ingestion with zero privacy
findings and zero broken relations.

## 11. California regression results

**Not run — California is unreachable** (see §1). No California behavior was
modified, deleted, or presumed. The shared package is state-agnostic and
unit-tested; migrating California into `scripts/ingest/states/california.py`
is pending the rebase.

## 12. Publication results (editorial tree only)

* `ted_ids.py`: validated **60 pages**; no files changed.
* Markdown link audit: all local links resolve.
* Privacy scan + relation targets: 0 findings / 0 broken.
* `validate_graph.sh`: Boris graph clean; full Cantilever build passed; HTML
  ID audit 0 duplicates.
* `ted-publish.sh`: site, sitemap, IR, RAG, context bundle, and `llms.txt`
  exported and valid.
* No Massachusetts artifacts appear anywhere in `dist/` or `publish/`.

The backward-date regression guard covers day-level fields (testing, sales)
and month-level fields (`price_per_gram`, `plant_activity`, normalized to
first-of-month); `DateRegressionError` fires beyond a 30-day backward move
without a source clarification.

## 13. Unresolved issues

* **California commit `3628c641` unreachable** from this worktree (origin
  path sandboxed). Rebase blocked.
* R industry-report script URLs render via an AJAX table; no stable direct
  download captured.
* Duplicate-key guard on live testing data uses `(date, metrc, analyte, lab,
  result)`; same-day identical retests could still collide — verify against
  the first live sync.
* 2024 vs 2025 testing schemas differ (casing/columns); both handled, drift
  flagged.

## 14. Next-sync commands (after reconciliation unblocks)

```bash
# full live sync — first run records checksums/row counts; streams ~175 MB
BORIS_BIN="$PWD/bin/boris" python3 scripts/state_ingest.py massachusetts

# single dataset retry
python3 scripts/state_ingest.py massachusetts --dataset testing_2025

# offline verification (tests only; never writes public content)
python3 -m unittest discover -s tests -t .
python3 scripts/state_ingest.py massachusetts --fixtures-only   # exits 2 (guard)
```

## 15. Focused commit SHA

`3628c641af3d262825b11b0baa4db7a304556356` — the California DCC ingestion
commit on `main` that this reconciliation must be rebased onto once it is
reachable.
