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

- **The DCC licensee registry is still retrievable from GitHub.** This is
  California's data and California's blocker. The 2026-08-12 history rewrite
  cleaned `main`, but 43 pre-rewrite `refs/pull/N/head` refs still carry the
  commit that introduced the payloads, so an unauthenticated client can still
  fetch the registry. The repository is public. Specifics are in the private
  security advisory, not here. Closing it needs a GitHub Support request; see
  `docs/history-cleanup-plan.md`.
- Cross-state ID allocation and the canonical CLI are not yet unified.
- The DCC tree disposition is private/unpublished storage; whether California
  is re-fetched through the shared adapter or frozen as a documented legacy
  snapshot is still undecided.

## Partially resolved (2026-08-12)

`origin/main` no longer carries the historical `data/dcc/` payloads. The history
rewrite in `docs/history-cleanup-plan.md` was executed and `main` was
force-pushed on 2026-08-12T18:04:56Z. A fresh clone's `.git` is 3.2 MiB with no
blob above 2 MiB, and `git log origin/main -- data/dcc/license-registry/latest.json`
returns no commits. Only `manifest.json`, `schema-report.md` and one sync report
remain tracked under `data/dcc/`. The pull-ref copies above are what is left.

## Next action

Choose between migrating California into the shared state adapter contract or
keeping the legacy path with an explicit, tested compatibility boundary.

## Validation

Verified 2026-08-13 on `39a5589`. The source-only ID check passes for the
combined content tree (445 pages). The Boris graph, Cantilever build,
Markdown-link audit, crosslink validator and HTML-ID audit all pass, and the
public-release audit now completes with no findings above its `high` fail
threshold — no bypass required.
