# Three-State Jurisdiction Review — California, Massachusetts, Michigan

Date: **2026-08-09**.

## What is universal

- Jurisdiction → license → legal entity/premises is a useful backbone.
- Testing requirements need raw state terminology plus normalized categories.
- Labs, recalls/advisories, products, batches, and COAs need separate identity
  and provenance rather than a single licensee object.
- Source manifests and retrieval dates are useful even when a source is not
  machine-readable.
- Negative evidence gaps must be first-class records.

## State-specific differences preserved

| Concept | California | Massachusetts | Michigan |
| --- | --- | --- | --- |
| License source | DCC JSON API | CCC CSV/JSON open-data catalog | Accela search + DOC/DOCX reports |
| Testing data | DCC lab registry and curated requirements; no public statewide COA corpus | Large testing CSVs; lab names anonymized | CRA technical guide; no public statewide COA corpus |
| Notice vocabulary | recall | public health and safety advisory | voluntary recall, mandatory recall, consumer advisory |
| Traceability | DCC license/recall surfaces | Metrc-derived testing files | Metrc is described, but public data access is limited |
| Numeric limits | intentionally not republished in CA record | intentionally not republished in MA record | captured from current CRA guidance with matrix/product scope |

## Architecture findings

1. The shared source-manifest and evidence model survived Michigan without a
   schema rewrite.
2. The shared ID-seeding and closed-frontmatter conventions worked; Michigan
   records allocated after existing CA/MA records without collisions.
3. The shared COA model survives a jurisdiction with zero public COAs: zero is
   represented as an evidence gap, not a chemistry result.
4. The current human collection names are not fully jurisdiction-neutral:
   `recalls` and `safety-advisories` carry historical state semantics.
5. The largest missing abstraction is a source adapter contract for
   document-oriented registries and PDFs, not another state-specific page
   generator.

## State #4 readiness

State #4 should be easier to add than Michigan if it has a stable CSV/JSON/API
surface: the Massachusetts package provides the reusable path, and Michigan
proves how to document a poor source without creating a second architecture.
If State #4 is another Accela/DOCX/portal-heavy state, the same source and
document friction will recur until shared document ingestion and relationship
confidence are improved.
