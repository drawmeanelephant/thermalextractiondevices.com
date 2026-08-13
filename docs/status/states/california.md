# State Status — California

Status: In progress
Last verified: 2026-08-13
Owner: Unassigned
Branch: main

## Scope

California Department of Cannabis Control licensing, laboratory, recall,
contaminant, requirements, and dataset records currently represented under
content/ and the redacted `data/dcc/` provenance boundary.

## Implementation state

- Adapter: scripts/dcc_ingest.py and scripts/dcc_sync.py.
- Canonical command: California currently follows the legacy DCC path; the
  relationship to scripts/state_ingest.py remains an architectural decision.
- Live snapshot: source payloads are retained privately; no raw or normalized
  DCC snapshot is tracked in the public repository.
- Generated content: jurisdiction, license, organization, testing laboratory,
  recall, contaminant, dataset, and requirements collections are present.
- Durable artifacts: `data/dcc/manifest.json`, `schema-report.md`, and sync
  reports are tracked; raw and normalized payloads are private/unpublished.
- Fixtures and tests: California regression coverage must be preserved while
  the shared state architecture is reconciled.

## Blockers

- Cross-state ID allocation and the canonical CLI are not yet unified.
- The DCC tree disposition is private/unpublished storage; whether California
  is re-fetched through the shared adapter or frozen as a documented legacy
  snapshot is still undecided.

## Resolved (2026-08-12)

The historical `data/dcc/` payloads no longer block public release. The history
rewrite in `docs/history-cleanup-plan.md` was executed and `main` was
force-pushed on 2026-08-12T18:04:56Z. A fresh clone of `origin/main` is 3.2 MiB
with no blob above 2 MiB, and `git log origin/main -- data/dcc/license-registry/latest.json`
returns no commits. Only `manifest.json`, `schema-report.md` and one sync report
remain tracked under `data/dcc/`.

## Next action

Choose between migrating California into the shared state adapter contract or
keeping the legacy path with an explicit, tested compatibility boundary.

## Validation

Verified 2026-08-13 on `39a5589`. The source-only ID check passes for the
combined content tree (445 pages). The Boris graph, Cantilever build,
Markdown-link audit, crosslink validator and HTML-ID audit all pass, and the
public-release audit now completes with no findings above its `high` fail
threshold — no bypass required.
