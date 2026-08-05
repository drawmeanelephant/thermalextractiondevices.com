# Massachusetts CCC Ingestion — Operator Guide

State-backed ingestion for Thermal Extraction Devices. One canonical command
drives everything:

```bash
python3 scripts/state_ingest.py massachusetts [flags]
```

---

## Source discovery

Official Massachusetts Cannabis Control Commission (CCC) sources:

| Source | URL |
| --- | --- |
| Data catalog | `https://masscannabiscontrol.com/open-data/data-catalog/` |
| Advisories | `https://masscannabiscontrol.com/news/public-health-and-safety-advisories/` |
| Direct downloads | `https://masscannabiscontrol.com/resource/<slug>.csv` (or `.json`) |

The catalog is JavaScript-rendered; direct CSV/JSON downloads are discovered
from the catalog page's `resource/*.csv|.json` links. The adapter's `DATASETS`
table (`scripts/ingest/states/massachusetts.py`) records each dataset's exact
official URL, reporting period, schema expectations, disclaimers, and
clarifications. **Archive the exact URL for every dataset** — the manifest
records `official_source_url` per snapshot.

## Live sync

```bash
BORIS_BIN="$PWD/bin/boris" python3 scripts/state_ingest.py massachusetts
```

This downloads every dataset (testing files are streamed to disk, never loaded
fully into memory), ingests advisories, regenerates content under `content/`,
runs the publication gates, and writes a sync report. Exit code is non-zero on
any blocking error.

> **Publication policy**: public content may only be generated from a
> complete verified live snapshot. Fixture/synthetic records are test-only.
> `--fixtures-only` refuses to run (exit 2) unless the explicit development
> flag `--allow-fixture-content` is passed — and that flag routes output to
> the isolated, gitignored `var/ingest/<state>-ccc/demo-content/` directory,
> never the real `content/` tree.

## Fixture-only tests (no network)

```bash
python3 scripts/state_ingest.py massachusetts --fixtures-only   # exits 2 (guard)
python3 -m unittest discover -s tests -t .
```

Fixtures live in `tests/fixtures/massachusetts/` and are small schema-faithful
samples of the real files (private fields scrubbed). Every row set is labeled
verbatim / redacted / synthetic / handcrafted in
`tests/fixtures/massachusetts/PROVENANCE.md`. Fixture runs use an isolated
temporary store and never touch `data/massachusetts-ccc/`.

## Dataset-specific sync

```bash
python3 scripts/state_ingest.py massachusetts --dataset licenses
python3 scripts/state_ingest.py massachusetts --dataset licenses --dataset sales_gross
```

`--refresh` forces re-download even when an immutable snapshot checksum
matches.

## Artifact storage

| Path | Contents | Committed? |
| --- | --- | --- |
| `var/ingest/massachusetts-ccc/raw/` | Immutable raw snapshots (by SHA-256) | No (gitignored) |
| `var/ingest/massachusetts-ccc/normalized/` | Normalized machine records | No (gitignored) |
| `var/ingest/massachusetts-ccc/reports/` | Full sync reports | No |
| `data/massachusetts-ccc/manifest.json` | Per-dataset snapshot history | Yes |
| `data/massachusetts-ccc/id-map.json` | Natural-key → Boris ID mapping | Yes |
| `data/massachusetts-ccc/source-catalog.json` | Official source inventory | Yes |
| `data/massachusetts-ccc/schema-report.md` | Latest column schemas per dataset | Yes |
| `data/massachusetts-ccc/privacy-spec.md` | Excluded-field specification | Yes |
| `data/massachusetts-ccc/affected-packages.csv` | Normalized advisory packages | Yes |
| `data/massachusetts-ccc/cultivar-candidates.csv` | Cultivar-candidate report | Yes |
| `data/massachusetts-ccc/sync-reports/` | Durable sync reports | Yes |

Override the working directory with `--artifacts-dir PATH` (the durable
directory stays `data/massachusetts-ccc/` unless a cloud/artifact integration
is wired in later).

## Schema updates

Edit `required_columns` / `column_types` in the dataset's `DatasetDef`. Guards
fail publication when required columns disappear or numeric columns drift.
`date` drift produces non-blocking warnings that appear in the sync report.

## Source corrections

When a source release changes (checksum changes), the importer:

1. retains the prior manifest record and prior snapshot (never overwrites the
   only earlier copy);
2. records a new immutable snapshot under the new SHA-256;
3. compares row identity and values (`compare_snapshots`), distinguishing
   changed status labels from changed measurements;
4. writes a revision entry in the sync report.

`supersedes` relations are only emitted when the official release relationship
supports them — see `content/datasets/TDTS-0009.md` (Testing Corrections and
Clarifications).

## ID mapping

`data/massachusetts-ccc/id-map.json` persists every natural key → Boris entity
ID (`<collection>/<PREFIX>-NNNN`). IDs are allocated deterministically and
reused across runs. The file carries an integrity digest; editing it outside
the importer raises `IdMappingChangedError`. Do not hand-edit the mapping —
run the importer.

## Privacy allowlists

`PRIVACY_SPEC` in the state adapter defines the excluded field names and the
per-entity allowlists. The publication gate scans every generated Markdown
page for excluded field names and sensitive-value patterns (EIN/TIN, email,
phone, street address, raw coordinates). Raw local snapshots may keep source
fields for fidelity, but they stay in the gitignored working directory and
never reach generated content.

## Content regeneration

```bash
python3 scripts/state_ingest.py massachusetts --skip-publish
```

Regenerates all Massachusetts pages under `content/` (trunks at the root,
satellites in their collections). Pages are rebuilt from the manifest,
aggregates, and advisory records; existing editorial content is untouched.
Regeneration is deterministic: two identical runs produce byte-identical
pages and ID maps (verified). Only run against live-verified snapshots for
publishable output.

## Publication

The default run executes the full gate chain:

```bash
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl
python3 scripts/audit_markdown_links.py content
bash bin/validate_graph.sh   # Boris graph check + full HTML build
```

Gates fail closed: any error (privacy finding, broken relation, failed build)
returns a non-zero exit and the sync report records it. `--skip-publish`
bypasses the gates. `--report-only` renders a report from the existing
manifest without touching anything.

## Failure recovery

* **Network failure on one dataset**: the run reports the dataset as `error`;
  other datasets still ingest. Re-run with `--dataset <slug>` to retry only
  the failed one.
* **Checksum changed unexpectedly**: re-download is normal; the guard requires
  a new snapshot record whenever the checksum changes, and a row-collapse
  guard fails the run if row counts drop below the configured threshold
  without a recognized source correction.
* **Content half-written**: re-run; page generation is idempotent (IDs are
  stable, files are overwritten deterministically).
* **Corrupted `id-map.json`**: restore from the previous commit — but only
  after confirming no importer run raced it; the digest guard will flag
  manual edits.

## Reconciliation note (2026-08-05)

This repository's `main` (as visible from the worktree) does not contain the
California DCC ingestion commit `3628c641`; that commit lives in a repository
outside the sandbox and is currently unreachable. Until a rebase onto the
California-containing `main` completes, Massachusetts content must NOT be
published. All Massachusetts files here are uncommitted and test-only.

## What is intentionally not generated

* One page per license or per test result (only aggregates; individual pages
  only for active Independent Testing Laboratories, advisory-connected
  licensees, and representative affected products).
* Cultivar pages from advisory/testing strain strings — a candidate report is
  produced but no lineage/effect/terpene facts are manufactured.
* Laboratory rankings, producer rankings, or cultivar rankings.
* Numeric action limits — these must be confirmed against current regulation
  text before republishing.
* Raw coordinates, EIN/TIN, emails, phones, street addresses, agent records.
* `dcc_sync.py`-style duplicate workflows — there is exactly one canonical
  command (`state_ingest.py`).
