# Editorial Audit Reports

These documents were produced during the scientific/technical/legal/editorial reliability pass over `content/`. They are internal maintainer artifacts and are intentionally **not** part of the published Boris site (they live outside `content/`).

| Report | Purpose |
| --- | --- |
| [placeholder-disposition.md](placeholder-disposition.md) | Disposition of industrial-process placeholder content |
| [unresolved-claims.md](unresolved-claims.md) | Every claim left unresolved, with needed source and recommended action |
| [source-manifest.md](source-manifest.md) | Primary sources added/attributed across the audit |
| [terminology-consistency.md](terminology-consistency.md) | Standardized evidence and claim terminology |
| [cultivar-identity-implementation.md](cultivar-identity-implementation.md) | Provenance-aware cultivar identity architecture and claim registry |
| [validation-results.md](validation-results.md) | Commands run and their results |

## Scope guardrails honored

- No changes to `scripts/ingest/`, `scripts/*_ingest.py`, `content/jurisdictions/`, `licenses/`, `testing-laboratories/`, `recalls/`, `safety-advisories/`, `affected-products/`, `datasets/`, `requirements/`, or `theme/`.
- The closed Boris frontmatter schema (`id`, `title`, `parent`, `status`, `tags`, `relations`) was preserved; no new frontmatter keys were introduced.
- No fabricated sources. Where evidence could not be found, claims were softened and logged in `unresolved-claims.md`.
- Generated build output (`dist/`, `publish/`) was not committed.