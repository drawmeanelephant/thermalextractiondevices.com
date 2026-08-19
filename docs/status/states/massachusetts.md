# State Status — Massachusetts

Status: Complete (v2 productionized)
Last verified: 2026-08-13
Owner: Massachusetts implementation agent
Branch: agent/massachusetts-ingestion-v2

## Scope

Massachusetts Cannabis Control Commission open-data datasets, public-health
advisories, licensing, testing laboratories, requirements, contaminants,
affected products, and related aggregate records.

## Implementation state

- Adapter: scripts/ingest/states/massachusetts.py (shared `scripts/ingest/`
  package, state-agnostic core).
- Canonical command: `scripts/state_ingest.py massachusetts`.
- Live snapshot: completed and verified — 15 CCC datasets, 953,553 rows,
  ~185 MB (large testing files streamed), immutable checksummed snapshots in
  `var/ingest/massachusetts-ccc/` (gitignored).
- Generated content: 118 source-backed Massachusetts pages in the shared
  canonical collections (jurisdictions, licenses, organizations,
  testing-laboratories, datasets, requirements, contaminants,
  safety-advisories, affected-products, reference).
- ID allocation: reconciled with the global Boris identity policy —
  Massachusetts shares collections with California and seeds the allocator
  from the combined content tree. Massachusetts = `jurisdictions/TJUR-0022`
  (the number main's jurisdiction scaffold reserved); all other collections
  continue above California's maxima. Mappings persist in
  `data/massachusetts-ccc/id-map.json`.
- Durable artifacts: manifests, sync reports, privacy spec, and compact
  derived data under `data/massachusetts-ccc/`; large raw files stay outside
  git.
- Fixtures and tests: committed, privacy-scrubbed fixtures, an end-to-end
  fixture suite, live smoke tests, determinism and stale-source regression
  guards (89 offline + 5 live tests).

## Resolved blockers (2026-08-09)

- State-local ID allocation reconciled with the global Boris identity policy.
- Canonical relationship decided: shared `state_ingest.py` contract; the
  California `dcc_sync.py` workflow is retained as a documented legacy path.
- Live sync completed, privacy-safe, and published.
- Raw large source files kept outside git; privacy gate passes for all
  Massachusetts artifacts.

## Remaining item

None for Massachusetts. This document previously recorded the repo-wide
public-release audit as blocked by California's `data/dcc/` findings. That was
already out of date before the history rewrite: the payloads were untracked from
the working tree in `6d740f4`, and PR #41 graded the deleted-but-reachable
history findings `medium`, below the `high` fail threshold, so the gate passed
with every blob still reachable. The 2026-08-12 rewrite then removed the data
from `main` — a privacy improvement, not a gate change. Massachusetts
contributed zero findings throughout.

The repository does still have an open PII exposure, but it is neither
Massachusetts' nor blocking this lane: the purged payload remains downloadable
from GitHub through pre-rewrite pull refs. See `docs/history-cleanup-plan.md`.

## Validation

Verified 2026-08-13. Fixture tests, live smoke tests, ted_ids, Markdown link
audit, privacy scan, Boris graph, full build and publish all pass. The release
audit runs unconditionally and completes with no findings above its `high` fail
threshold — the `SKIP_RELEASE_AUDIT=1` escape hatch this document previously
relied on was removed from the codebase by the publication-hardening wave and no
longer exists. Live re-sync is byte-identical.

## Changelog

Reserved: changelog/TCHG-0003. Do not create a competing TCHG record on a
parallel branch.
