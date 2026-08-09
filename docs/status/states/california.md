# State Status — California

Status: In progress
Last verified: 2026-08-08
Owner: Unassigned
Branch: main

## Scope

California Department of Cannabis Control licensing, laboratory, recall,
contaminant, requirements, and dataset records currently represented under
content/ and data/dcc/.

## Implementation state

- Adapter: scripts/dcc_ingest.py and scripts/dcc_sync.py.
- Canonical command: California currently follows the legacy DCC path; the
  relationship to scripts/state_ingest.py remains an architectural decision.
- Live snapshot: California DCC snapshots are present under data/dcc/.
- Generated content: jurisdiction, license, organization, testing laboratory,
  recall, contaminant, dataset, and requirements collections are present.
- Durable artifacts: data/dcc/ contains raw, normalized, manifest, schema, and
  sync-report material.
- Fixtures and tests: California regression coverage must be preserved while
  the shared state architecture is reconciled.

## Blockers

- Public release is blocked until the privacy and storage disposition for
  data/dcc/ is decided.
- Cross-state ID allocation and the canonical CLI are not yet unified.

## Next action

Choose between migrating California into the shared state adapter contract or
keeping the legacy path with an explicit, tested compatibility boundary.

## Validation

The source-only ID check currently passes for the combined content tree. The
Boris graph, Cantilever build, Markdown-link audit, and HTML-ID audit pass; the
overall release gate remains blocked by the known data/dcc privacy findings.
