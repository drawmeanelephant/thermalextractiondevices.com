# Crosslinking Implementation Report — Evidence-Aware Derived Navigation

**Date:** 2026-08-09
**Branch:** `freebuff/make-sure-you-have-most-current-git-ff021824-…` (based on `github/main` @ `2945c47`)
**Status:** Implemented, tested, wired into the build gate
**Architecture:** `docs/crosslinking-architecture.md` (normative design)
**Changelog:** `content/changelog/TCHG-0007.md`

---

## 1. What was built

A deterministic crosslink/navigation layer that turns the archive's existing
structured relationships into labeled, bounded, crawlable navigation — without
replacing the Boris graph engine and without touching content prose.

| Artifact | Purpose |
| --- | --- |
| `scripts/crosslinks.py` | derivation layer (loaders → typed/classified edges → reverse & multi-hop derived edges → context-appropriate sections → machine export → HTML injection → RAG companion) |
| `scripts/validate_crosslinks.py` | build-gate validation, checks CXL-01…CXL-10 |
| `metadata/coa-records.jsonl` | durable COA intake point (empty today; schema `metadata/coa-measurement.schema.json`) |
| `content/cannabinoids/d9-thc.md` | new `cannabinoids/TCBN-0009` Δ9-THC record (closed the documented "no canonical THC record" gap; needed for the Definition of Done) |
| `tests/test_crosslinks.py` + `tests/fixtures/crosslinks/` | 28 tests incl. the Definition-of-Done scenario |
| `bin/validate_graph.sh`, `scripts/ted-build.sh`, `themes/cantilever/assets/cantilever.css`, `content/changelog/TCHG-0007.md` | wiring, styling, changelog |
| `metadata/id-map.jsonl` | regenerated via the repo's own `ted_ids.py --write` (413 pages; the Δ9-THC record + recent content waves were missing from the committed map) |

## 2. Relationship categories

Five edge classes, never mixed, never silently upgraded (see architecture
doc §3): `direct` (frontmatter semantic relations), `source` (attribution to
a named non-entity — rendered as text, never a fabricated link), `measurement`
(COA edges), `identity_claim` (claim registry with entity objects), `derived`
(reverse/multi-hop navigation with evidence traces).

Live graph on this tree: **413 entities, 1,354 edges** (672 direct · 677
derived · 5 identity_claim; 0 measurement because no verified COA records
exist yet — the honest empty state). 313 entity pages get derived navigation
(collection trunks without meaningful relations are skipped).

## 3. Reverse-edge strategy

Implemented automatically: every forward edge yields a `derived` reverse edge
whose trace is the forward source, so the laboratory page's "Reports issued",
the compound page's "Laboratory reports measuring this compound", the product
page's "Laboratory reports", and the cultivar page's "Products carrying this
name" / "Batch-associated laboratory reports" sections all derive — no manual
bidirectional pairs, no double-maintained-edge disagreement.

## 4. Derived-edge strategy

Multi-hop projections are computed with evidence traces:

- `Cultivar → Compound` ("Compounds observed in associated reports") via
  product/batch cultivar claims → reports → analyte results; the UI note
  states the observation is batch- and report-attached and never asserts a
  cultivar chemotype. The machine export carries the justifying report ids.
- `Compound → Cultivar`, `Product → Compound`, `Compound → Product`
  projections follow the same rule.
- Non-entity breeders/catalog names from the claim registry surface in the
  "Breeder / origin claims" and "Seed / catalog listings" sections as labeled
  text (class `source`), never as links to nonexistent pages.

## 5. Rendering rules

- Context-appropriate section tables per role (compound, cultivar, product,
  laboratory, lab report) plus generic `related` / `backlinks`.
- Caps: 8 items/section, 48 links/page, 3 trace ids/item; full counts always
  shown with "(+N more)".
- Every section and item carries `data-edge-class` / `data-source-class`;
  record kinds are visible badges (`demonstration`, `unverified`) so demo
  records can never be mistaken for verified evidence.
- Injection is idempotent (a prior run's block is replaced) and happens after
  the Boris render — content files stay untouched.
- Deterministic ordering throughout (fixed section table; items by
  evidence-weight then id; sorted keys in the machine export; no timestamps).

## 6. RAG rules

`exports/crosslinks.json` (machine) and `exports/crosslinks-rag.md`
(human/RAG companion) ship with the build. Consumers join these with Boris's
IR/RAG exports and must (a) grade by *source class*, (b) keep derived wording
epistemic ("appears in laboratory reports associated with products labeled
Blue Dream"), and (c) gate any statistical use on `recordKind == verified`.
Both files are gitignored generated artifacts, reproducible from the repo.

## 7. Performance

- Indexes built once (O(E)); per-page sections are O(degree) + bounded
  truncation; no O(N²) expansion.
- Measured on this worktree: full `ted-build.sh` (Boris compile of 413 pages
  + all audits + crosslink derivation/injection of 313 pages) ≈ **19 s**;
  the crosslink pass itself is well under a second and idempotent.

## 8. Definition-of-Done walkthrough

The scenario — add ONE lab report with cultivar claim, laboratory, batch,
THCA, Δ9-THC, β-myrcene, limonene — is exercised by
`tests/test_crosslinks.py::TestDefinitionOfDone` on the fixture site
(`tests/fixtures/crosslinks/`, one `CoaRecord` + claim registry + 8 content
pages). Verified navigation improvements, all derived (the report page's
frontmatter only names the product):

| Entity | Derived navigation now present |
| --- | --- |
| `lab-results/TLAB-0001` (report) | Testing laboratory (TSTL-0001) · Batch (BR-BD-…) · Product (TPRD-0001) · Cultivar claim (TCUL-0001) · 4 measured compounds |
| `products/TPRD-0001` (product) | Cultivar claim · Laboratory reports · 4 observed compounds |
| `testing-laboratories/TSTL-0001` (laboratory) | Reports issued |
| `cultivars/TCUL-0001` (cultivar) | Products carrying this name · Batch-associated reports · 4 observed compounds |
| THCA / Δ9-THC / β-myrcene / limonene | Laboratory reports measuring this compound · Products with measurements · Cultivars observed in associated reports |

No page was hand-edited to produce these links. On the live tree, the same
mechanism activates the moment the first verified `CoaRecord` lands in
`metadata/coa-records.jsonl` (migration `docs/graph/coa-migration.md` Path A);
today the layer honestly renders zero measurement sections because no verified
record exists. Per the migration doc's hard rule, the demo COA's synthetic
values are **not** converted into `CoaRecord` instances, so the live demo
record contributes its (already published) relationships only.

The Δ9-THC record (`cannabinoids/TCBN-0009`) was created because the COA model
docs flagged it as the missing canonical compound, and the Definition of Done
names it. It reuses the archive's already-verified citations (Dussy 2005;
Lovestead & Bruno 2017; Wang 2016; García-Valverde 2022; Jikomes 2018; Eyal
2023; de Meijer 2003) plus the standard identity data for the compound.

## 9. Validation results

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | **245 tests, OK** (6 skipped: network-dependent) — includes the new 28 crosslink tests |
| `python3 scripts/validate_crosslinks.py --root content … --html-dir dist/cantilever` | PASS — 413 entities, 1,354 edges, 0 broken generated links, index pages validated (CXL-11/CXL-12) |
| `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl` | PASS — 413 pages, no files changed (map regenerated with `--write`) |
| `./scripts/ted-build.sh` (Boris compile + ID/link audits + crosslinks + HTML ID audit + public-release audit) | PASS through compile/injection/ID-audit; **313 pages injected, 0 duplicate HTML IDs, 0 broken links** |
| Public-release audit (tree, `--no-history`) | PASS at fail threshold `high` — no findings above threshold from this change |
| HTML ID audit | PASS — 0 pages with duplicate IDs |
| Markdown link audit | PASS — all local Markdown links resolve |

Notes: the local run of `ted-build.sh`'s history scan reports pre-existing
PII-001 history findings from full-clone history (commits by `beau@boorman.tech`
reachable from other branches); CI and Cloudflare deploy use shallow checkouts
(`actions/checkout@v4` default `fetch-depth: 1`), so they never see them, and
they predate this change. The tree-level audits for this change are clean.

## 10. Honest limitations and future scaling

- **Live measurement sections are empty** until the first verified COA record
  exists — by design (fixture/synthetic values must never become publication
  data). The mechanism is proven by tests and ready for Path A ingestion.
- Hand-written "Related pages" lists in content remain and are additive; they
  do not conflict with the marked-up generated sections. Retiring them is a
  content decision for a later wave.
- Dedicated paginated index pages are **built** (not future work): any
  section whose count exceeds `MAX_ITEMS_PER_SECTION` gets index pages at
  `INDEX_PAGE_SIZE` (100) items each, linked from the entity page as "View
  all N" with a prev/page/next pager. The live build currently emits **17
  index pages** (e.g. `jurisdictions/TJUR-0022-backlinks.html` +
  `-backlinks-2.html` covering 104 backlinks, verified to paginate
  correctly). CXL-11/CXL-12 keep them in sync with the graph.
- The machine export is a single deterministic JSON file today; per-collection
  JSONL is the planned incremental-retrieval form at scale.
- Reverse navigation of *direct* relations ("Pages that link here") is capped
  and includes relation sources; it is deliberately not a full backlink crawl
  of the Boris dependency graph.

## 11. Files changed / added

**Added:** `scripts/crosslinks.py`, `scripts/validate_crosslinks.py`,
`metadata/coa-records.jsonl`, `content/cannabinoids/d9-thc.md`,
`content/changelog/TCHG-0007.md`, `tests/test_crosslinks.py`,
`tests/fixtures/crosslinks/**`, `docs/crosslinking-architecture.md`,
`reports/crosslinking-implementation.md`.

**Modified:** `bin/validate_graph.sh`, `scripts/ted-build.sh`,
`themes/cantilever/assets/cantilever.css`, `metadata/id-map.jsonl`
(regenerated via `ted_ids.py --write`).

No content `relations:` lines were edited; no prose was touched; nothing was
merged.
