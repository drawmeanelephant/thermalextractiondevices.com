# State Status — Massachusetts

Status: In progress
Last verified: 2026-08-08
Owner: Massachusetts implementation agent
Branch: TBD

## Scope

Massachusetts Cannabis Control Commission open-data datasets, public-health
advisories, licensing, testing laboratories, requirements, contaminants,
affected products, and related aggregate records.

## Implementation state

- Adapter: scripts/ingest/states/massachusetts.py exists and is fixture-tested.
- Canonical command: scripts/state_ingest.py massachusetts.
- Live snapshot: none completed in the current repository state.
- Generated content: zero published Massachusetts pages.
- Durable artifacts: the importer supports data/massachusetts-ccc/, but no
  live durable snapshot is currently committed.
- Fixtures and tests: committed, privacy-scrubbed fixtures and an end-to-end
  fixture suite exist.

## Blockers

- Reconcile state-local ID allocation with the global Boris identity policy.
- Decide the canonical relationship between the Massachusetts CLI and the
  California DCC workflow.
- Complete and verify a live sync before generating publishable content.
- Keep raw large source files outside git and pass the privacy gate.

## Next action

Complete one live, privacy-safe Massachusetts run and record its exact
datasets, checksums, generated pages, and validation results.

## Validation

Fixture tests and source-only ID validation are available. The pinned Boris
graph/build tools are now available; live Massachusetts publication still
requires the sync, privacy review, and global release gate.

## Changelog

Reserved: changelog/TCHG-0003. Do not create a competing TCHG record on a
parallel branch.
