# Thermal Extraction Devices — Current Status

Last verified: 2026-08-09
Base commit reviewed: 2195db4

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
| California DCC program | In progress | DCC scripts, aggregate content, and the redacted data/dcc manifest/schema boundary are present | Private payload storage and historical cleanup remain; Massachusetts findings are out of scope for this pass | Keep the safe ingest boundary and reconcile the legacy path |
| Massachusetts CCC program | In progress | Adapter, fixtures, tests, and CLI exist; no live content is published | Live verified sync plus architecture/ID reconciliation | Complete first live Massachusetts run |
| Device encyclopedia | In progress | 43 device records and four manufacturer records; the Cannabis Hardware catalog is complete and fully classified (TCHG-0004) | Coverage of the remaining manufacturers | Apply the Cannabis Hardware completion pattern to the next manufacturer |
| Laboratory and batch/COA graph | Parked | California laboratory collections and demonstration records exist | Canonical batch/report/analyte model | Define the minimum batch/COA schema |
| Profile intelligence | Parked | Terpene and evidence reference pages exist | Measured batch corpus and normalization | Start after batch/COA model |
| Public release readiness | Blocked | Checklist, release gates, and hardening reports exist | Historical DCC payloads, licensing, security-process confirmation, and excluded Massachusetts findings | Complete maintainer decisions and history cleanup |

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

The hardening pass removes current California DCC raw/normalized payloads,
redacts direct contacts and street addresses from in-scope content, and makes
release audits fail closed. Validation must be rerun on the completed branch;
historical DCC blobs and the explicitly excluded Massachusetts lane remain
reported blockers. Do not use an audit bypass as a release result.
