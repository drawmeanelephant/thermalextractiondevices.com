# Thermal Extraction Devices — Current Status

Last verified: 2026-08-09
Base commit reviewed: 8649973

This is the current coordination snapshot. It is intentionally shorter-lived
than docs/roadmap.md and more operational than the public changelog.

## Status vocabulary

- **Complete** — acceptance criteria met and verified.
- **In progress** — active implementation exists, but required work remains.
- **Blocked** — work cannot proceed until the named dependency is resolved.
- **Parked** — intentionally deferred.
- **Ready** — scoped and unblocked for an agent.

## Current workstream matrix

| Workstream | Status | Current evidence | Main blocker | Next deliverable |
| --- | --- | --- | --- | --- |
| Roadmap and coordination | Complete | docs/roadmap.md, this file, and state lanes exist | None | Keep status current as work lands |
| Multi-state ingestion architecture | In progress | California scripts and shared Massachusetts package coexist | Canonical CLI and global ID allocation are unresolved | Publish adapter contract and collision-safe registry |
| California DCC program | In progress | DCC scripts, content collections, and data/dcc snapshots are on main | Public-release privacy and storage decision | Reconcile or explicitly document the legacy path |
| Massachusetts CCC program | Complete | Live sync verified (15 datasets, ~954k rows); 118 source-backed pages published; IDs reconciled with the shared collections (Massachusetts = jurisdictions/TJUR-0022) | Repo-wide release audit is blocked by pre-existing `data/dcc/` findings (see reports/massachusetts-ingestion-v2.md) | Keep manifests current as CCC publishes |
| Device encyclopedia | In progress | 43 device records and four manufacturer records; the Cannabis Hardware catalog is complete and fully classified (TCHG-0004) | Coverage of the remaining manufacturers | Apply the Cannabis Hardware completion pattern to the next manufacturer |
| Laboratory and batch/COA graph | Parked | California laboratory collections and demonstration records exist | Canonical batch/report/analyte model | Define the minimum batch/COA schema |
| Profile intelligence | Parked | Terpene and evidence reference pages exist | Measured batch corpus and normalization | Start after batch/COA model |
| Public release readiness | Blocked | Checklist and audits exist | Category-4 data in data/dcc, licensing, security contact | Decide data disposition before public release |

## Immediate priorities

1. Establish one safe multi-state ingestion contract without regressing
   California.
2. Make ID allocation global across all generated state collections.
3. Complete Massachusetts as one end-to-end live-state reference.
4. Decide whether California is migrated into the shared adapter architecture
   or remains a documented legacy path.
5. Define the minimum product → batch → laboratory report → analyte model
   before scaling data ingestion.

## Parallel-work contract

- The roadmap records direction and acceptance criteria; do not use it as a
  daily task log.
- Each state or workstream owns its file under docs/status/states/.
- Update the top-level status matrix only when a milestone, dependency, or
  status meaningfully changes.
- Changelog records are append-only and describe completed merged work or
  durable architectural decisions.
- Do not invent a parallel TCHG ID. Use an ID reserved here or ask the
  integrator to allocate one at merge time.
- Do not hand-edit metadata/id-map.jsonl. Run the approved ID tooling after
  content changes.
- Do not commit raw snapshots, build output, credentials, or local compiler
  binaries.

## Changelog reservations

| ID | Reservation | Lane |
| --- | --- | --- |
| changelog/TCHG-0002 | Roadmap, status, and parallel-work coordination | This documentation PR |
| changelog/TCHG-0003 | Massachusetts CCC end-to-end integration | Massachusetts implementation agent |
| changelog/TCHG-0004 | Cannabis Hardware corpus completion | Merged — this lane |

Unused reservations may be released by the integrator; canonical IDs are
immutable once a record is merged.

## Known documentation state

The August 5 Massachusetts audit and implementation report are historical
snapshots. They contain useful design evidence, but their statements about
California being unreachable and Massachusetts work being uncommitted no
longer describe main. This status file is the current summary; stale
operational wording should be corrected as part of the relevant implementation
lane.

## Verification notes

The current source-only ID check validated 419 pages without changing files.
The Boris graph, Cantilever build, Markdown-link audit, crosslink validator,
and HTML-ID audit completed successfully. The device taxonomy audit reports 0
errors and 24 existing warnings; the COA and record-completeness audits report
0 errors and 0 warnings. The system test run completed 311 tests with 6
optional skips.

## Archive integrity update

Verified 2026-08-09. The Arizer Solo II and Solo III CPSC recalls are now
modeled as `recalls/TRCL-0007` and `recalls/TRCL-0008`, with source-backed
relations to the manufacturer and Solo III device record. The crosslink layer
now rejects a fully isolated satellite collection (`CXL-13`), and the DCC
generator now emits conservative organization → laboratory/recall reverse
edges when unique license-number matches exist. The required validation wrapper
still exits at the pre-existing public-release audit: 60 blocking findings,
including historical DCC data, PII-review findings, and git-history metadata.

## Publication hardening update

Verified 2026-08-09 against main commit `41768af` and the publication-
hardening commits on this branch. This PR removes current California DCC raw
and normalized payloads, redacts direct contacts and street addresses from
in-scope content, removes internal provenance paths from published content,
and makes release audits fail closed. It does not modify the Massachusetts
implementation, fixtures, tests, or state documents. The remaining release
blockers are reachable historical DCC blobs and metadata, the documented
human-review findings, licensing/security-process decisions, and the
repo-wide audit findings carried by the Massachusetts lane.

Validation must be rerun on the completed branch. Do not use an audit bypass as
a release result.
