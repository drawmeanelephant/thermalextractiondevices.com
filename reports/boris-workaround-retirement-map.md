# Boris Workaround Retirement Map

**Status:** planning handoff; no workaround is removed by this document.

This map records the current TED/Boris boundary after the current Boris
implementation review. It supersedes the older assumption that Boris lacks
canonical page-ID validation and marks BORIS-13 as needing a current
reproduction before any link-audit deletion is considered.

## Retirement classes

1. **Relations work:** generic navigation work expected to disappear after
   Boris exposes validated outgoing relations and derived incoming relations
   to the HTML render path.
2. **Check-policy work:** duplicated filtering expected to disappear after
   Boris reports `unreferenced_page` without making it fatal by default.
3. **BORIS-13 pending:** local Markdown-link validation may disappear only
   after a current Boris reproduction proves that the compiler rejects broken
   literal Markdown routes before publication.
4. **TED-specific:** regulatory, evidence, scientific, provenance, and
   epistemic logic that remains necessary regardless of Boris capabilities.
5. **Review:** useful or duplicated project machinery whose retirement needs a
   separate design/consolidation decision.

## Project-level inventory

| Component | Class | Retirement decision |
| --- | --- | --- |
| `bin/validate_graph.sh` Boris check JSON filtering | 2 | Remove only the `unreferenced_page` filtering branch after the check-policy PR is merged; retain the gate and all TED-specific validators. |
| `scripts/dcc_ingest.py::verify_content` Boris check filtering (around lines 1302–1310) | 2 | Remove the duplicate interpretation of Boris findings after the same policy change; keep ingestion guards and publication orchestration. |
| `scripts/audit_markdown_links.py` | 3 | Keep today. Reclassify/delete only after current Boris source plus a minimal fixture demonstrate pre-publication rejection of broken authored local Markdown routes. |
| `scripts/ted-build.sh` invocation of the Markdown audit | 3 | Keep today; its removal is coupled to the audit decision. The Boris build wrapper itself remains TED orchestration. |
| `scripts/state_ingest.py` invocation of the Markdown audit | 3 | Keep today; remove or centralize only after BORIS-13 is reproduced as fixed and the ingestion release contract is rechecked. |
| `scripts/crosslinks.py` direct relation parser, reverse edges, generic Related/Backlinks rendering, HTML injection, and generic pagination | 1 | Candidate for retirement after Boris relation data is available in templates/output. Retire in slices; do not remove domain projections with it. |
| `scripts/validate_crosslinks.py` checks that only protect the generic injected navigation layer | 1 | Reassess after relation rendering moves into Boris. Keep the TED semantic and evidence checks. |
| `scripts/crosslinks.py` claim, COA, source-note, trace, epistemic-label, and domain projection logic | 4 | Must remain. These are TED graph semantics, not generic Boris navigation. |
| `scripts/cultivar_claims.py` and `scripts/validate_cultivar_claims.py` | 4 | Must remain. Extensible Boris relation kinds could reduce entity-to-entity duplication, but cannot replace claim status, provenance, disagreement, or wording rules. |
| `scripts/coa_model.py`, `scripts/audit_coa_content.py`, and COA metadata | 4 | Must remain. Boris must not absorb analytical chemistry or regulatory evidence semantics. |
| `scripts/ted_ids.py`, `metadata/id-policy.json`, `metadata/id-map.jsonl` | 4/5 | Keep TED domain allocation, migration, and immutability rules. Boris owns valid/unique page-ID validation; TED owns its form-code and migration policy. Review whether the migration map can be the sole shared registry. |
| `scripts/ingest/ids.py::NaturalKeyRegistry`, `data/massachusetts-ccc/id-map.json` | 5 | A second allocation/mapping surface exists. Consolidate only through a deliberate multi-state migration; do not delete as a Boris PR side effect. |
| `scripts/audit_html_ids.py` and release/privacy/audit tooling | 4/5 | Keep unless a separately verified Boris output contract makes a specific check redundant. These are publication and release-governance checks, not relation work. |

## `crosslinks.py` decomposition

Line numbers below refer to the current file at the time of this handoff.

| Approx. lines / functions | What it does | Class | Decision |
| --- | --- | --- | --- |
| 183–278: `Entity`, `Edge`, `Section`, `CrosslinkGraph` | TED's typed graph/index and display metadata containers | 4/5 | Keep the domain fields and evidence trace model. The generic incoming/outgoing index can be replaced or fed by Boris's validated graph export later. |
| 280–308: `load_entities` | Loads TED's ID map for titles, collections, roles, and output paths | 4/5 | Keep as a TED publication projection. It is not a second Boris identity authority. Reassess only if Boris supplies equivalent title/path metadata. |
| 310–361: `parse_frontmatter_relations`, `load_direct_edges` | Re-parses Boris frontmatter relations to recover direct edges | 1 | Generic workaround. Replace with Boris's validated relation surface once available; do not delete before that. |
| 363–458: `coa_record_from_dict`, `load_coa_records` | Rehydrates and validates durable COA records | 4 | Must remain; this is scientific evidence-model logic. |
| 460–478: collection/role helpers and `build_graph` entry | TED collection semantics and graph assembly | 4/5 | Keep TED role semantics; remove only duplicated Boris graph loading when a safe replacement exists. |
| 493–529: claim-registry edge construction and source notes | Converts identity claims into typed edges or text-only attributions | 4 | Must remain; claims are not ordinary navigation edges. |
| 531–576: COA measurement edges and report/batch metadata | Projects laboratory, product, analyte, and batch evidence | 4 | Must remain. Boris must not become a COA/regulatory graph engine. |
| 578–644: reverse-edge and cultivar/product multi-hop projections | Generic reverse navigation plus TED evidence-aware projections | 1 + 4 | Split. Boris relation work can replace the generic reverse/backlink half; cultivar/product/report projections and evidence traces remain TED-owned. |
| 657–733: reverse-kind, role, item collection, backlink/outgoing helpers | Deterministic navigation materialization | 1 | Generic portions are retirement candidates after Boris renders incoming/outgoing relations. Preserve TED edge-class and evidence labeling where still needed. |
| 755–939: `sections_for` | Context rules for compounds, cultivars, products, laboratories, reports, Related, and Backlinks | 1 + 4 | Split by section: generic `related`/`backlinks` are class 1; lineage, breeder, claim, laboratory, batch, analyte, observed-compound, and epistemic sections are class 4. |
| 940–1031: `export_json`, `render_rag_document` | TED machine export and retrieval companion with evidence wording | 4/5 | Keep. Reassess only the direct-edge input once Boris has an authoritative export; do not assume Boris can replace TED's evidence language. |
| 1035–1184: HTML escaping, item/section rendering, `inject_html`, `inject_all` | Post-render navigation injection | 1, with 4 inputs | Generic workaround expected to disappear for relation navigation after Boris template rendering. Keep until the replacement is verified; domain evidence sections still need an approved rendering surface. |
| 1186–1361: index paths, pagers, shell splicing, `generate_index_pages` | Bounded/paginated navigation pages created outside Boris | 1 + 5 | Generic backlink pagination is a retirement candidate if Boris provides bounded rendering. TED-specific high-degree evidence projections need a separate review. |
| 1364–1600: `validate_graph`, `_validate_edge_type`, section/HTML/index validators | TED graph semantics, provenance and generated-output checks | 4/5 | Keep semantic/evidence checks. Remove only checks proven to duplicate Boris's future validated relation/rendering contract. CXL-01 is tied to the injection layer and should be reassessed with that layer. |
| 1602–1709: CLI and orchestration | Loads TED registries, builds graph, emits exports, injects, indexes, validates | 5 | Keep as orchestration until the underlying slices are retired; it should shrink rather than be removed wholesale. |

## Boris finding status

| Finding | Current status in TED notes |
| --- | --- |
| BORIS-01, -02, -03 | Confirmed as one Boris semantic-relations capability gap: constrained relation model plus no first-class HTML outgoing/incoming rendering. |
| BORIS-04 | Deferred. Structured data and jurisdiction ingestion remain TED concerns; no Boris expansion is planned from this evidence alone. |
| BORIS-05 | Deferred/re-scoped. TED validators are real, but this does not justify an executable plugin lifecycle; prefer stable Boris artifacts/validation surfaces and keep domain checks outside Boris. |
| BORIS-06 | Reclassified/closed as a Boris-gap claim. Boris already owns canonical page-ID shape and duplicate validation. TED's form-ID allocation, migration, and domain policy remain project-owned. |
| BORIS-07 | Deferred. Shell orchestration shows friction but does not establish that Boris should execute third-party hooks. |
| BORIS-08 | Confirmed and narrowed to `unreferenced_page` default exit policy plus findings documentation/configuration. The TED filters are temporary workarounds. |
| BORIS-09, -10, -11, -12 | Retain as lower-priority ergonomics/ecosystem/documentation backlog; not affected by this correction. |
| BORIS-13 | `needs-current-reproduction`. Do not delete `audit_markdown_links.py` until the old literal `.md` case is tested against current Boris source. |

## Validators that remain necessary today

TED must continue to run ID/domain-policy checks, taxonomy and record
completeness checks, cultivar-claim validation, COA/evidence validation,
relation-target and crosslink semantic validation, source-level Markdown-link
validation pending BORIS-13 reproduction, rendered HTML-ID checks, and public
release/privacy/large-file audits. `crosslinks.py` relation/backlink behavior
also remains required today because Boris semantic relations are not yet
HTML-visible.

## Cleanup gates

1. Land and verify the Boris check-policy change, then remove only the two
   TED-side `unreferenced_page` exit filters.
2. Reproduce BORIS-13 against current Boris with the smallest fixture before
   touching the Markdown-link audit.
3. Land Boris relation rendering/export work, migrate the generic direct,
   reverse, backlink, injection, and pagination slices, and verify TED's
   domain evidence projections independently before shrinking `crosslinks.py`.
4. Treat the two ID maps as a separate multi-state consolidation project.
