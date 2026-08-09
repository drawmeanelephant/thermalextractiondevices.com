# Boris Issue Candidates — Thermalextractiondevices.com Dogfood Audit

Each entry is independently readable and copy-ready for an issue tracker. They were **not** filed automatically. Evidence is drawn from `reports/boris-dogfood-script-audit.md`, which contains the full inventory and analysis.

**Empirical verification:** several entries carry "Verified (boris/0.8.1, 2026-08-09)" evidence — the pinned Boris binary (`9505ec6`) was provisioned and the open questions were tested against fixture sites (template markers, relation cap/kinds, link audit, `check` output). See Appendix B of the audit report for the test protocol and raw results.

Priority legend: P0 = data-integrity risk; P1 = repeatedly causes project-local scaffolding; P2 = substantial ergonomic problem; P3 = useful improvement; P4 = documentation/polish.

---

## BORIS-01 — Expose the relation graph to templates (or render reverse edges/backlinks natively)

- **Priority:** P1
- **Classification:** Boris core
- **Problem:** A graph-based static-site compiler that renders no reverse edges and gives templates no access to `relations` forces every project to reimplement navigation. This repository built a 1,710-line Python layer (`scripts/crosslinks.py`) that re-parses frontmatter relations, computes backlinks and multi-hop projections, injects HTML into rendered pages with regex surgery, generates paginated index pages by copying layout shells, and validates its own output.
- **Real-world evidence:**
  - The theme (`themes/cantilever/layouts/*.html`) exposes `{{title}} {{content}} {{toc}} {{children}} {{breadcrumb}} {{nav}} {{asset-url}}` and nothing else; a search of the theme for relation references returns zero matches.
  - **Verified (boris/0.8.1, 2026-08-09):** the template marker vocabulary is closed — `{{relations}}` in a layout is a hard build error (`LayoutUnknownMarker`), and `{{metadata}}` renders status/parent/tags but never relations. Semantic relations are exposed nowhere in the HTML pipeline; the validated relation set appears only in the IR export (`graph.json`). Boris's own contract (`docs/contracts/semantic-relations.md`) states relations are "not a navigation edge" — i.e. Boris offers no navigation primitive at all.
  - `reports/graph-connectivity.md` (2026-08-08): an agent hand-added 96 relation edges and maintained a "bidirectional pair convention" because both ends of a relationship had to be edited.
  - `reports/crosslinking-implementation.md` (2026-08-09): the layer was built explicitly to replace that convention.
  - 90+ content pages carry hand-written `## Related Devices` / `## Related pages` sections that now coexist with generated sections.
- **Current workaround:** post-render HTML injection (`crosslinks.py --inject`) plus hand-maintained prose link lists.
- **Desired behavior:** A page template can render its outgoing relations, its incoming (backlink) relations, and (optionally) bounded derived sections (e.g. "Compounds observed in associated reports" from multi-hop edges) with count + truncation, all inside the normal render pass.
- **Acceptance criteria:**
  1. A template variable/function exposes incoming and outgoing typed relations per page (with entity id + title + relation kind).
  2. Backlinks render without any post-processing script; no regex HTML surgery.
  3. Bounded output is achievable (e.g. a built-in cap or a documented pattern) so a 20,000-backlink page does not explode.
  4. The existing `crosslinks.py` HTML-injection path can be deleted from the consuming project.
- **Design direction:** template data API (per-page `relations_in`, `relations_out`, `backlinks`) or a built-in `related` renderer; keep edge metadata (kind, direction) so projects can classify.
- **Affected project files:** `scripts/crosslinks.py`, `scripts/validate_crosslinks.py`, `scripts/ted-build.sh`, `themes/cantilever/layouts/*.html`, ~99 content pages with hand-written Related sections.
- **AI-attractor factor:** EXTREME.

---

## BORIS-02 — Relation cap of 16 per page is a hard wall that degrades content

- **Priority:** P0 (data integrity of the graph model) / P1 (scaffolding)
- **Classification:** Boris core
- **Problem:** `relations` is capped at 16 per page (`max_relation_count`, boris/0.8.1). Hub pages (manufacturers, jurisdictions, datasets, laboratories) naturally outgrow the cap; the failure message (`EFRONTMATTER: relations exceeds maximum relation count`) gives no mitigation. The result is that content authors drop *real* relationships to satisfy the limit, and the graph model silently understates the site's connectivity.
- **Verified (boris/0.8.1, 2026-08-09):** `max_relation_count: usize = 16` is a compile-time constant and relations live in a fixed `[16]SemanticRelation` array (`src/page.zig`). Fixture tests: 17 distinct relations → `EFRONTMATTER: relations exceeds maximum relation count`; 16 → builds. Raising the cap is a code change, not configuration.
- **Real-world evidence:**
  - `docs/device-taxonomy-migration.md`: a manufacturer record with 23 devices exceeded the cap; the reciprocal `relates_to` list was removed and device links moved into prose tables validated by a separate link-audit script.
  - The same document instructs future authors: "Do not re-add a per-device relation list to a manufacturer page; it does not scale past 16 devices and adds no graph information."
- **Current workaround:** drop relations; encode links in prose; add a Markdown-link audit to compensate.
- **Desired behavior:** The cap is removed or configurable (with a sane default), so a hub page can carry as many relations as its content requires. Performance and rendering bounds should be solved in the render layer (see BORIS-01), not by truncating the data model.
- **Acceptance criteria:**
  1. A page with >16 relations compiles and renders.
  2. The number of relations per page is configurable per project (or unbounded).
  3. Docs state the behavior and the recommended pattern for high-degree hubs (e.g. relation pages/pagination).
- **Affected project files:** `docs/device-taxonomy-migration.md` (the workaround narrative), `content/manufacturers/TMFR-0004.md` (dropped relations), `scripts/dcc_sync.py` (`relations_for_category` exists to stay under the cap).
- **AI-attractor factor:** HIGH — an agent hitting the cap will write a helper or drop edges rather than question the limit.

---

## BORIS-03 — Relation kinds are a closed 4-item vocabulary; rich typed relations require a parallel registry

- **Priority:** P1
- **Classification:** Boris extension (configurable relation kinds)
- **Problem:** Only `relates_to`, `implements`, `depends_on`, `supersedes` are allowed (verified against source, boris/0.8.1). Real content needs typed edges like `product_claims_cultivar`, `batch_claims_cultivar`, `claimed_lineage_parent`, `claimed_bred_by`, `listed_by`, `sold_by`, `tested_by`, `analyte_result`, `observed_in_reports`. Because the vocabulary cannot be extended, this project maintains a separate JSONL claim registry (`metadata/cultivar-claims.jsonl`) with its own validation, and a Python layer to render those edges.
- **Real-world evidence:** `scripts/cultivar_claims.py` docstring: "The published Boris graph only supports four relation kinds … The rich claim vocabulary in this module therefore lives in a machine-readable registry."
- **Current workaround:** parallel registry + registry validator + derived-navigation renderer; the graph Boris sees is a subset of the real graph.
- **Desired behavior:** The relation-kind vocabulary is extensible via project config/schema (kinds carry a name and, optionally, endpoint-role constraints), with unknown kinds rejected only when they are not declared.
- **Acceptance criteria:**
  1. A project can declare additional relation kinds in a config file.
  2. Declared kinds pass `boris check`; undeclared kinds still fail with a message naming the allowed set.
  3. The consuming project can express `product_claims_cultivar` as a first-class relation and retire the JSONL registry for entity-to-entity claims.
- **Affected project files:** `metadata/cultivar-claims.jsonl`, `scripts/cultivar_claims.py`, `scripts/validate_cultivar_claims.py`, `scripts/crosslinks.py` (edge classes).
- **AI-attractor factor:** HIGH.

---

## BORIS-04 — No structured-data concept alongside prose; every dataset must become Markdown

- **Priority:** P1
- **Classification:** core (data files) / extension (generate-from-data hook)
- **Problem:** Boris's only input is Markdown. There is no way to attach a JSON/CSV dataset to a page or collection and render it. This repository converts entire regulator datasets into generated Markdown pages (thousands of lines of page-generation code), and durable records that are *not* pages (measurements, claims) live in project-owned JSONL files Boris never reads.
- **Real-world evidence:**
  - `scripts/ingest/markdown.py` reimplements the Boris content grammar (frontmatter, escaped tables, callouts, wiki-links, deflists, footnotes, task lists) so generators can emit valid input.
  - `scripts/dcc_ingest.py` (1,658 lines), `scripts/dcc_sync.py` (447), `scripts/state_ingest.py` + `scripts/ingest/states/massachusetts.py` (2,528) exist substantially to produce Markdown from data.
  - **PR #28 added a third, independent renderer**: `scripts/testing_requirements.py` (141 lines) treats `data/testing-requirements/<state>.json` as the source of truth and renders `content/requirements/TREQ-*.md` as "a derived view" — hand-building Boris frontmatter incl. `relations:` lists without reusing `ingest/markdown.py`. Same pressure, new script, no Boris issue.
  - `metadata/coa-records.jsonl`, `metadata/cultivar-claims.jsonl`, and `data/source-manifests/*.json` are only consumable by project Python; `scripts/crosslinks.py` renders the JSONL ones by HTML injection.
- **Current workaround:** generate Markdown at ingest time; maintain side registries for non-page data.
- **Desired behavior:** A page or collection can reference structured data files; templates can iterate rows with escaping; the render pass handles data + prose coherently. Alternatively, a documented, first-class "generate pages from data" extension point with deterministic regeneration.
- **Acceptance criteria:**
  1. A data file (JSON/CSV) attached to a page is validated and renderable from a template.
  2. The repository can express its license/measurement/claim registries as data without writing a page generator per dataset.
  3. Regeneration is deterministic and no side registries are required for entity-to-entity facts.
- **Affected project files:** `scripts/ingest/markdown.py`, `scripts/dcc_ingest.py`, `scripts/dcc_sync.py`, `scripts/ingest/states/massachusetts.py`, `metadata/coa-records.jsonl`, `metadata/cultivar-claims.jsonl`.
- **AI-attractor factor:** HIGH.

---

## BORIS-05 — No content-validation API; projects reimplement validation as separate scripts

- **Priority:** P1
- **Classification:** core (validation API) / extension (validator plugin)
- **Problem:** The closed frontmatter schema prevents unknown keys but provides no surface for content *semantics*: controlled tag vocabularies, mutually exclusive tags, required sections/rows, relation-type constraints, canonical-ID requirements. This project runs six Python auditors in its build gate, each re-parsing frontmatter with regexes.
- **Real-world evidence:**
  - `scripts/audit_device_taxonomy.py` (TAX-01..05, ADV-01/02), `scripts/audit_record_completeness.py` (REC-01..06), `scripts/audit_coa_content.py` (COA-01..07), `scripts/validate_cultivar_claims.py`, `scripts/validate_crosslinks.py`, `scripts/ingest/validation.py`.
  - The vocabulary they enforce lives in `metadata/device-taxonomy.json`, which must stay in sync with the published standard page `content/reference/TREF-0004.md`.
- **Current workaround:** one Python auditor per rule-set, wired into `bin/validate_graph.sh` by hand, each with its own exit codes.
- **Desired behavior:** A validation surface inside `boris check` (declarative schema rules: allowed tag values, required sections, relation endpoint roles, cross-field invariants) or a plugin interface with a stable findings format.
- **Acceptance criteria:**
  1. A project can declare "tag X and tag Y are mutually exclusive" or "collection C requires section S" declaratively.
  2. Violations surface through `boris check` with the same findings format as graph diagnostics.
  3. The consuming project's gate is one command instead of eight.
- **Affected project files:** `bin/validate_graph.sh`, the five auditor scripts, `metadata/device-taxonomy.json`, `metadata/coa-measurement.schema.json`.
- **AI-attractor factor:** HIGH.

---

## BORIS-06 — No canonical ID policy; projects build their own ID registries (twice)

- **Priority:** P1
- **Classification:** Boris core (ID uniqueness/validation) with docs for migration
- **Problem:** Boris accepts an `id` field but provides no identity policy, allocation, collision detection, or migration record. This project built two independent registries (`scripts/ted_ids.py` → `metadata/id-map.jsonl`; `scripts/ingest/ids.py` `NaturalKeyRegistry` → `data/massachusetts-ccc/id-map.json`) with different allocation rules, plus a committed generated migration map and a documented renumbering hazard (deleting a collection's anchor file silently renumbers its satellites).
- **Real-world evidence:**
  - `docs/status.md`: "Canonical CLI and global ID allocation are unresolved."
  - `reports/placeholder-disposition.md`: anchor-file deletion renumbers collections.
  - `metadata/id-map.jsonl` is a generated file deliberately committed; four other tools parse it.
  - **PR #28 hit the collision live** (`reports/jurisdiction-pipeline-audit.md` §8): a fresh Massachusetts `NaturalKeyRegistry` would allocate `jurisdictions/TJUR-0001` on top of California's, and the same for every shared prefix (TLIC, TSTL, TDTS, TREQ, TCNT, TORG…); the fix was project-side seeding of the registry from existing content plus create-if-missing trunk writes. The two-allocator problem is documented in the same report as "a future consolidation item" — still no Boris surface.
- **Current workaround:** project-owned allocation scripts + committed generated map + manual regeneration discipline.
- **Desired behavior:** Boris validates ID uniqueness/format per project policy and offers a documented, single migration story (or the project consolidates on one registry with Boris-agnostic helpers).
- **Acceptance criteria:**
  1. Boris reports duplicate or malformed IDs with actionable messages.
  2. There is one documented way to keep a stable migration record across renames.
  3. The consuming project can delete one of its two registries.
- **Affected project files:** `scripts/ted_ids.py`, `scripts/ingest/ids.py`, `metadata/id-map.jsonl`, `data/massachusetts-ccc/id-map.json`, `metadata/id-policy.json`.
- **AI-attractor factor:** HIGH.

---

## BORIS-07 — No build lifecycle hooks; pre/post steps are shell concatenation

- **Priority:** P2
- **Classification:** Boris extension (hooks/plugins)
- **Problem:** Everything before or after the render pass is a shell wrapper. This project's `ted-build.sh` sequences: ID check → link audit → compile → HTML injection → HTML-ID audit → proof-check → header copy → release audit. The post-render injection is regex HTML surgery because there is no hook between render and write.
- **Real-world evidence:** `scripts/ted-build.sh` (89 lines of sequenced steps); `scripts/crosslinks.py --inject`; `scripts/audit_html_ids.py` (validates rendered output because nothing else does).
- **Current workaround:** a growing bash wrapper.
- **Desired behavior:** Named lifecycle phases (before-build, after-render, after-write) with a hook/plugin interface so project steps are declared and ordered by the compiler.
- **Acceptance criteria:**
  1. A project can register an after-render hook without wrapping the whole binary in bash.
  2. Hooks receive stable context (page list, output dir) and a documented failure contract.
- **Affected project files:** `scripts/ted-build.sh`, `scripts/ted-publish.sh`, `bin/validate_graph.sh`, `scripts/crosslinks.py`.
- **AI-attractor factor:** MEDIUM-HIGH.

---

## BORIS-08 — `boris check` diagnostics are noisy and undocumented; projects filter them by hand

- **Priority:** P2 (findings format/docs P4)
- **Classification:** core (diagnostics quality) + docs
- **Problem:** On a healthy site, `boris check` emits hundreds of `unreferenced_page` findings (mostly intentional: collection trunks, changelog records). The project filters that code out — twice — with no documented findings schema, severity levels, or way to exempt intentional cases.
- **Real-world evidence:**
  - `bin/validate_graph.sh` filters `.code != "unreferenced_page"`.
  - `scripts/dcc_ingest.py` (line ~1302) re-implements the identical filter.
  - **Verified (boris/0.8.1, 2026-08-09):** on the live 417-page tree, `boris check` reports **382 of 417 pages (91.6%)** as `unreferenced_page` — all 26 roots and 356 satellites — far above the ~178 figure in the historical reports (measured when the tree was ~207 entities). The findings JSON is written to **stderr**, not stdout (undocumented; the project discovered this and captures `2>file`). The rule is documented in Boris's `docs/contracts/documentation-intelligence.md` (excludes a page's own `parent`), so it is not mysterious to Boris — but it is undiscoverable to a consumer, who must reverse-engineer the findings shape and the tolerated baseline.
- **Current workaround:** project-side filtering of the JSON findings output (reverse-engineered).
- **Desired behavior:** Findings have a documented schema; `unreferenced_page` (or any code) is configurable/declaratively excludable per page or collection; severity levels exist so "informational" findings do not read as failures.
- **Acceptance criteria:**
  1. The findings JSON format is documented with code list and severities.
  2. A page can opt out of a specific diagnostic (e.g. `unreferenced_page`) declaratively.
  3. The consuming project deletes its duplicated filter.
- **Affected project files:** `bin/validate_graph.sh`, `scripts/dcc_ingest.py`, `docs/device-taxonomy-migration.md` (mentions diagnostics).
- **AI-attractor factor:** MEDIUM.

---

## BORIS-09 — Default layout rules per collection require enumerating every collection in the build command

- **Priority:** P3
- **Classification:** core (small) / docs
- **Problem:** Layout selection for satellites is done with one explicit `--layout-rule default glob:<collection>/*` flag per collection — 14 flags in the build script (3 of them dead: `releases/*`, `safety/*`, `specs/*` never existed as directories). Adding a collection means editing the build script in three places (content dir, ID prefixes, layout flags). The `role:satellite` selector cannot replace the globs as a pure refactor: it is not collection-scoped, and the current build assigns two different layouts to satellites (11 authored collections → compact; 11 generated collections → default main, which alone carries the "Regulation & Public Data" nav group). A full-site rebuild confirmed a global `role:satellite → compact.html` rule changes 268 pages.
- **Real-world evidence:** `scripts/ted-build.sh` contained 14 `--layout-rule default glob:…` lines; git history shows the glob list accreted (7 at init → 14) while the generated collections were never added; verified by rebuild (2026-08-09). The three dead globs (`releases/*`, `safety/*`, `specs/*`) were removed the same day with byte-identical output confirmed.
- **Current workaround:** hand-maintained flag list.
- **Desired behavior:** A per-collection default layout (declared in content/config) or a documented glob/default syntax so the build command stays stable as collections grow; alternatively a collection-scoped role selector (e.g. `role:satellite` constrained to a collection) so the two-tier assignment is expressible without globs.
- **Acceptance criteria:**
  1. Adding a new collection does not require editing the build command.
  2. Docs describe how a collection declares its layout.
  3. A project can assign different layouts to different satellite collections without enumerating them.
- **Affected project files:** `scripts/ted-build.sh`, `scripts/dcc_ingest.py` (schema report notes the flat-collection constraint).
- **AI-attractor factor:** MEDIUM.

---

## BORIS-10 — No binary releases; every consumer reimplements provisioning

- **Priority:** P3 (ecosystem)
- **Classification:** release engineering (not compiler core)
- **Problem:** Boris ships only source; consumers must pin a commit, download a specific Zig toolchain (checksummed), and compile. This repository implements that in a 337-line provisioner (`scripts/ensure-boris.sh`) with a version manifest and checksums, a provisioner test suite, and a *third* clone-and-build in CI.
- **Real-world evidence:** `scripts/ensure-boris.sh`, `metadata/boris-version.json`, `scripts/test_ensure_boris.py`, `.github/workflows/ci.yml` and `deploy.yml` (both clone + `zig build`).
- **Current workaround:** per-project provisioning.
- **Desired behavior:** Official binary releases (or a canonical provisioner) keyed by version, so projects pin a release instead of a source build.
- **Acceptance criteria:**
  1. A documented release artifact exists (per platform) that a project can download and verify.
  2. The consuming project's provisioner shrinks to a fetch + checksum + execute.
- **Affected project files:** `scripts/ensure-boris.sh`, `scripts/clean-binaries.sh`, `scripts/test_ensure_boris.py`, `.github/workflows/*.yml`.
- **AI-attractor factor:** MEDIUM (the workaround already exists; new projects will copy it).

---

## BORIS-11 — Documentation: frontmatter reference missing limits, kinds, and messages

- **Priority:** P4
- **Classification:** docs
- **Problem:** The relation cap (16), the allowed relation kinds, and the layout-rule surface are discoverable only by build failure or by reading project docs. Unknown relation kinds fail without naming the allowed set.
- **Real-world evidence:** `docs/device-taxonomy-migration.md` documents the cap only after the project hit it; `scripts/crosslinks.py` re-encodes the 4-kind list because the project had to discover it.
- **Desired behavior:** A frontmatter reference page covering: allowed fields, relation kinds, the cap and how to change it, layout rules, and failure messages that state the allowed values.
- **Affected project files:** `AGENTS.md`, `rules.md`, `scripts/ted_ids.py` (prefix table) would cite it.
- **AI-attractor factor:** MEDIUM (a documented reference reduces reverse-engineering).

---

## BORIS-12 — Documentation: canonical data-driven-pages and derived-navigation recipes

- **Priority:** P4
- **Classification:** docs / examples
- **Problem:** Two capabilities the project needed — rendering structured data into pages, and derived navigation (backlinks/related) — have no canonical Boris pattern, so agents invent pipelines and post-processors.
- **Real-world evidence:** the entire `scripts/ingest/` page-generation stack and `scripts/crosslinks.py` exist because no recipe existed.
- **Desired behavior:** Official recipes ("How to publish a dataset", "How to render related pages") with a fixture site, so future projects follow the blessed pattern.
- **Acceptance criteria:** a newcomer can implement a dataset page and a related-pages section without writing a Markdown generator or an HTML post-processor.
- **AI-attractor factor:** HIGH (recipes directly reduce script invention).

---

## BORIS-13 — Link validation: `boris check` reports no link findings, and the built-in output audit silently ships broken `.md` hrefs

- **Priority:** P2
- **Classification:** core (small) + docs
- **Problem:** Boris's only link validation is a post-render audit (`src/link_audit.zig`) that runs immediately before publishing and **deliberately skips literal `.md`/`.mdx` targets** (a documentation-links contract: it leaves them "byte-for-byte unchanged"). `boris check` reports no link findings at all. A broken `[x](missing.md)` therefore compiles, renders, and ships as a literal `href="missing.md"` 404. None of this is discoverable from a consuming project; this project wrote its own `audit_markdown_links.py` to catch exactly the case Boris skips.
- **Verified (boris/0.8.1, 2026-08-09):** fixture tests — broken `href="missing.html"` fails the build (`EROUTEMISSING … does not resolve to a published output` → `LinkAuditFailed`); broken `[x](missing.md)` builds and ships byte-for-byte; broken asset href fails. `boris check` emits no link findings.
- **Current workaround:** `scripts/audit_markdown_links.py` (source-level) + `scripts/validate_crosslinks.py` CXL-01 for injected `.html` links (needed because injection runs *after* Boris's audit).
- **Desired behavior:** (a) document the output link audit and its `.md`-skip contract so consumers know what is and is not checked; (b) warn on literal `.md` hrefs in site output (or provide an opt-in strict mode); (c) optionally surface link findings through `boris check`.
- **Acceptance criteria:**
  1. The `.md`-skip behavior is documented where consumers look (CLI help, contract docs shipped with the binary).
  2. A broken `.md` link either fails the build or produces a check finding in strict mode.
  3. The consuming project can delete `audit_markdown_links.py` without losing coverage.
- **Affected project files:** `scripts/audit_markdown_links.py`, `scripts/validate_crosslinks.py` (CXL-01), `scripts/ted-build.sh`.
- **AI-attractor factor:** LOW-MEDIUM (the existing script is justified; the risk is future projects re-inventing it or assuming `boris check` covers links).
