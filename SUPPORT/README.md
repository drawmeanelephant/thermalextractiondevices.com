# Thermal Extraction Devices Content Truck 01

This pack contains source Markdown intended for the Boris `afterparty` content
tree.

## Payload

- 8 provenance-first cultivar pages
- 2 reference pages
- 4 guides
- 3 reusable include fragments
- index-link suggestions

## Installation

Copy the `content/` directory into the site's content root while preserving
paths. Review `PATCHES.md` and add the suggested wiki-links to the existing
trunk pages.

## Important assumptions

- Existing trunk entity IDs are `cultivars`, `guides`, `reference`,
  `lab-results`, `products`, and `terpenes`.
- Existing terpene IDs match the RAG bundle supplied for the project.
- New numeric IDs continue the sequences shown in that bundle.
- All cultivar lineage and morphology statements are explicitly attributed to
  first-party breeder or seed-company sources.
- The pages do not claim that breeder marketing predicts a batch's chemistry or
  effects.

## Build checks

```text
boris check
boris --quiet
boris --rag --quiet
```

Inspect callouts, advanced tables, footnotes, include expansion, wiki-links, and
the long page TOC after compilation.
