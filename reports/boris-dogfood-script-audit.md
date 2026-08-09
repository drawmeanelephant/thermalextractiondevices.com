# Boris Dogfood Script Audit

**Scope:** All project-local automation in `thermalextractiondevices.com` (scripts, generators, ingestion utilities, validators, migration helpers, build wrappers, CI commands).
**Method:** Documentation-only. No scripts were modified, no bugs were fixed, no features were implemented. Every finding records *why a script exists* and what it says about Boris.
**Commit audited:** `3095c04` (github/main, 2026-08-09); **updated through `4a7b241`** (PR #28, jurisdiction-pipeline-infra) to incorporate the 5 scripts and 2 test modules that PR merged. Counts below reflect the updated tree.

**Empirical verification:** The pinned Boris binary (`9505ec6`, boris/0.8.1) was
provisioned via the repo's own `scripts/ensure-boris.sh --provision` and the
open questions in the original audit were answered empirically with fixture
sites (see **Appendix B — Empirical Verification Results**). Several
conclusions changed as a result; the changed findings are marked with
“🔬 verified”.

---

## Executive Summary

**50 automation units inspected** (46 files under `scripts/`, `bin/validate_graph.sh`, `preview.sh`, and 2 GitHub Actions workflows), plus 22 test modules (≈266 tests) and the git history that explains why the tooling exists.

| Count | Category |
| --- | --- |
| 23 | Legitimate domain tooling / source acquisition (DCC/CCC pipelines, ingest package + evidence/sources/testing-requirements models, COA models, research queues, dev convenience) — belongs in this repo |
| 4 | Generic *release/governance* audits (PII/secrets/history/headers) — arguably reusable outside Boris, not a Boris gap |
| 17 | Boris-adjacent (compensating for a Boris limitation, ergonomics gap, or missing feature — see the pressure clusters) |
| 6 | Boris *ecosystem* friction (compiler acquisition/provisioning: `ensure-boris.sh`, CI/deploy clone-and-build) |
| 0 | Scripts deleted, renamed, or cleaned up by this audit (the 3 dead layout globs were removed separately at the maintainer's request) |

50 total automation units. The categories are a primary-classification split; several scripts legitimately straddle two (e.g. `dcc_sync.py` is acquisition *and* content generation; `cultivar_claims.py` is a domain model whose existence was forced by the 4-kind relation vocabulary; `testing_requirements.py` is a data validator whose *render* half is Boris-adjacent).

**Biggest recurring architectural pressures (evidence-backed):**

1. **Relation model** — Boris caps `relations` at **16 per page** (`max_relation_count`, boris/0.8.1), supports only **4 relation kinds** (`relates_to`, `implements`, `depends_on`, `supersedes`), and **exposes none of the graph to templates**. This single cluster produced the largest script in the repo (`scripts/crosslinks.py`, 1,710 lines), a parallel claim registry (`metadata/cultivar-claims.jsonl`), a second navigation vocabulary, hand-maintained bidirectional relation pairs, and 90+ hand-written "Related pages" sections in content.
2. **Structured data** — there is no Boris concept of structured data alongside prose. Every dataset must become Markdown pages; durable measurement/claim records live in project-owned JSONL side registries that only project Python can read and render.
3. **Schema-aware validation** — the closed 6-key frontmatter schema cannot express controlled vocabularies, required sections, relation-type rules, or record-completeness floors, so the project re-implemented content validation as six Python auditors with two JSON vocabularies.
4. **Stable canonical IDs** — Boris accepts an `id` field but provides no identity management; the project built two independent ID registries (`metadata/id-map.jsonl` via `ted_ids.py`, and `data/massachusetts-ccc/id-map.json` via `NaturalKeyRegistry`), a committed generated migration map, and documented a renumbering hazard.
5. **Build lifecycle** — everything that must run before or after Boris is bolted on with shell wrappers; the project has built its own post-render HTML injection pipeline (with its own pagination, index pages, and link validation).

**Highest-risk workaround:** `scripts/crosslinks.py` HTML injection. It is a post-render, regex-based splice into generated HTML (including copying a page's layout shell to fabricate paginated index pages). It is deterministic and well-tested today, but it is the clearest evidence that the project has quietly built *a second rendering layer on top of Boris*.

**Highest-value Boris improvement:** Give templates access to the relation graph (or provide an official derived-navigation/reverse-edge feature). That single change would retire the largest, most generic, most recently-added script in the repository.

---

## Actual Build Pipeline

The real pipeline, reconstructed from `ted-build.sh`, `validate_graph.sh`, `ci.yml`, `deploy.yml`, `cloudflare-build.sh`, and the reports:

```text
external sources (DCC API, CCC CSVs, COA PDFs)
        │
        ▼
retrieval scripts          dcc_ingest.py, dcc_sync.py, state_ingest.py
        │                  + ingest/{fetch,storage,schema,core}.py   (checksums, guards, provenance)
        ▼
normalization              ingest/states/massachusetts.py, coa_model.py, cultivar_profiles.py,
        │                  ingest/evidence.py + sources.py + testing_requirements.py (PR #28)
        ▼
generated Markdown         ingest/markdown.py (frontmatter + Apex dialect), dcc_sync.py build_record(),
        │                  testing_requirements.py --render (hand-built frontmatter + relations)
        │                  → content/**/*.md  (also hand-edited editorial content)
        ▼
ID normalization           ted_ids.py  →  metadata/id-map.jsonl (committed, regenerated)
        │
        ▼
link pre-check             audit_markdown_links.py
        │
        ▼
BORIS (Zig compiler, pinned commit 9505ec6, "afterparty" branch)
   ├── check (graph diagnostics)  ← wrapped by validate_graph.sh, which filters baseline findings
   ├── HTML build (+ 14 explicit --layout-rule globs, one per collection)
   ├── sitemap / site-url
   └── proof/checks.json, IR/RAG/context/llms exports (ted-publish.sh)
        │
        ▼
POST-PROCESSING (all project-local, after Boris renders)
   ├── crosslinks.py --inject   (re-derives the graph in Python, injects navigation HTML, builds paginated index pages by splicing layout shells)
   ├── audit_html_ids.py        (duplicate id= audit on rendered HTML)
   ├── cp _headers              (security manifest copy into dist)
   └── audit_public_release.py  (PII/secret/history/gitignore/header audits; previously blocked on data/dcc)
        │
        ▼
validation gates               bin/validate_graph.sh (ted_ids → taxonomy → COA → completeness → claims → crosslinks → boris check → build)
        │
        ▼
deploy                         Cloudflare Pages via deploy.yml (re-runs the whole chain)
```

Per-step Boris-boundary question and answer:

| Step before/after Boris | Why is Boris not doing this? | Classification |
| --- | --- | --- |
| Source retrieval, checksumming, normalization | Regulator-specific acquisition; genuinely outside a static-site compiler | Correctly outside Boris |
| Markdown generation from structured data | Boris has no data-file concept and no content-generation API; the *only* input is Markdown | Should probably be a Boris extension point (data files / generate hook) — partially "should probably be Boris" for the *rendering* side |
| `ted_ids.py` ID normalization/allocation | Boris accepts `id:` but owns no identity policy, allocation, or migration record | Should probably be Boris (ID policy is generic) |
| `audit_markdown_links.py` pre-check | Boris has a `check` command; whether it validates local Markdown links is undocumented — the project did not discover/trust it | Uncertain — could be "Boris can already do it" (discoverability) or a genuine gap |
| Layout selection (14 `--layout-rule` globs) | Boris supports layout rules but apparently not a default-glob; every new collection requires editing `ted-build.sh` | Should probably be Boris (or docs for an existing glob syntax) |
| `boris check` diagnostic filtering | Boris emits ~178 `unreferenced_page` findings on a healthy site; the project filters them in `validate_graph.sh` and again in `dcc_ingest.py` | Boris diagnostics gap (noise / undocumented baseline) |
| `crosslinks.py` HTML injection | Boris renders no reverse edges/backlinks/related sections and exposes no graph data to templates | Should probably be Boris (generic) — this is the big one |
| `audit_html_ids.py` | Post-render check on generated HTML; Boris has no post-render hook and no output validation | Should probably be a Boris extension point (output hook) |
| `audit_public_release.py` etc. | Repository governance (PII, secrets, history blobs); not a compiler concern | Correctly outside Boris |

---

## Script Inventory

Legend — **manual**: run by a person; **auto**: wired into `validate_graph.sh` / `ted-build.sh` / CI / deploy. **Boris-adjacent** = reads/writes Boris source content, reproduces Boris output, wraps Boris, or compensates for a Boris limit. Size is lines of code.

### Build / pipeline wrappers

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/ted-build.sh` | bash | 89 | Production HTML build: ID check → link audit → Boris compile (14 layout rules) → crosslinks injection → HTML-ID audit → proof check → copy `_headers` → release audit | `content/`, theme, `_headers` | `dist/cantilever/` | auto (CI, deploy, preview, validate_graph) | yes | writes only `dist/` | yes (wraps Boris + all post-steps) | Boris has no build pipeline / hooks; every pre/post step needs a wrapper | Medium: layout rules must be extended by hand per collection; audit hook is hand-rolled fail-closed logic |
| `scripts/ted-publish.sh` | bash | 56 | Export HTML, IR, RAG, Context, llms.txt + release audits + claims.jsonl | `content/` | `publish/` | manual / release | no | writes only `publish/` | yes | Boris has no "publish bundle" orchestration; each export is a separate CLI flag | Low |
| `bin/validate_graph.sh` | bash | 49 | The validation gate: ted_ids → device-taxonomy → COA content → completeness → cultivar claims → crosslinks → **boris check (with `unreferenced_page` filter)** → full build | content, metadata | pass/fail | auto (CI, deploy, cloudflare-build) | yes (CI gate) | no | yes | Boris `check` output needs filtering; the gate accumulates one step per project audit | Medium: grows per audit; duplicates `dcc_ingest.py`'s own filter |
| `preview.sh` | bash | 12 | Build + serve on :8000 | — | dist/preview | manual | no | no | yes | Convenience wrapper around `ted-build.sh` + `http.server` | Low |
| `scripts/cloudflare-build.sh` | bash | 21 | Legacy CF build entry: provision Boris → validate → build | — | dist/cantilever | manual/legacy | no (deploy.yml supersedes) | no | yes | Wrapper; overlaps CI/deploy | Low; superseded by workflows |

### Boris acquisition / provisioning (ecosystem friction)

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/ensure-boris.sh` | bash | 337 | Resolve or provision Boris at pinned commit: check `BORIS_BIN` → verify manifest → sibling repo → download Zig (checksummed) → clone + build Boris | `metadata/boris-version.json` | `bin/boris` + `bin/boris.json` manifest | auto (validate_graph, ted-build, state_ingest) | yes (resolves compiler) | removes `.tools/boris-build` | yes | Boris ships no binary releases; every consumer must build from a pinned Zig commit | Medium: 337 lines of toolchain logic; duplicates CI's clone+build steps |
| `scripts/clean-binaries.sh` | bash | 35 | Delete provisioner artifacts | — | cleaned bin/.tools | manual | no | **yes (deletes bin/boris, .tools)** | yes | Companion to ensure-boris | Low |
| `scripts/test_ensure_boris.py` | python | 102 | Unit tests for the provisioner | — | test results | test | no | no | yes | Boris provisioning is complex enough to need its own test suite | Low |
| `.github/workflows/ci.yml` / `deploy.yml` | yaml | 69/81 | CI validates and deploys; both clone+build Boris from the afterparty branch | repo | site | auto | yes | no | yes | Boris has no CI-friendly binary; the acquire-and-build step is reimplemented a **third** time here | Medium: three copies of "get Boris" (ensure-boris.sh, ci.yml, deploy.yml) |

### Identity tooling

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/ted_ids.py` | python | 350 | Normalize/validate/allocate `<collection>/<PREFIX>-NNNN` entity IDs; detect collisions; write/validate `metadata/id-map.jsonl` migration map | `content/`, existing map | validated IDs; `--write` rewrites frontmatter `id:` and the map | auto (every build, validate_graph, state_ingest) | yes (pre-build) | `--write` mutates content files and the committed map | yes | Boris accepts `id:` but has no identity policy, allocation, migration record, or collision detection | Medium: the committed generated map can drift; anchor-file deletion renumbers a collection (documented in reports/placeholder-disposition.md) |
| `scripts/ingest/ids.py` | python | 195 | `NaturalKeyRegistry`: stable natural-key → Boris entity ID with tamper-detection digest | source natural keys | `data/massachusetts-ccc/id-map.json` | auto (state_ingest) | no (content gen) | no | yes | A **second, independent** ID registry because ingest needs persisted natural-key mapping; must be kept collision-free against `ted_ids.py` | High: two ID systems; docs/status.md itself flags "global ID allocation… unresolved" |
| `metadata/id-policy.json` | json | — | Documents the ID scheme | — | — | read by agents | no | no | yes | The ID scheme is project policy, not Boris | Low |
| `metadata/id-map.jsonl` | jsonl | generated | Entity registry + migration record | ted_ids.py | consumed by crosslinks, audits, publish | auto | yes | regenerated | yes | Generated file deliberately committed; crosslinks and three auditors parse it | Medium: hand-edit prohibition; regeneration ordering |

### Validation / audit tooling

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/audit_markdown_links.py` | python | 52 | Check local `](...)` links resolve | `content/` | findings | auto (ted-build, state_ingest) | yes | no | yes | yes | Validates the prose-table fallback that replaced dropped relations; Boris link-checking not used/trusted | Low |
| `scripts/audit_html_ids.py` | python | 51 | Duplicate `id=` audit on rendered HTML | `dist/` | findings | auto (ted-build) | yes | no | yes | Boris post-render output is unvalidated | Low |
| `scripts/audit_device_taxonomy.py` | python | 170 | Enforce device taxonomy tags (TAX-01..05, ADV-01/02) against `metadata/device-taxonomy.json` | content, vocab | findings | auto (validate_graph) | yes | no | yes | Closed frontmatter schema cannot express controlled vocabulary or contradiction rules | Medium: rules live in JSON, must stay in sync with reference/TREF-0004 content page |
| `scripts/audit_record_completeness.py` | python | 175 | Enforce the device record-completeness floor (REC-01..06) | content, vocab | findings | auto (validate_graph) | yes | no | yes | Same: required-sections/rows rules have no Boris surface | Medium |
| `scripts/audit_coa_content.py` | python | 224 | Enforce COA content contract (COA-01..07): canonical ids, demo labeling, provenance sections, no chemistry on cultivar pages | content, id-map | findings | auto (validate_graph) | yes | no | yes | Content-level invariants the frontmatter schema cannot hold | Medium |
| `scripts/validate_cultivar_claims.py` | python | 55 | Validate claim registry against content entity IDs | content, claims | findings | auto (validate_graph) | yes | no | yes | The claim vocabulary is not expressible in Boris relations | Medium |
| `scripts/validate_crosslinks.py` | python | 118 | Validate the derived navigation graph (CXL-01..12) | content, id-map, claims, coa | findings | auto (validate_graph, ted-build) | yes | no | yes | Validates the layer built *because* Boris renders no navigation | Medium |
| `scripts/audit_common.py` | python | 230 | Shared finding/config model for the release audits | config | — | imported | yes (via audits) | no | yes | Shared plumbing for the audit family | Low |
| `scripts/audit_public_release.py` | python | 248 | Orchestrated release readiness (secrets, PII, provenance, gitignore, headers, human review) | repo, config | findings / JSON report | auto (ted-build, publish, CI) | yes | no | no | Repository governance; deliberately outside Boris | Low |
| `scripts/audit_sensitive_content.py` | python | 413 | Secrets/PII/path scanning incl. git history | repo, config | findings | auto (CI, publish) | yes | no | no | Release governance | Low |
| `scripts/audit_large_files.py` | python | 376 | Large tracked files, reachable history blobs, duplicates, cleanup plan | repo, config | findings / report | auto (CI, publish) | yes | no | no | Release governance + history hygiene | Low |

### Crosslinking / navigation layer (the core Boris-pressure cluster)

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/crosslinks.py` | python | 1710 | Re-parse frontmatter relations + claim registry + COA records; build a typed edge graph; derive backlinks/related/multi-hop sections; **inject HTML into rendered pages**; generate **paginated index pages by copying layout shells**; emit machine + RAG exports | content, id-map, claims, coa | `exports/crosslinks.json`, `exports/crosslinks-rag.md`, injected `dist/` pages, index pages | auto (ted-build) | yes | writes only `dist/` + `exports/` | yes | yes | Boris renders no reverse edges/backlinks, and templates cannot access the relation graph | High: 1,710 lines; regex HTML surgery; its own pagination/index system; its own validation |
| `scripts/validate_crosslinks.py` | python | 118 | Gate for the above | — | findings | auto | yes | no | yes | As above | Medium |

### Content-generation / ingestion (domain + Boris boundary)

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/dcc_ingest.py` | python | 1658 | California DCC pipeline: fetch license registry, recalls, labs; checksum private payloads; generate Markdown collections; write manifests/reports; run Boris gates | DCC APIs | content collections (licenses, orgs, labs, recalls, contaminants, datasets, requirements), data/dcc manifest | manual | no (generated content is committed) | writes content pages + data/dcc | partial | Regulator-specific acquisition (legitimate) + **Markdown generation to feed Boris** | High: 1,658 lines; private-source dependence; the only reason DCC pages exist |
| `scripts/dcc_sync.py` | python | 447 | DCC license-registry segment sync + law-and-use summary records; `relations_for_category()` hardcodes the same 3-4 relations | DCC API | content/law-and-use/*.md, data/dcc snapshots | manual | no | overwrites its own records in place | yes | Acquisition + generation; the hardcoded relations must "stay in sync" with published records | Medium: `relations_for_category` is a divergence hazard (documented in reports/graph-connectivity.md) |
| `scripts/state_ingest.py` | python | 283 | Canonical CLI for state ingestion (fixtures-only guard, dataset selection, gates) | — | reports, content | manual | no | guarded | yes | CLI for the ingest package | Low |
| `scripts/ingest/__init__.py` | python | 9 | Package marker | — | — | — | — | no | yes | no | plumbing | Low |
| `scripts/ingest/core.py` | python | 276 | Dates, change reports, errors, misc | — | — | imported | no | no | yes | no | shared ingest primitives | Low |
| `scripts/ingest/fetch.py` | python | 270 | HTTP fetcher with retries, content-type guards, streaming, fixture mode | URLs | bytes/checksums | imported | no | no | yes | no | acquisition | Low |
| `scripts/ingest/storage.py` | python | 192 | Immutable SHA-256 raw snapshots, durable manifest | raw bytes | var/ingest + data/<state>-ccc | imported | no | no | yes | no | provenance storage | Low |
| `scripts/ingest/schema.py` | python | 339 | CSV/JSON readers, schema drift, row-collapse, duplicate-key, date-regression guards | CSVs | rows/errors | imported | no | no | yes | no | data-integrity guards | Low |
| `scripts/ingest/diff.py` | python | 125 | Snapshot revision comparison (status vs numeric) | two snapshots | DiffResult | imported | no | no | yes | no | change reporting | Low |
| `scripts/ingest/ids.py` | python | 195 | NaturalKeyRegistry (see Identity tooling) | — | — | imported | no | no | yes | yes | second ID registry | High |
| `scripts/ingest/markdown.py` | python | 145 | **Renders Boris frontmatter + Apex Markdown dialect** (escaped tables, callouts, wiki-links, deflists, footnotes, task lists) | data | Markdown strings | imported | no | no | yes | yes | Reimplements the Boris content grammar so generators can emit valid input; only `relates_to` is ever emitted | Medium: hand-maintained mirror of Boris's grammar |
| `scripts/ingest/validation.py` | python | 206 | Privacy field/value scans; relation-target validation; entity-id collection | content | findings | imported | no | no | yes | yes | Privacy policy + re-implemented relation checks | Medium |
| `scripts/ingest/states/massachusetts.py` | python | 2528 | Full Massachusetts CCC adapter: 15 datasets, normalizers, advisories, page-generation policy, 10 collections of generated pages | CCC CSVs/HTML | generated content, manifests, reports | manual (state_ingest) | no | guarded (fixture block) | yes | partial | Regulator-specific acquisition + **generated Markdown for Boris** | High: 2,528 lines; the largest file in the repo; still the only live-verified state adapter |
| `scripts/coa_model.py` | python | 1316 | Durable measurement model: result states, unit/basis conversion audits, comparability grading, provenance, Massachusetts adapter | — | CoaRecord | imported (crosslinks, verify, tests) | no | no | yes | no | Scientific domain model — legitimately not Boris | Medium |
| `scripts/cultivar_profiles.py` | python | 289 | Batch analyte profile model (censoring discipline, CLR/aitchison helpers) | — | BatchProfile | imported | no | no | yes | no | Scientific domain model | Low |
| `scripts/cultivar_claims.py` | python | 393 | Claim vocabulary + registry validation + epistemic rendering | claims | validation/render | imported (crosslinks, validate) | no | no | yes | yes | **Explicitly created because Boris's 4-kind relation vocabulary is too narrow** (docstring) | Medium |
| `scripts/coa_verify_example.py` | python | 616 | Hand-transcribe one real COA; render lab-results page + dataset record; optional PDF snapshot | COA PDF/URL | content/lab-results/TLAB-0002.md, datasets/TDTS-0022.md | manual | no | writes content | yes | partial | One-off verified ingestion + **hand-rolled page renderer with a hardcoded link map** | Medium: hardcoded relative-link dict (`COMPOUND_IDS`→paths) |
| `scripts/ma_ccc_walkthrough.py` | python | 162 | Read-only demo of MA mapping; refuses `--write` | fixture | stdout | manual | no | no | yes | partial | Verification/checklist demonstration | Low |
| `scripts/serve-headers.py` | python | 100 | Local server that applies `_headers` | `_headers` | HTTP responses | manual | no | no | no | no | Dev convenience (http.server can't send custom headers) | Low |
| `scripts/research_queue_analysis.py` | python | 237 | Analyze research corpus ledgers → coverage/priority metadata | research/_index/manifest.jsonl | stdout rows | manual | no | no | yes | no | Agent-orchestration decision support | Low |
| `scripts/research_queue_assign.py` | python | 281 | Enrich manifest + write ingestion queue | manifest + reports | research/_index/* | manual | no | writes research/_index | yes | no | Agent-orchestration | Low |
| `scripts/research_queue_doc.py` | python | 262 | Render ingestion-queue.md from manifest | manifest | research/_index/ingestion-queue.md | manual | no | writes | yes | no | Agent-orchestration | Low |

### Jurisdiction-pipeline infrastructure (PR #28, merged 2026-08-09)

| Path | Lang | Size | Purpose | Inputs | Outputs | Called | In prod build | Destructive | Idempotent | Boris-adjacent | Reason it exists | Maintenance risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/ingest/evidence.py` | python | 448 | Canonical jurisdiction-agnostic evidence model: analytical-state discipline (`numeric|below_lod|below_loq|nd|blank|qualitative|unknown`), `*_raw` preservation, required provenance | records | validated EvidenceRecord | imported | no | no | yes | no | Domain data model (see `docs/jurisdiction-evidence-model.md`) — legitimately not Boris | Low |
| `scripts/ingest/sources.py` | python | 266 | Source-manifest model: controlled `SOURCE_CLASSES` vocabulary, URL normalization, `researched` flag so stubs never claim research | state manifests | validated SourceManifest | imported | no | no | yes | no | Source acquisition/registry — legitimately not Boris | Low |
| `scripts/ingest/testing_requirements.py` | python | 408 | Testing-requirements schema: citation-required numeric limits, `pending-transcription` value status, effective/superseded dates | `data/testing-requirements/<state>.json` | validated requirement records | imported | no | no | yes | no | Domain data model with deliberate epistemic discipline | Low |
| `scripts/source_manifest.py` | python | 118 | CLI: `--validate` manifests, `--render` markdown report, `--stubs` (re)generate 49 state stubs | manifests | validation/report/stubs | manual | no | no | yes | no | Tooling for the source registry | Low |
| `scripts/testing_requirements.py` | python | 141 | CLI: `--validate` both datasets; `--render` writes `content/requirements/TREQ-*.md` — **hand-builds Boris frontmatter incl. `relations:` lists** (does not reuse `ingest/markdown.py`) | JSON (source of truth) | content/requirements pages | manual | no | writes content | yes | **yes (content generation)** | Third hand-rolled “data → generated Markdown” renderer (after dcc_ingest, MA adapter); JSON is source of truth, Markdown is a derived view Boris requires | Medium: another mirror of the Boris grammar |

---

## Boris Pressure Clusters

### BORIS PRESSURE: relation scalability and graph rendering (strongest evidence)

Files: `crosslinks.py`, `validate_crosslinks.py`, `cultivar_claims.py`, `ingest/ids.py` (relation emission), `dcc_sync.py` (hardcoded relations), `audit_markdown_links.py` (prose-table fallback), `ted-build.sh` (layout rules), plus ~99 hand-written `## Related Devices` / `## Related pages` sections in content.

Evidence chain:
- `docs/device-taxonomy-migration.md`: *"Boris caps `relations` at 16 per page (`max_relation_count`, boris/0.8.1). The manufacturer record used to carry a reciprocal `relates_to` for every device; at 23 Cannabis Hardware records that list exceeded the cap and failed the build with `EFRONTMATTER: relations exceeds maximum relation count`."* The fix: drop reciprocal relations, put device links in prose tables, validate them with a link audit.
- `scripts/cultivar_claims.py` docstring: *"The published Boris graph only supports four relation kinds (`relates_to`, `implements`, `depends_on`, `supersedes`). The rich claim vocabulary in this module therefore lives in a machine-readable registry…"*
- `reports/graph-connectivity.md` (2026-08-08): an agent hand-added **96 relation edges** to 53 content files, manually computing connected components, and preserved a "bidirectional pair convention" — i.e., both ends of every relationship had to be edited by hand.
- The very next day (2026-08-09), `crosslinks.py` was built to automate reverse edges. Its own report says *"This replaces the manual bidirectional pair convention… there is no longer any need to edit both ends of a relationship."*
- `themes/cantilever/layouts/*.html`: the template surface is `{{title}} {{content}} {{toc}} {{children}} {{breadcrumb}} {{nav}} {{asset-url}}` — **zero access to relations or the graph** (confirmed by searching the theme for `relations|backlink|related`; no matches).
- `docs/crosslinking-architecture.md` claims Boris "owns discovery, parent/nav validation, and rendering" while the layer "adds presentation edges only" — but the layer re-implements reverse-edge derivation, multi-hop projection, per-role section rules, ordering, pagination, index-page generation, HTML injection, machine export, and its own link validation. That is most of a navigation engine.

Underlying pressure: **the relation model is closed (4 kinds), capped (16/page), unidirectional in rendering, and invisible to templates.** One deficiency, five or more compensating utilities.

### BORIS PRESSURE: generated collections / data-driven pages

Files: `dcc_ingest.py`, `dcc_sync.py`, `state_ingest.py`, `ingest/markdown.py`, `ingest/states/massachusetts.py`, `coa_verify_example.py`, `testing_requirements.py`, `crosslinks.py` (index pages).

Evidence:
- Boris input is Markdown only. Every structured dataset must be converted into content pages: DCC produced `licenses/`, `organizations/`, `testing-laboratories/`, `recalls/`, `contaminants/`, `datasets/`, `requirements/`, `law-and-use/`; Massachusetts generates 10 collections (118 published pages from ~954k rows).
- **PR #28 added a third renderer**: `scripts/testing_requirements.py` treats JSON (`data/testing-requirements/<state>.json`) as the source of truth and renders `content/requirements/TREQ-*.md` as "a derived view" — hand-building Boris frontmatter incl. `relations:` lists and not even reusing `ingest/markdown.py`. The PR's own audit (`reports/jurisdiction-pipeline-audit.md`) documents the pattern as "pipeline: source evidence -> pages" — i.e. the project keeps absorbing the Boris boundary project-side.
- Durable *records* that cannot be pages (measurements, claims, source manifests) live in side JSON/JSONL registries (`metadata/coa-records.jsonl`, `metadata/cultivar-claims.jsonl`, `data/source-manifests/`) that only project Python reads; Boris never sees them.
- `ingest/markdown.py` reimplements the Boris content grammar (frontmatter, tables, callouts, wiki-links) so generators can emit valid input — and only ever emits `relates_to`, silently discarding the other three kinds.
- The project's own docs ask the right question in reverse: whether "research datasets are being unnecessarily converted into Markdown merely to satisfy Boris." The audit's answer: partially yes — aggregate pages (license counts, dataset summaries) are reasonable pages; per-record pages (a page per affected product, per dataset snapshot) are the byproduct of "everything must be Markdown."

Underlying pressure: **no structured-data concept, no data-attachment mechanism, no content-generation API.** Agents responded by building a mini content-generation framework.

### BORIS PRESSURE: schema-aware validation

Files: `audit_device_taxonomy.py`, `audit_record_completeness.py`, `audit_coa_content.py`, `validate_cultivar_claims.py`, `validate_crosslinks.py`, `ingest/validation.py`, `ingest/schema.py`, plus the vocabularies in `metadata/device-taxonomy.json` and `metadata/coa-measurement.schema.json`.

Evidence: The frontmatter schema is deliberately closed to 6 keys (`id, title, parent, status, tags, relations`) — unknown keys fail the build. That protects the schema but leaves **no way to express content contracts**: controlled tag vocabularies, mutually exclusive tags, required spec rows, required sections, relation-type constraints, canonical-ID requirements. Every one of those is re-implemented as a Python audit with its own exit-code convention. The audits even re-parse frontmatter with regexes (`FRONTMATTER = re.compile(r"^---\n(.*?)\n---")`), duplicating Boris's own parsing.

Underlying pressure: **no validation API / no schema extension for content semantics.** Six auditors exist because one capability is missing.

### BORIS PRESSURE: canonical stable IDs

Files: `ted_ids.py`, `ingest/ids.py`, `metadata/id-map.jsonl`, `data/massachusetts-ccc/id-map.json`, `metadata/id-policy.json`.

Evidence:
- Two independent ID registries coexist: `ted_ids.py`'s `metadata/id-map.jsonl` and the ingest package's `NaturalKeyRegistry` (`data/massachusetts-ccc/id-map.json`), each with its own allocation scheme and collision rules.
- **PR #28's audit (`reports/jurisdiction-pipeline-audit.md` §8) documents the consequence**: an empty Massachusetts `id-map.json` would allocate `jurisdictions/TJUR-0001` — colliding with California's — and the same for every shared collection prefix (TLIC, TSTL, TDTS, TREQ, TCNT, TORG…). The fix was project-side: seed the registry from existing content before allocating, plus create-if-missing trunk writes to stop the MA pipeline clobbering CA trunk text. No Boris issue was filed.
- `metadata/id-map.jsonl` is a **generated file deliberately committed** ("the one deliberate exception"), regenerated by `ted_ids.py --write`; four other scripts parse it.
- `reports/placeholder-disposition.md` documents a renumbering hazard: deleting a collection's anchor file silently renumbers the remaining satellites.
- `docs/status.md`: "Canonical CLI and global ID allocation are unresolved."

Underlying pressure: **Boris has an `id` field but no identity policy, no allocation, no collision detection, no migration record.** The project built two.

### BORIS PRESSURE: build lifecycle hooks

Files: `ted-build.sh`, `ted-publish.sh`, `bin/validate_graph.sh`, `crosslinks.py --inject`, `audit_html_ids.py`, `ensure-boris.sh`.

Evidence: Everything that must run before or after Boris is a shell wrapper: pre-build ID/link checks, post-build HTML injection, post-build HTML-ID audit, post-build security-header copy, post-build release audit, pre-build compiler provisioning. There is no Boris lifecycle/plugin interface, so the project's "pipeline" is a bash script that grows a step per need. The HTML-injection step is the most telling: the project cannot express navigation in the theme, so it patches rendered output.

Underlying pressure: **no hooks/plugins/lifecycle phases.** Even if Boris gained features, the wiring would still be shell unless a hook interface exists.

### BORIS PRESSURE: provenance-aware source ingestion (partially correctly outside Boris)

Files: `dcc_ingest.py`, `ingest/fetch.py`, `ingest/storage.py`, `ingest/schema.py`, `ingest/diff.py`, `ingest/core.py`.

Evidence: checksummed immutable snapshots, content-type guards, row-collapse and date-regression guards, change reports. This is research-grade acquisition discipline. It is **correctly outside Boris** — the only Boris-adjacent part is the final "convert to Markdown" step and the ID allocation.

---

## Ranked Boris Shortcomings

Priorities: **P0** actively dangerous / data-integrity risk; **P1** repeatedly causes project-local scaffolding; **P2** substantial ergonomic problem; **P3** useful improvement; **P4** documentation/polish.

### 1. No navigation/backlink rendering exists anywhere in the HTML pipeline — **P1** (highest value to fix) 🔬

- **Evidence:** theme templates reference no relation data; `crosslinks.py` (1,710 lines) exists solely to derive and render backlinks/related sections; `reports/graph-connectivity.md` shows humans hand-adding 96 edges and maintaining bidirectional pairs; `docs/crosslinking-architecture.md` documents the resulting layer.
- **🔬 Verified:** Boris's template marker vocabulary is closed — `{{content}}`, `{{nav}}`, `{{breadcrumb}}`, `{{title}}`, `{{toc}}`, `{{children}}`, `{{metadata}}`, `{{footer}}`, `{{asset-url PATH}}` — and `{{relations}}` in a layout is a **hard build error** (`LayoutUnknownMarker`). `{{metadata}}` renders status/parent/tags and never relations. Boris's own contract (`docs/contracts/semantic-relations.md`) states this is deliberate: *“A relation is not a navigation edge, parent edge, include edge, or wiki-link reference edge.”* Semantic relations are IR knowledge metadata; HTML, Documentation Intelligence (`check`/`impact`), and RAG outputs explicitly do not expose them (documented in the respective contracts). The validated relation set is available **only** in the IR export (`graph.json`, schemaVersion 0.3.0, `relations` array — verified 16 relations exported). So the gap is not “Boris should render relations”; it is that **Boris offers no navigation primitive at all** — no backlinks, no related-pages rendering, no template access to the (validated) relation set in the HTML pipeline.
- **Affected scripts:** crosslinks.py, validate_crosslinks.py; audit_markdown_links.py (fallback); dcc_sync.py (hardcoded relations).
- **Affected content:** all 417 pages (measured live); ~99 hand-written "Related pages" sections that now duplicate generated sections.
- **Current workaround:** post-render HTML injection + hand-maintained prose links.
- **Why undesirable:** two navigation systems that can disagree; regex HTML surgery; the largest maintenance surface in the repo.
- **Frequency:** every build; every content wave.
- **Maintenance burden:** High (1,710 lines, its own pagination + index pages).
- **Risk of data corruption:** Low (idempotent), but risk of *divergence* between graph and prose is real.
- **Risk of divergence:** High — hand-written "Related" lists coexist with generated sections.
- **AI-attractor factor:** **EXTREME** — this is the single most likely friction to make an agent write a new script: an agent sees "pages should link to related entities" and reaches for Python because the template has no way to ask for it.
- **Boris partial support:** none discovered (templates expose `children` but not relations).
- **Proposed Boris-level solution:** expose the relation graph (outgoing/incoming edges, typed) to templates, or provide a built-in backlinks/related-navigation renderer with caps; at minimum document a first-class "derived navigation" recipe.
- **Core vs extension vs docs:** **CORE** (backlinks/related pages are generic static-site behavior) with a template-data API as the mechanism.
- **Migration implications:** crosslinks.py and validate_crosslinks.py could be deleted; injected markup replaced by template output; hand-written Related sections retired.
- **Priority:** P1 (first).

### 2. Relation cap (16/page) and 4-kind closed vocabulary are deliberate, hard-coded, and undiscoverable from a consuming project — **P0** (data-integrity) / **P1** (scaffolding) 🔬

- **Evidence:** `docs/device-taxonomy-migration.md` (the 23-device manufacturer page hit `EFRONTMATTER: relations exceeds maximum relation count`); `cultivar_claims.py` docstring (4 kinds → parallel registry).
- **🔬 Verified:** `max_relation_count: usize = 16` is a compile-time constant and relations are stored in a fixed-size `[16]SemanticRelation` array (`src/page.zig`); the vocabulary is exactly `relates_to`, `implements`, `depends_on`, `supersedes`. Fixture tests: 17 distinct relations → `EFRONTMATTER: relations exceeds maximum relation count`; 16 → builds. The cap and the vocabulary are **documented and deliberate** in Boris's own `docs/contracts/semantic-relations.md` ("The initial vocabulary is deliberately small"; "maximum 16 entries per page"), so this is a design decision, not an accident — but it is **undiscoverable from the project side**: the build/check error messages never name the allowed kinds ("relations contains an unknown relation kind [Fix the frontmatter or encoding for this file]"), and the contract docs ship only in the Boris repo, not with the binary.
- **Affected scripts:** dcc_sync.py (must hardcode minimal relations to stay under the cap), crosslinks.py (has to compensate for dropped edges), cultivar_claims.py, validate_cultivar_claims.py.
- **Affected content:** manufacturer pages (relations dropped → device links live in prose tables); cultivar identity pages (rich claim types cannot be relations).
- **Current workaround:** drop relations, keep links in prose; registry JSONL for richer kinds.
- **Why undesirable:** the graph model is silently incomplete — relationships that *exist in the content* are not *edges*, so graph diagnostics, connectivity analysis, and RAG consumers understate the site; the two representations (graph vs prose) can diverge with no build error.
- **Frequency:** every time a hub page (manufacturer, jurisdiction, dataset) outgrows 16 relations — which is the normal direction of growth for this archive.
- **Maintenance burden:** Medium.
- **Risk of data corruption:** Medium — no silent *wrong data*, but silent *missing edges* and a hard wall that forces content degradation.
- **Risk of divergence:** High.
- **AI-attractor factor:** **HIGH** — an agent hitting `EFRONTMATTER` is far more likely to write a "relation distribution helper" or drop relations than to question the cap.
- **Boris partial support:** the cap is enforced and validated; the four kinds are enforced; relation diagnostics exist (`ERELATIONMISSING`, `ERELATIONSELF`, `ERELATIONDUPLICATE`, `EFRONTMATTER` — ERELATIONSELF verified firing).
- **Proposed Boris-level solution:** raise/remove the cap (or make it configurable with a sane default); make the relation-kind vocabulary extensible via config/schema rather than closed; make the failure messages name the allowed kinds. Because relations are stored in a fixed `[16]SemanticRelation` array, raising the cap is a code change, not configuration.
- **Core vs extension vs docs:** **CORE** for the cap; **extension** (configurable relation kinds) for the vocabulary; **DOCS** for surfacing the contract to consumers.
- **Migration implications:** manufacturer pages could re-add per-device relations; crosslinks sections could consume them; `relations_for_category` in dcc_sync.py becomes unnecessary.
- **Priority:** P0/P1.

### 3. No structured-data concept alongside prose — **P1**

- **Evidence:** `ingest/markdown.py` reimplements the Boris grammar to convert datasets into Markdown; `testing_requirements.py` (PR #28) hand-builds a *third* renderer with its own frontmatter + `relations:` emission and treats JSON as source of truth; durable records live in `metadata/coa-records.jsonl` / `cultivar-claims.jsonl` / `data/source-manifests/` that Boris never reads; `crosslinks.py` is the only consumer of those files and renders them by HTML injection.
- **Affected scripts:** dcc_ingest.py, dcc_sync.py, state_ingest.py, ingest/markdown.py, testing_requirements.py, coa_verify_example.py, crosslinks.py.
- **Affected content:** all generated collections (~180+ pages).
- **Current workaround:** generate Markdown from data at ingest time; maintain parallel JSONL for anything that isn't a page.
- **Why undesirable:** the site's structured data (measurements, claims, license registries) exists twice — once as generated prose pages, once as JSONL — and the two can drift; regeneration requires a full content rebuild.
- **Frequency:** every ingest cycle.
- **Maintenance burden:** High (the ingest pipeline is 5,000+ lines).
- **Risk of data corruption:** Low-Medium (guards are good).
- **Risk of divergence:** High (generated pages vs source data vs JSONL).
- **AI-attractor factor:** **HIGH** — every new state or dataset produces a new adapter + page generator rather than a data declaration.
- **Boris partial support:** none found (no data-file type).
- **Proposed Boris-level solution:** a first-class data-file concept (JSON/CSV attached to a page or collection) with template access, OR a documented, canonical "generate pages from data" extension point with stable data-sync semantics.
- **Core vs extension vs docs:** **EXTENSION POINT** (data files could be core; a generate-from-data hook is an extension API); at minimum **DOCS/EXAMPLE**.
- **Migration implications:** ingestion pipelines shrink from page-generators to data-sync + template rendering.
- **Priority:** P1.

### 4. No content-validation API (schema extension for semantics) — **P1**

- **Evidence:** six Python auditors re-parse frontmatter with regexes to enforce rules the closed schema cannot hold (taxonomy contradiction rules, record-completeness floor, COA content contract, claim registry integrity).
- **Affected scripts:** audit_device_taxonomy.py, audit_record_completeness.py, audit_coa_content.py, validate_cultivar_claims.py, validate_crosslinks.py, ingest/validation.py.
- **Affected content:** devices, lab-results, cultivars, generated collections.
- **Current workaround:** one Python auditor per rule-set, each with its own exit codes, wired into `validate_graph.sh` by hand.
- **Why undesirable:** validation logic lives outside the compiler; the closed schema gives no place for controlled vocabularies, so vocabulary lives in JSON files that must be kept in sync with content pages (e.g. `metadata/device-taxonomy.json` vs `content/reference/TREF-0004.md`).
- **Frequency:** every build (the gate runs 6 audits).
- **Maintenance burden:** Medium.
- **Risk of data corruption:** Low (they fail loudly).
- **Risk of divergence:** Medium (vocab JSON vs standard page).
- **AI-attractor factor:** **HIGH** — agents respond to "record must satisfy rules" by writing a new Python checker rather than a declarative schema.
- **Boris partial support:** frontmatter schema validation exists (closed grammar) but no content-semantics surface.
- **Proposed Boris-level solution:** a validation API (or declarative schema rules: allowed tag vocabularies, required sections, relation-type constraints, cross-field invariants) that runs inside `boris check` so the gate is one command.
- **Core vs extension vs docs:** **CORE** (validation API) or **EXTENSION** (a validator plugin interface).
- **Migration implications:** six auditors collapse into declarative rules; `validate_graph.sh` shrinks.
- **Priority:** P1.

### 5. Stable canonical ID management is project-owned and duplicated — **P1/P2**

- **Evidence:** `ted_ids.py` + `NaturalKeyRegistry`; two id-maps; committed generated `metadata/id-map.jsonl`; documented renumbering hazard; `docs/status.md` "global ID allocation unresolved." **PR #28 hit the collision live**: a fresh Massachusetts registry would have allocated `TJUR-0001` on top of California's (and the same for every shared prefix); the fix (seed registry from content, create-if-missing trunks) was implemented project-side in `ingest/ids.py` + `state_ingest.py` — see `reports/jurisdiction-pipeline-audit.md` §8.
- **Affected scripts:** ted_ids.py, ingest/ids.py, and every consumer of `metadata/id-map.jsonl` (crosslinks, 3 auditors, publish).
- **Affected content:** every page with an `id`.
- **Current workaround:** a committed migration map regenerated by a script; a second registry with tamper-detection digest.
- **Why undesirable:** two sources of truth; ordering-dependent allocation; the risk of renumbering on anchor deletion.
- **Frequency:** every build.
- **Maintenance burden:** Medium.
- **Risk of data corruption:** Medium (renumbering would silently break URLs).
- **Risk of divergence:** High (two registries).
- **AI-attractor factor:** **HIGH** — new collections require editing `ted_ids.py` prefix tables; agents have done so repeatedly (the file grew 9 prefixes in one commit).
- **Boris partial support:** `id` field is validated as required/unique? (partially, via check), but no allocation or policy.
- **Proposed Boris-level solution:** canonical ID validation/allocation in Boris, or a documented "ID policy" mechanism with collision detection and a stable migration story; alternatively accept the project registry but make it the *single* one.
- **Core vs extension vs docs:** **CORE** (ID uniqueness is generic) with docs for migration.
- **Migration implications:** `ted_ids.py` shrinks to a validator; `ingest/ids.py` could be deleted.
- **Priority:** P1.

### 6. No build lifecycle hooks — **P2**

- **Evidence:** `ted-build.sh` manually sequences 8 pre/post steps; HTML injection and audits are shell-wired; post-render HTML-ID audit exists because nothing validates output.
- **Affected scripts:** ted-build.sh, ted-publish.sh, validate_graph.sh, crosslinks.py --inject, audit_html_ids.py.
- **Proposed solution:** explicit lifecycle phases (before-build, after-render, after-write) with a hook/plugin interface so project steps are declarative, not shell concatenation.
- **Core vs extension:** **EXTENSION** (hooks/plugins).
- **AI-attractor factor:** **MEDIUM-HIGH**.
- **Priority:** P2.

### 7. Boris diagnostics: `unreferenced_page` fires on 91.6% of a healthy site and is filtered by hand (twice) — **P2/P3** 🔬

- **Evidence:** `validate_graph.sh` filters `.code != "unreferenced_page"`; `dcc_ingest.py` re-implements the same filter (line ~1302).
- **🔬 Verified:** on the live 417-page tree, `boris check` reports **382 of 417 pages (91.6%) as `unreferenced_page`** — all 26 roots and 356 satellites — far above the ~178 figures in the historical reports (measured when the tree was ~207 entities). The rule is *documented* in Boris's `docs/contracts/documentation-intelligence.md` ("unreferenced pages, excluding the page's own `parent` relationship"), so it is not mysterious to Boris — but it is undiscoverable to a consumer, who must reverse-engineer the JSON findings shape and the tolerated baseline. There is no way to mark a page as intentionally unreferenced or to configure the check.
- **Affected scripts:** validate_graph.sh, dcc_ingest.py.
- **Proposed solution:** configurable/declarative "ignore" set, severity levels, or shipped findings documentation; the project should not need to re-implement the filter twice.
- **Core vs extension vs docs:** **CORE** (diagnostics quality) + **DOCS** (findings format — note the JSON goes to **stderr**, not stdout, which is itself undocumented; the project discovered this and captures `2>file`).
- **AI-attractor factor:** **MEDIUM** — the wrapper exists; worse, its filter logic is duplicated.
- **Priority:** P2 (documentation of the findings format is P4 alone).

### 8. Layout selection: the 14 per-collection glob rules can collapse to role selectors the project never discovered — **P3** 🔬

- **Evidence:** 14 `--layout-rule default glob:<collection>/*` flags in ted-build.sh; every new collection (cannabinoids, terpenes, jurisdictions…) required editing the build script.
- **🔬 Verified:** `--layout-rule` selectors include `role:trunk` and `role:satellite` (per `boris --help`; fixture-verified working: `rules=1`). **Correction, verified by full-site rebuild:** the 14 globs do *not* cover every satellite collection — only the 11 authored collections (botanicals, changelog, cultivars, devices, guides, lab-results, law-and-use, manufacturers, products, reference, terpenes); `releases/*`, `safety/*`, `specs/*` are **dead rules** (those directories never existed; only the top-level trunk pages remain). *(Update 2026-08-09: the three dead globs were removed from `ted-build.sh`; a rebuild confirmed the output is byte-identical — `rules=11`, 0 diffs.)* The 11 DCC/CCC-generated collections (affected-products, cannabinoids, contaminants, datasets, jurisdictions, licenses, organizations, recalls, requirements, safety-advisories, testing-laboratories) were **never globbed** and render the default `main.html` — the layout that carries the "Regulation & Public Data" nav group. A global `--layout-rule default role:satellite …/compact.html` therefore **changes 268 pages** (removes that nav group from the data pages), so it is *not* output-identical and cannot be adopted as a pure refactor. A `role:` selector cannot express "satellites in these collections only" — there is no collection+role combination. (The DCC schema-report note that Boris derives a collection from the *first path segment* remains a separate, valid constraint.)
- **Proposed solution:** DOCS first (surface the selector), plus a default per-collection layout mechanism as a small core feature.
- **Core vs extension vs docs:** **DOCS** (primary) / **CORE** (small).
- **AI-attractor factor:** **MEDIUM** — adding a collection is a three-file edit (content dir, ted_ids prefixes, build script).
- **Priority:** P3.

### 8b. The validated relation set is only reachable via a separate IR pass; the project's crosslinks layer re-parses frontmatter instead — **P2** 🔬

- **Evidence:** `scripts/crosslinks.py` parses `relations:` lines from source Markdown with regex (`FRONTMATTER_RELATION_RE`). Boris's `docs/contracts/semantic-relations.md` requires consumers to "consume the same validated relation set" and warns they "must not invent a second parser."
- **🔬 Verified:** the *validated* relation set (all of ERELATIONMISSING/ERELATIONSELF/ERELATIONDUPLICATE/cap applied) is emitted only in the IR export — `boris --no-rag --out <dir>` → `graph.json` (`schemaVersion: 0.3.0`, `relations: [{from, to, kind}]` — verified 16 relations on the fixture). HTML, `check`, `impact`, and RAG outputs deliberately omit semantic relations (documented in each contract). The project therefore re-parses source instead of consuming the validated export — a second parser, exactly what the contract forbids — because no validated relation data is available in the HTML-render path it uses.
- **Affected scripts:** crosslinks.py, validate_crosslinks.py.
- **Current workaround:** regex re-parse of frontmatter (brittle: the parser must mirror Boris's grammar exactly, and it raises on any entry Boris would have already rejected).
- **Why undesirable:** duplicated parsing of the compiler's own input; drift risk if the grammar changes; the project must re-validate what Boris already validated.
- **Proposed solution:** (a) an official recipe for consuming IR `graph.json` before HTML injection, or (b) a Boris flag/artifact that exposes the validated relation set in the HTML pipeline (e.g. a render-time data file), or (c) template access to validated relations (ties to finding #1).
- **Core vs extension vs docs:** **DOCS/EXAMPLE** (recipe) or **EXTENSION** (render-time data).
- **AI-attractor factor:** **HIGH** — any agent building graph features will re-parse frontmatter rather than discover the IR export.
- **Priority:** P2.

### 9. Generated artifacts in the source tree — **P3/P4**

- **Evidence:** `metadata/id-map.jsonl` is generated + committed + consumed by 5+ tools; `data/massachusetts-ccc/*` durable records are generated + committed; sync reports are committed. The repo makes one deliberate exception and documents "do not hand-edit," but regeneration ordering (run `ted_ids.py --write` after content changes) is a recurring coordination step that agents get wrong.
- **Proposed solution:** Boris-level support for committing generated state with deterministic regeneration, or a documented single "regenerate everything" command.
- **Core vs extension vs docs:** **DOCS** (recipe) mostly; a lifecycle hook would fix it.
- **AI-attractor factor:** **MEDIUM** — agents have regenerated the map at least four times in history; one report notes the committed map was missing recent records.
- **Priority:** P3.

### 9b. Boris ships a built-in output link audit that the project never discovered; the project's link audit covers a real `.md`-target gap — **P3** 🔬

- **Evidence:** no project doc, report, or script mentions Boris's `link_audit`; the project relies on its own `audit_markdown_links.py` (source-level) and `validate_crosslinks.py` CXL-01 (injected links).
- **🔬 Verified:** Boris runs a post-render link audit (`src/link_audit.zig`) immediately before publishing: broken `.html`/asset hrefs fail the build with `EROUTEMISSING`/`EROUTEESCAPE` (fixture test: `href="TED-9999.html"` → `error: EROUTEMISSING … does not resolve to a published output` → `LinkAuditFailed`). It **deliberately skips literal `.md`/`.mdx` targets** (documented in `docs/contracts/documentation-links.md`: "leaves missing targets byte-for-byte unchanged") — verified: a broken `[x](TED-9999.md)` builds and ships as a literal `href="TED-9999.md"` 404. `boris check` reports **no link findings at all**.
  - Therefore the project's `audit_markdown_links.py` is **not** a duplicated Boris capability: it catches source-level `.md` typos that would otherwise ship as literal broken hrefs. What is undiscovered: Boris's output audit already gates broken `.html`/asset links (the project's own pipeline inherits this free), and the crosslinks layer's injected `.html` links run *after* Boris's audit and so need their own CXL-01 check — a direct consequence of the post-render injection architecture.
- **Affected scripts:** audit_markdown_links.py (justified; keep), audit_html_ids.py (complementary), validate_crosslinks.py CXL-01.
- **Proposed solution:** DOCS (surface the built-in link audit + its `.md`-skip contract); optionally change the documentation-links contract so literal `.md` targets are flagged unless rewritten.
- **Core vs extension vs docs:** **DOCS** (primary) / **CORE** (small: warn on literal `.md` hrefs).
- **AI-attractor factor:** **LOW-MEDIUM**.
- **Priority:** P3.

### 10. Boris acquisition friction (release channel) — **P3/P4**

- **Evidence:** `ensure-boris.sh` (337 lines) + `metadata/boris-version.json` + Zig checksums + a provisioner test suite + CI cloning and building Boris a third way. Boris has no binary releases; every project must pin, fetch Zig, and compile.
- **Proposed solution:** release binaries/manifests for Boris (or a documented official provisioner), so projects stop reimplementing it.
- **Core vs extension vs docs:** **ECOSYSTEM** (release engineering), not compiler core.
- **AI-attractor factor:** **MEDIUM** (agents don't usually write this — the project already did, twice).
- **Priority:** P3.

---

## Potential Boris Extension Points

Things Boris should *enable* without owning the domain logic:

1. **Data-file attachment** — a page can reference a JSON/CSV data file; templates can render it. This would let the site keep license registries, measurements, and claims as data while pages stay prose.
2. **Generate-from-data hook** — a lifecycle hook where a project-provided generator produces pages from data before the main render; the current "generate Markdown in Python" would become a thin, declarative step.
3. **Validation plugin API** — project validators (taxonomy, completeness, COA, claim registry) registered so `boris check` runs them with a stable findings format.
4. **Post-render hook** — for output transforms (e.g. the current injection) without regex HTML surgery; hooks would run inside the build with proper ordering.
5. **Relation-kind extension** — configurable relation vocabulary (claims, lineage, tested-by, etc.) so projects don't build parallel registries.
6. **ID policy plugin** — project-defined ID allocation/normalization rules validated by Boris.

---

## Documentation / Discoverability Failures

Cases where Boris likely already does the job, but the project (or an agent) would not discover it:

1. **`boris check` findings format and semantics.** The project reverse-engineered the JSON findings shape and filters `unreferenced_page`. There is no documented schema, no list of finding codes, no documented baseline behavior, no documented way to exempt pages. Consequence: `validate_graph.sh` and `dcc_ingest.py` both re-implement the same filter by hand.
2. **Whether Boris validates internal Markdown links.** 🔬 The project wrote `audit_markdown_links.py` before (or without) discovering whether `boris check` does this. **Verified: it does not** — `boris check` reports no link findings, and Boris's post-render audit deliberately skips literal `.md` targets (see finding 9b and Appendix B.1). So this script is a **genuine gap**, not a duplicated capability — but the *existence* of the built-in output audit (and its `.md`-skip contract) is still undiscovered/undocumented.
3. **Template data surface.** The project knows `{{children}}`, `{{nav}}`, `{{toc}}`, `{{breadcrumb}}` exist, but nothing suggests relation access is possible. Either Boris has no relation template data (a gap), or it has it and it's undocumented (a discoverability failure). Either way, the absence of documentation caused a 1,710-line workaround. This is the most expensive documentation failure in the repo.
4. **The `relations` cap and kind list are only discoverable by build failure.** `EFRONTMATTER: relations exceeds maximum relation count` at 16, and an unlisted kind is rejected with no hint of the allowed set. A documented frontmatter reference (fields, relation kinds, limits, layout rules) would have saved the manufacturer-page degradation and the claim-registry detour.
5. **Layout rule syntax.** 14 glob rules in `ted-build.sh` suggest per-collection configuration is possible but tedious; no doc explains whether a default/glob form exists.

---

## AI Scaffold Magnets

Places where Boris ergonomics practically invite agents to write glue code:

1. **"Make these pages link to each other."** — EXTREME. Any agent asked to improve navigation writes a Python script (parse frontmatter → compute backlinks → mutate content or HTML). This happened at least three times: graph-connectivity pass (manual edges), crosslinks layer (automation), and the hand-written "Related pages" sections. The template has no answer to the question, so the agent answers with a script.
2. **"Enforce these content rules."** — HIGH. The closed schema has no place for rules, so each rule-set becomes a new `audit_*.py` with its own exit codes and wiring. Six exist.
3. **"Add a dataset / state."** — HIGH. Adding structured data requires a new adapter + page generator + ID prefixes + trunk pages + layout rule; agents build pipelines instead of declaring data.
4. **"Keep IDs stable across migrations."** — HIGH. Agents reach for `ted_ids.py`-style scripts because Boris offers no identity facility.
5. **"Validate the rendered site."** — MEDIUM. Post-render checks (HTML IDs, headers, links) are written from scratch because there is no output-validation surface.

**Important framing:** the agents that built these scripts were behaving reasonably. The pattern to report is architectural: *local automation was introduced at this boundary rather than extending/fixing Boris*. For the ingestion pipelines (DCC/CCC), that decision was **reasonable at the time** (Boris is not a data-acquisition framework). For the navigation layer and the validators, the decision looks **accidental** — the authors even wrote docstrings insisting they were not reimplementing Boris, while implementing most of a navigation engine.

---

## Legitimate Project Tooling

This section is deliberate. Not every script is a Boris deficiency:

- **`dcc_ingest.py`, `dcc_sync.py`, `state_ingest.py`, the entire `ingest/` package, and `ingest/states/massachusetts.py`** — regulator data acquisition, normalization, provenance, privacy, and change management. This is exactly the class of work Boris should *not* own. The checksums, schema-drift guards, row-collapse guards, date-regression guards, and fixture-mode safety are exemplary engineering and belong in this repository.
- **`coa_model.py`, `cultivar_profiles.py`, `cultivar_claims.py`** — scientific measurement and identity models (censoring discipline, unit-conversion audits, comparability grading, epistemic claim rendering). A static-site compiler has no business owning analytical-chemistry semantics. The only Boris-adjacent part is *why* claims live in a registry instead of relations (the 4-kind cap).
- **`audit_public_release.py`, `audit_sensitive_content.py`, `audit_large_files.py`, `audit_common.py`** — repository release governance (PII, secrets, history blobs, headers). These are generic and could be reused outside this repo, but they are not Boris's job.
- **`serve-headers.py`, `research_queue_*.py`, `ma_ccc_walkthrough.py`, `coa_verify_example.py` (walk-through mode)** — developer convenience, agent orchestration, and verification demos.
- **`ensure-boris.sh`, `clean-binaries.sh`, `test_ensure_boris.py`, CI/deploy workflows** — legitimate *ecosystem* tooling (though it signals a Boris release-channel gap, it is not evidence of a compiler deficiency).

Defensible, honest, and valuable: the acquisition pipeline and the scientific models. The report does not recommend deleting them even after Boris improves.

---

## "Delete If Boris Improves" Map

Candidates only — nothing is deleted. "Could disappear" ≠ "should disappear."

| Script | Boris improvement required | Full deletion realistic? | Shrink instead? | Migration difficulty | Dependencies | Risk | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `crosslinks.py` (+ validate_crosslinks.py) | Relation graph in templates / built-in backlinks + pagination | Yes (markup becomes template output) | Would shrink to a thin "edge classification" helper if kept | Medium (re-template the theme; retire hand-written Related sections) | id-map, claims, coa registries, theme | Low-Medium | High |
| `cultivar_claims.py` + `validate_cultivar_claims.py` | Extensible relation kinds | No — the claim vocabulary is domain logic | Yes — could emit Boris relations for entity-to-entity claims; keep registry for non-entity sources | Low | registry | Low | Medium |
| `audit_device_taxonomy.py`, `audit_record_completeness.py`, `audit_coa_content.py` | Validation API / schema rules | Yes (rules become declarative) | Yes — could remain as docs + a thin adapter | Medium | vocab JSONs | Low | Medium |
| `ted_ids.py` (validation mode) | ID policy in Boris | Yes for allocation; map stays as migration record | Yes — shrink to a migration-map writer | Low-Medium | metadata/id-map.jsonl | Medium (renumbering history) | Medium |
| `ingest/ids.py` (`NaturalKeyRegistry`) | Single ID registry / allocation in Boris | Yes, if merged with ted_ids | Yes — merge into one registry | Medium (migrate id-maps) | data/massachusetts-ccc/id-map.json | Medium | Medium |
| `ingest/markdown.py` | Data files or generate-from-data hook | No — still needed to emit pages | Yes — thinner if Boris owns grammar/escaping | Low | generators | Low | Medium |
| `audit_markdown_links.py` | None needed — verified genuine gap (Boris skips `.md` targets by design); optionally a docs-links warning in Boris | No — should stay (catches source typos that ship as literal broken `.md` hrefs) | No | Low | none | Low | High |
| `audit_html_ids.py` | Post-render hook or output validation | Yes | No | Low | dist | Low | High |
| `ted-build.sh` layout rules + audit hooks | Default layout rules; lifecycle hooks | No (wrapper stays) | Yes — much shorter | Low | Boris CLI | Low | High |
| `bin/validate_graph.sh` | Clean diagnostics; validation API | No (gate stays) | Yes — drops 5 of 8 steps | Low | all auditors | Low | High |
| `ensure-boris.sh` + `boris-version.json` | Boris binary releases / official provisioner | Yes | Yes — replace with a 5-line fetch | Low | network | Low | High |
| `dcc_ingest.py`, `dcc_sync.py`, `state_ingest.py`, `ingest/*` | (Data files + generate hook would shrink only the page-generation half) | No | Yes — the acquisition half stays; the Markdown-generation half shrinks | Medium | DCC/CCC sources | Medium | Medium |

---

## Recommended Boris Issues

See `reports/boris-issue-candidates.md` for independently readable, copy-ready issue drafts. Candidate list:

1. Expose the relation graph to templates (or render reverse edges/backlinks natively) — core.
2. Raise/remove the 16-relation-per-page cap; make it configurable — core.
3. Allow extensible relation kinds (config/schema) — extension.
4. First-class data files + template access — core/extension.
5. Content-validation API or declarative schema rules — core/extension.
6. Canonical ID policy/allocation (or consolidate the two project registries) — core.
7. Lifecycle hooks (before-build, after-render, after-write) — extension.
8. Document `boris check` findings schema and allow configuring/ignoring `unreferenced_page` — core/docs.
9. Default layout rules by collection — core/docs.
10. Official binary releases / provisioner — ecosystem.

---

## Recommended Boris Documentation Changes

1. **Frontmatter reference**: all allowed fields, the relation-kind list, the `max_relation_count` cap, and failure messages that state the allowed set — so the cap is discoverable before a build fails.
2. **Template data reference**: every template variable (including whether relations/backlinks are available); if they are not, say so and point at the recommended pattern.
3. **`boris check` reference**: findings JSON schema, codes, severity, exit codes, and how to exempt intentional cases (the project currently reverse-engineers this).
4. **Layout rules reference**: syntax, default behavior, and whether a per-collection default exists.
5. **A canonical "data-driven pages" recipe**: the blessed pattern for turning a structured dataset into rendered pages, so future states stop inventing adapters.
6. **A "derived navigation" recipe**: backlinks/related pages without post-render HTML surgery.
7. **An ID-policy recipe**: how a project should keep stable IDs and a migration record (the project's `id-map.jsonl` pattern is a good candidate to canonize or replace).

---

## Top 10 Boris Improvements Suggested by This Repository

1. **Template access to the relation graph + reverse-edge/backlink rendering** (kills crosslinks.py).
2. **Remove/configurable relation cap (16/page)** (kills the prose-table fallback and the dropped edges).
3. **Extensible relation kinds** (kills the claim registry detour).
4. **Data files / generate-from-data hook** (kills the page-generator half of the ingest pipelines).
5. **Content-validation API / declarative schema rules** (kills five auditors).
6. **Canonical ID policy or single registry** (kills the two-ID-system tension).
7. **Lifecycle hooks (after-render, after-write)** (kills the HTML injection + post-build shell wiring).
8. **Clean, documented `boris check` diagnostics with configurable baselines** (kills the duplicated filter).
9. **Default layout rules by collection** (kills the 14-flag enumeration).
10. **Binary releases / official provisioner** (kills the 337-line provisioning script and its CI twin).

---

## Things Boris Should Explicitly NOT Do

Boundaries discovered during this audit:

1. **Do not absorb regulator-specific acquisition** (DCC/CCC fetchers, normalizers, privacy specs, disclaimers, jurisdiction terminology). `ingest/states/massachusetts.py` (2,528 lines) is domain logic that would pollute a general-purpose compiler.
2. **Do not absorb the analytical measurement model** (result states, censoring discipline, unit/basis conversion audits, comparability grading, provenance requirements). That is a scientific data model, not a rendering concern.
3. **Do not absorb research-corpus orchestration** (research_queue_*: ledgers, verification status, ingestion priorities). That is agent-workflow tooling.
4. **(Softer)** Do not become a data-acquisition framework. The provenance discipline (checksums, guards, change reports) is valuable but project-owned.

---

## Conclusion

> Are we successfully dogfooding Boris, or are we gradually building a second site generator around it?

**Both, and the split is informative.**

At the **content-authoring and acquisition boundary**, the project is dogfooding honestly: the DCC/CCC pipelines, the COA models, and the release audits are exactly the kind of workload Boris should be asked to carry, and they are cleanly outside it. Nothing about the ingest package suggests a second site generator.

At the **rendering and navigation boundary**, the project has, in fact, built a second site generator layer — and it did so *while asserting it wasn't*. `scripts/crosslinks.py` re-derives the graph from Boris's own source structures, computes reverse edges and multi-hop projections, applies per-role rendering rules, enforces deterministic ordering and display caps, generates paginated index pages by copying layout shells, injects HTML into rendered output, validates its own output, and exports machine-readable companions. That is a navigation engine, a pagination engine, an index generator, and an output post-processor — roughly the second half of a static-site generator — layered on top of Boris. Its own docs say Boris "owns rendering" while the script does regex surgery on rendered HTML; that sentence is the tension this audit exists to surface.

The sequence in git history is the strongest evidence: on 2026-08-08 an agent hand-wired 96 bidirectional relations because "both ends of a relationship" had to be edited manually; on 2026-08-09 the project automated exactly that with a 1,710-line Python layer. Nobody wrote a Boris issue; nobody asked whether templates could see relations; the friction was absorbed locally instead of being reported upstream. That is the quiet-scaffolding failure mode the mission asked us to look for — and it is the single highest-value thing this audit found.

The verdict: the repository is dogfooding Boris as a *content compiler* successfully, and as a *graph platform* only by building around it. The fix is not "fewer scripts." The fix is that the next time the archive needs backlinks, pagination, validation, or stable IDs, the first question asked should be "what should Boris do?" — and the answer should be an issue, not a script.

**Highest-value Boris issue to tackle first:** expose the relation graph to templates (or render backlinks/related navigation natively), because it eliminates the largest workaround, addresses the most generic capability, and is the strongest AI-attractor in the repository.

---

## Appendix A — Areas Where Evidence Was Insufficient

Resolved empirically in the verification pass (2026-08-09; pinned Boris `9505ec6`, boris/0.8.1, provisioned via `scripts/ensure-boris.sh --provision`):

1. ~~**Whether Boris already validates internal Markdown links**~~ — **RESOLVED.** Boris runs a post-render link audit (`link_audit.zig`) that fails the build on broken `.html`/asset hrefs (`EROUTEMISSING`/`EROUTEESCAPE`) but **deliberately skips literal `.md`/`.mdx` targets**; `boris check` reports no link findings. So `audit_markdown_links.py` is a **genuine gap**, not a duplicated capability (see finding 9b).
2. ~~**Whether Boris templates can access relations**~~ — **RESOLVED.** The template marker vocabulary is closed (`{{content}} {{nav}} {{breadcrumb}} {{title}} {{toc}} {{children}} {{metadata}} {{footer}} {{asset-url}}`); `{{relations}}` is a hard build error (`LayoutUnknownMarker`). Semantic relations are exposed **nowhere** in the HTML pipeline; the validated relation set is available only in the IR export (`graph.json`) (see finding 1).
3. ~~**The current `unreferenced_page` baseline count and `boris check` output shape**~~ — **RESOLVED.** Re-measured live on the 417-page tree: **382 of 417 pages (91.6%)** flagged `unreferenced_page`; findings JSON is written to **stderr** (which is why `validate_graph.sh` captures `2>file`); the edges array exposes only `parent` edges, never semantic relations (see finding 7).
4. ~~**Exact Boris version and feature set**~~ — **RESOLVED.** Boris source (`9505ec6`) inspected: `max_relation_count = 16` compile-time constant, fixed `[16]SemanticRelation` array, exactly 4 relation kinds, `role:trunk|satellite` layout-rule selectors, `impact` command, IR/RAG exports — all verified against fixtures (see Appendix B).
5. **`dcc_ingest.py` and `state_ingest.py` live behavior** — still not executed (network-dependent, writes content); characterized from source and reports. Unchanged.

## Appendix B — Empirical Verification Results

All tests run against the pinned Boris binary (`9505ec6`, boris/0.8.1, built from source) on minimal fixture sites, 2026-08-09. Binary: `bin/boris` in this worktree.

### B.1 Does `boris check` validate local Markdown links?

**No.** `boris check` reports only graph findings (`unreferenced_page`, etc.) — no link findings. Link validation happens in a **post-render audit** (`src/link_audit.zig`) that runs immediately before publishing:

| Fixture | Result |
| --- | --- |
| Broken `href="missing.html"` (valid page id, unpublished route) | Build **fails**: `error: EROUTEMISSING … does not resolve to a published output`, then `LinkAuditFailed` |
| Broken `[x](missing.md)` | Build **succeeds**; the literal `href="missing.md"` ships byte-for-byte (404 in production) |
| Broken `href="missing.css"` (asset) | Build **fails** (`EROUTEMISSING` / `EROUTEESCAPE` family) |

Boris's `docs/contracts/documentation-links.md` documents the `.md` skip as deliberate: it leaves documentation-link targets "byte-for-byte unchanged" (a docs-links contract, not a site-links checker). Consequences for the audit:

- The project's `audit_markdown_links.py` (source-level `.md` target check) is **justified — not a duplicated Boris capability**. It catches source typos that would otherwise ship as literal broken `.md` hrefs.
- The project's pipeline already inherits Boris's output audit for free on `.html`/asset links — but the crosslinks layer's **injected** links run *after* Boris's audit and therefore need their own check (`validate_crosslinks.py` CXL-01). That is a direct cost of the post-render injection architecture.
- `boris check`'s findings JSON goes to **stderr**, not stdout — undocumented, and consistent with the project's `2>file` capture in `validate_graph.sh`.

### B.2 Can templates access relation data?

**No.** The template marker vocabulary is closed and unknown markers are hard build errors:

| Template marker | Result |
| --- | --- |
| `{{relations}}` | Build **fails**: `LayoutUnknownMarker` |
| `{{metadata}}` | Renders `Status`, `Parent`, `Tags` only — **never relations** |
| `{{nav}}`, `{{children}}`, `{{breadcrumb}}`, `{{toc}}`, `{{title}}`, `{{content}}`, `{{footer}}`, `{{asset-url PATH}}` | Work (documented set) |

Boris's own contract (`docs/contracts/semantic-relations.md`) states the design intent: *"A relation is not a navigation edge, parent edge, include edge, or wiki-link reference edge."* Semantic relations are treated as IR knowledge metadata: HTML, Documentation Intelligence (`check`/`impact`), and RAG outputs deliberately omit them (verified in each contract doc). The **only** machine-readable surface that includes the validated relation set is the **IR export** (`boris --no-rag --out <dir>` → `graph.json`, `schemaVersion 0.3.0`, `relations: [{from, to, kind}]` — 16 relations verified on fixture).

Combined with B.1, this settles the audit's biggest open question: **Boris offers no navigation primitive at all** — no backlinks, no related-pages rendering, no template access to relations in the HTML pipeline. `crosslinks.py` is not duplicating a feature that exists; it is building the feature that is missing.

### B.3 Relation cap and kinds

| Test | Result |
| --- | --- |
| 17 distinct relations on one page | Build **fails**: `EFRONTMATTER: relations exceeds maximum relation count` |
| 16 distinct relations | Build **succeeds** |
| Unknown relation kind | Build **fails** with `relations contains an unknown relation kind` — **the error does not list the allowed kinds** |
| Self-relation (`relates_to` self) | Build **fails**: `ERELATIONSELF` |
| Duplicate relation | Build **fails**: `ERELATIONDUPLICATE` (fired before the cap test in our fixture) |
| Missing target | `ERELATIONMISSING` (documented; part of the same validation family) |

Source inspection confirms: `max_relation_count: usize = 16` is a compile-time constant and relations live in a fixed `[16]SemanticRelation` array (`src/page.zig`); the vocabulary is exactly `relates_to`, `implements`, `depends_on`, `supersedes`. The cap and vocabulary are **documented and deliberate** in `docs/contracts/semantic-relations.md` ("The initial vocabulary is deliberately small"), i.e. this is a design decision — but one that is **undiscoverable from a consuming project**: the contract ships only in the Boris repo, and the error messages never name the allowed kinds.

### B.4 Layout-rule selectors

`boris --help` documents `role:trunk` and `role:satellite` selectors. Fixture test: `boris build --layout-rule default role:satellite themes/cantilever/layouts/compact.html` applies `rules=1`. **However, a full-site rebuild disproved the "collapse to one rule" claim:** the 14 globs cover only the 11 authored satellite collections (3 are dead: `releases/*`, `safety/*`, `specs/*`); the 11 DCC/CCC-generated collections were never globbed and render the default `main.html`, which alone carries the "Regulation & Public Data" nav group. Replacing the globs with a global `role:satellite → compact.html` rule changed **268 pages** (all 11 generated collections, every page) — the layout shell swap removed that nav group — while the 11 previously-globbed collections and all 26 roots stayed byte-identical. So `role:` selectors cannot reproduce the current two-tier layout assignment; a `role:` selector is not collection-scoped. (The DCC schema-report note that Boris derives a collection from the *first path segment* remains a separate, valid constraint.)

### B.5 Where does the validated relation set actually appear?

| Output | Semantic relations present? |
| --- | --- |
| HTML build | No |
| `boris check` JSON | No (edges array shows `parent` only) |
| `boris impact` | No |
| RAG export | No (parent-only by design, per contract) |
| Documentation Intelligence (`docs/contracts/documentation-intelligence.md`) | Explicitly excluded |
| **IR export `graph.json`** | **Yes** — `relations: [{from, to, kind}]`, schemaVersion 0.3.0 |

So `crosslinks.py` re-parses frontmatter with regex (`FRONTMATTER_RELATION_RE`) — a second parser, exactly what Boris's own contract warns against ("consume the same validated relation set… must not invent a second parser") — because no validated relation data is available in the HTML-render path the project uses (see finding 8b).

### B.6 Baseline `unreferenced_page` measurement

Live `boris check` on the real 417-page tree: **382 of 417 pages (91.6%)** flagged `unreferenced_page` — all 26 roots and 356 satellites — versus ~178 at 207 entities in the historical reports. The rule is documented in `docs/contracts/documentation-intelligence.md` (excludes a page's own `parent`), so it is not mysterious to Boris; it is undiscoverable to a consumer, who must reverse-engineer the findings shape and the tolerated baseline, and there is no way to mark a page as intentionally unreferenced or configure the check.
