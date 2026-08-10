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

## Shared ID authority and allocation reservation

There is one canonical namespace. The global editorial authority is the ID in
content frontmatter, with `metadata/id-map.jsonl` recording the migration from
prior source identities. A state map is a durable natural-key registry and
reservation history; it is not a second namespace. State adapters share the
collection prefixes in `metadata/id-policy.json` and seed new allocations from
the combined `content/` tree. Existing canonical, source-native, and
provisional IDs are reused as-is; this procedure never renumbers them.

The current state registry loads, allocates, and saves in one process but does
not acquire a cross-process lock. Until that allocator is migrated into a
shared transactional registry, every allocation touching a shared collection
must use the repository lock for the complete preflight → allocation →
postflight window. On macOS (the operator environment), run the whole state
allocation as one locked shell group:

```bash
ID_LOCK="$PWD/.git/ted-id-allocation.lock"
(
  lockf -s -t 0 9 || exit 75
  python3 scripts/ted_ids.py \
    --root content --map metadata/id-map.jsonl --all-state-maps &&
  python3 scripts/state_ingest.py massachusetts "$@" &&
  python3 scripts/ted_ids.py \
    --root content --map metadata/id-map.jsonl --all-state-maps
) 9>"$ID_LOCK"
```

Put the state command's flags in place of `"$@"`; for example, invoke the
group from a wrapper with `--dataset licenses`, or remove `"$@"` for the
default live sync. Exit `75` means another allocator owns the reservation
window; do not retry inside the same uncommitted content tree without first
checking its status. On Linux, the equivalent is `flock -n` around the same
three commands.

For a global/editorial allocation, use the same lock and include `--write`
only after reviewing the preflight result:

```bash
lockf -k -t 0 "$PWD/.git/ted-id-allocation.lock" \
  python3 scripts/ted_ids.py \
    --root content --map metadata/id-map.jsonl --all-state-maps --write
```

The `--all-state-maps` guard verifies every configured state map's digest,
prefix, natural-key uniqueness, and canonical-ID uniqueness. `ted_ids.py`
also treats every state-map form ID as reserved, including a historical claim
whose page is not in the current tree, so a new editorial allocation cannot
reuse it. A duplicate claim fails closed with `state ID collision`; it must be
resolved by the integrator without renumbering either claimant.

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

## Sharing collections with California (v2)

Massachusetts shares the canonical collections (`jurisdictions`, `licenses`,
`organizations`, `testing-laboratories`, `datasets`, `requirements`,
`contaminants`, `safety-advisories`, `affected-products`) with the California
DCC content already committed on `main`. On every live run the importer seeds
its ID allocator from the combined content tree, so Massachusetts IDs always
continue from the highest existing number per collection (e.g. California owns
`jurisdictions/TJUR-0001`; Massachusetts is `jurisdictions/TJUR-0022`, the
number `main`'s jurisdiction scaffold reserved for the state). The persisted
`data/massachusetts-ccc/id-map.json` keeps these mappings stable across runs.

> ⚠️ **Never delete `data/massachusetts-ccc/id-map.json` without also removing
> the generated Massachusetts pages.** The allocator seeds from whatever IDs
> exist in the content tree; a deleted registry with stale pages left behind
> would allocate *new* IDs and orphan the old pages.

Existing trunk pages (`content/<collection>.md`) are preserved untouched when
Massachusetts regenerates content — only the missing trunks
(`safety-advisories.md`, `affected-products.md`) are created.

## Determinism

Regeneration is deterministic: given the same source snapshots and code
version, reruns produce byte-identical content files (verified: 293 content
files identical across a full live re-sync). Retrieval timestamps live in the
manifest, never in page text.

## Known pre-existing gate failure (California release audit)

The repo-wide public-release audit (`scripts/audit_public_release.py`) reports
blocking PII findings on `data/dcc/` (California's committed license-registry
JSON and recall HTML, added by commit `3628c64`). This is pre-existing on
`main` and unrelated to Massachusetts; the Massachusetts pipeline contributes
zero findings (its own privacy scan passes cleanly). To run the full build/publish
gates, use the project's documented escape hatch:

```bash
SKIP_RELEASE_AUDIT=1 BORIS_BIN="$PWD/bin/boris" bash bin/validate_graph.sh
SKIP_RELEASE_AUDIT=1 BORIS_BIN="$PWD/bin/boris" bash scripts/ted-publish.sh
```

Do not treat the CA findings as resolved by this task. Current cross-state
architecture decisions and state status are tracked in `docs/status.md` and
`docs/status/states/massachusetts.md`.

## What is intentionally not generated

* One page per license or per test result (only aggregates; individual pages
  only for active Independent Testing Laboratories, advisory-connected
  licensees, and representative affected products).
* Per-application detail rows from `l_applications_all_details.csv` (the
  source file carries EIN/TIN, contact, and street-address fields; only
  aggregate counts by license type/status are published).
* Cultivar pages from advisory/testing strain strings — a candidate report is
  produced but no lineage/effect/terpene facts are manufactured.
* Laboratory rankings, producer rankings, or cultivar rankings.
* Numeric action limits — these must be confirmed against current regulation
  text before republishing.
* Raw coordinates, EIN/TIN, emails, phones, street addresses, agent records.
* California's existing `dcc_sync.py` workflow is not silently removed. Its
  relationship to the shared `state_ingest.py` command is an open architecture
  decision tracked in `docs/roadmap.md` and `docs/status.md`.
