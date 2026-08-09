# State Status — Massachusetts

Status: Complete (v2 productionized)
Last verified: 2026-08-09
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

The repo-wide public-release audit (`scripts/audit_public_release.py`) is
blocked by pre-existing PII findings in California's committed `data/dcc/`
snapshots (commit `3628c64`). Massachusetts contributes zero findings. See
`reports/massachusetts-ingestion-v2.md`.

## Validation

Fixture tests, live smoke tests, ted_ids, Markdown link audit, privacy scan,
Boris graph + full build, and publish all pass (release audit via the
project's documented `SKIP_RELEASE_AUDIT=1` escape hatch, as noted above).
Live re-sync is byte-identical.

## Changelog

Reserved: changelog/TCHG-0003. Do not create a competing TCHG record on a
parallel branch.
