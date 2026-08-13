# Thermal Extraction Devices — Current Status

Last verified: 2026-08-13
Base commit reviewed: 39a5589

> `main` was force-pushed on 2026-08-12T18:04:56Z to remove the California DCC
> bulk payloads from git history. Every SHA quoted below from before that date
> refers to the pre-rewrite history and no longer resolves upstream. Re-clone or
> hard-reset to `origin/main`; do not merge a branch created before the rewrite
> without rebasing it first. See docs/history-cleanup-plan.md.

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
| Multi-state ingestion architecture | In progress | California scripts and shared Massachusetts package coexist; Boris validates canonical page-ID shape/uniqueness while TED owns domain allocation and migration policy | One documented TED allocation boundary across the shared content map and state natural-key maps | Consolidate or explicitly scope the two TED ID maps |
| California DCC program | In progress | DCC scripts and content collections are on main; the bulk `data/dcc` payloads were removed from the tree and purged from git history on 2026-08-12, leaving only `manifest.json`, `schema-report.md` and one sync report tracked | Whether California is re-fetched through the shared adapter or documented as a frozen legacy snapshot | Reconcile or explicitly document the legacy path |
| Massachusetts CCC program | Complete | Live sync verified (15 datasets, ~954k rows); 118 source-backed pages published; IDs reconciled with the shared collections (Massachusetts = jurisdictions/TJUR-0022) | None — the `data/dcc/` findings that blocked the repo-wide release audit were cleared by the history rewrite | Keep manifests current as CCC publishes |
| Michigan CRA program | In progress | The Michigan evidence wave merged in PR #31 as jurisdictions/TJUR-0023: 28 content files including TSTL-0029..0031, TREQ-0003 and TDTS-0023..0025 | No `docs/status/states/michigan.md` lane document exists, unlike California and Massachusetts | Write the Michigan state lane document to match the California and Massachusetts format |
| Device encyclopedia | In progress | 43 device records and four manufacturer records; the Cannabis Hardware catalog is complete and fully classified (TCHG-0004) | Coverage of the remaining manufacturers | Apply the Cannabis Hardware completion pattern to the next manufacturer |
| Laboratory and batch/COA graph | Parked | California laboratory collections and demonstration records exist | Canonical batch/report/analyte model | Define the minimum batch/COA schema |
| Profile intelligence | Parked | Terpene and evidence reference pages exist | Measured batch corpus and normalization | Start after batch/COA model |
| Public release readiness | In progress | History rewrite executed and verified: a fresh clone of `origin/main` is 3.2 MiB with no blob above 2 MiB and no `data/dcc` bulk payload reachable; the release audit reports 49 findings, none above the `high` fail threshold | 14 medium findings awaiting human review, plus the licensing and security-contact decisions | Adjudicate the 14 medium findings (10 × PII-007 prohibited field *names* in the privacy spec and ingest validator, 4 × PII-005 on the documentation placeholder EIN used in the test suite) |
| Static build reproducibility | In progress | Two pinned production builds produced 496 identical files; `reports/static-build-reproducibility.md` records the byte comparison | The 496-path baseline predates the Denmark, relation-kind and RAG-export merges, so it no longer matches the current corpus | Re-run the reproducibility workflow against `39a5589` and record a new baseline |

## Immediate priorities

1. Adjudicate the 14 medium release-audit findings and settle the licensing and
   security-contact decisions, so public release readiness stops being the last
   open gate.
2. Establish one safe multi-state ingestion contract without regressing
   California.
3. Make ID allocation global across all generated state collections.
4. Decide whether California is migrated into the shared adapter architecture
   or remains a documented legacy path.
5. Write the Michigan state lane document so all three live jurisdictions have
   one.
6. Define the minimum product → batch → laboratory report → analyte model
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
- `main` was rewritten and force-pushed on 2026-08-12. Any branch whose
  merge-base predates that rewrite reintroduces the purged `data/dcc` payloads if
  merged. Rebase it onto the current `origin/main`, or recreate the change, before
  opening a pull request.

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

Re-run 2026-08-13 against `origin/main` at `39a5589`.

`./bin/validate_graph.sh` completed cleanly. The source-only ID check validated
445 pages without changing files. The device taxonomy, COA, cannabinoid
thermal-property, and record-completeness audits each report 0 errors and 0
warnings. The cultivar identity registry validated 15 claims against 445
entities. The crosslink validator reports 445 entities, 1,614 edges and 1 COA
record with no problems; publication derived navigation for 345 entity pages and
19 index pages, and the HTML-ID audit found 0 duplicate IDs. The Boris graph
diagnostics pass outright. `python3 -m unittest discover -s tests -t .` ran 359
tests with 6 skips and no failures. Upstream CI (`CI & Graph Validation`,
`Deploy to Cloudflare Pages`) is green on `39a5589`.

Static build reproducibility was last machine-checked at 496 paths / 10,133,239
bytes / aggregate SHA-256
`9a909f8c5656b8e300331427f98f0daafe63ad6b618278788535795bbc6ebb9b`. That
baseline predates the Denmark, relation-kind and RAG-export merges, so the page
count no longer matches; re-run the reproducibility workflow to establish a new
baseline before quoting it.

## Archive integrity update

Verified 2026-08-09, still current. The Arizer Solo II and Solo III CPSC recalls
are modeled as `recalls/TRCL-0010` and `recalls/TRCL-0011`, with source-backed
relations to the manufacturer and Solo III device record. The crosslink layer
rejects a fully isolated satellite collection (`CXL-13`), and the DCC generator
emits conservative organization → laboratory/recall reverse edges when unique
license-number matches exist.

## Publication hardening update

The publication-hardening work merged, and the git-history rewrite it depended on
was executed and force-pushed on 2026-08-12T18:04:56Z. Verified 2026-08-13
against a fresh clone of `origin/main`: the clone is 3.2 MiB, contains no blob
above 2 MiB, and `git log origin/main -- data/dcc/license-registry/latest.json`
returns no commits. The release audit on that clone reports 49 findings — 15
`REV-001` informational, 20 `PII-005` low, 10 `PII-007` medium and 4 `PII-005`
medium — with none above the `high` fail threshold and no `LARGE-00x` findings at
all.

A working clone made before the rewrite reports more. `LARGE-004` and `LARGE-003`
scan `git rev-list --all`, so pre-rewrite local branches and tags still make the
purged payloads reachable *locally*; that is a property of the stale clone, not of
`origin/main`. Delete stale local refs and `git gc --prune=now` before treating a
`LARGE-00x` finding as real.

Remaining release blockers are the 14 medium human-review findings and the
licensing and security-contact decisions. The mediums are all schema- or
placeholder-shaped rather than live data: `PII-007` fires on prohibited field
*names* declared in `data/massachusetts-ccc/privacy-spec.md`,
`data/massachusetts-ccc/source-catalog.json` and `scripts/ingest/validation.py`,
and `PII-005` fires on the documentation placeholder EIN used in the test suite.
They still need an explicit adjudication rather than a silent pass.

Validation must be rerun on the completed branch. Do not use an audit bypass as
a release result.
