# Graph Connectivity & Orphan Hunter Report

**Agent 9 — Graph Connectivity & Orphan Hunter**
**Branch:** `agent/graph-connectivity`
**Date:** 2026-08-08
**Inputs:** `content/` (Boris site graph), `research/_index/manifest.jsonl` (195 records · 132 subjects), `research/_index/ingestion-queue.md`, `research/_index/verification-ledger.md`

## Goal

Prevent the site from becoming hundreds of excellent but isolated pages: find orphan entities, weak components, missing high-value edges, and duplicate concepts — then add only **high-confidence relationships supported by existing evidence**.

## Method

1. Parsed every `content/**/*.md` frontmatter into an entity graph (entities = `id`, edges = `relations`).
2. Computed connected components, isolated vertices, incoming/outgoing degree, and cross-collection gaps.
3. Cross-referenced the research corpus manifest (195 records) for subjects verified at the research level (`primary-sources-verified` = 176 records · 115 subjects) to identify candidate identities and missing entities.
4. Added 96 edges — every one mirroring a body assertion already present in the edited page or in the site's own reference standards (TREF-0001/0002/0003). No speculative edges; no new entities; no fixture data promoted.

## Entity counts (before / after)

| Metric | Before | After |
| --- | --- | --- |
| Entities (content pages with `id`) | 207 | 207 |
| Relation edges | 351 | **447** (+96) |
| Edge kinds | `relates_to` 342 · `supersedes` 8 · `depends_on` 1 | `relates_to` 438 · `supersedes` 8 · `depends_on` 1 |
| Weakly connected components | 53 | **30** |
| Fully isolated entities | 48 | **28** |
| Entities with no incoming edges | 97 | 95 |
| Entities with no outgoing edges | 54 | 30 |
| Broken relation targets | 0 | 0 |

### Collections (entities per collection)

botanicals 3 · cannabinoids 8 · changelog 3 · contaminants 8 · cultivars 9 · datasets 4 · devices 45 · guides 6 · jurisdictions 1 · lab-results 1 · law-and-use 9 · licenses 1 · manufacturers 13 · organizations 22 · products 1 · recalls 6 · reference 4 · releases 1 · requirements 1 · terpenes 19 · testing-laboratories 18 (+ 24 collection trunks).

## Orphan inventory (before the pass)

48 fully-isolated entities: **24 collection trunks** (navigation pages, expected to be relation-free) plus **24 satellites**:

| Group | Entities | Resolution |
| --- | --- | --- |
| Terpenes (13) | TTRP-0001/0003/0008/0010/0011/0013/0014/0015/0016/0017/0018/0019 (+ TTRP-0002/0004/0005/0006/0007/0009 only had botanical edges) | **Fixed** — 38 edges to TREF-0001/TREF-0003; 3 botanical edges |
| Law-and-use (8) | TLAW-0002..0009 (California DCC registry snapshots) | **Fixed** — 26 edges to TJUR/TLIC/TDTS (+TREQ for manufacturing/testing) |
| Guide | TGDE-0001 (Vaporizer Heating Architectures) | **Fixed** — 4 edges to TREF-0001 + its 3 documented devices |
| Changelog (2) | TCHG-0001, TCHG-0002 | **Intentional** — historical process records; no meaningful edge |
| Release (1) | TREL-0001 (Firmware v1.0.0) | **Intentional** — fixture release record |
| Law-and-use (1) | TLAW-0001 (Ohio Medical Cannabis) | **Unresolved** — no Ohio jurisdiction entity exists; left isolated (see Missing entities) |

**After the pass, 28 fully-isolated entities remain: 24 trunks + 4 intentional/blocked satellites** (TCHG-0001, TCHG-0002, TLAW-0001, TREL-0001).

## Weak components (before)

53 components: 48 singletons, 2 pairs (`botanicals/TBOT-0003 ↔ terpenes/TTRP-0009`; `guides/TGDE-0003 ↔ reference/TREF-0002`), and **three mutually disconnected clusters**:

| Cluster | Size | Collections | Problem |
| --- | --- | --- | --- |
| Device world | 64 | devices 45 · manufacturers 13 · reference 3 · guides 2 · changelog 1 | No link to compounds or standards consumers |
| Regulatory world | 61 | contaminants 8 · datasets 4 · jurisdictions 1 · licenses 1 · organizations 22 · recalls 6 · requirements 1 · testing-laboratories 18 | No link to the device/chemistry world |
| Chemistry world | 30 | botanicals 2 · cannabinoids 8 · cultivars 9 · guides 2 · lab-results 1 · products 1 · terpenes 7 | No link to the site's own evidence standards |

After the pass the chemistry world merged with the device world through the reference standards: **2 clusters** — merged device+chemistry+reference (110 members) and regulatory (69 members). The two clusters remain separate because no evidence-backed cross edge exists (see Missing high-value edges).

## Edges added (96, by group)

### 1. Compounds → the archive's reference standards (55 edges) — the biggest gap

Every terpene page carries a pressure-referenced boiling-point table and evidence-labeled biological sections; every cannabinoid page carries evidence sections; every cultivar page carries the cultivar-identity disclaimer. These are exactly the conformance relationships TREF-0001 ("Every terpene record in this archive reports the reference pressure alongside the value") and TREF-0003 define. Verified per-page before adding.

- 19 terpenes → `relates_to=reference/TREF-0001` (Physical Property Data Standards) — 19 edges
- 19 terpenes → `relates_to=reference/TREF-0003` (Evidence Labels and Claim Grammar) — 19 edges
- 8 cannabinoids → `relates_to=reference/TREF-0003` — 8 edges
- 9 cultivars → `relates_to=reference/TREF-0002` (Cultivar Name, Product Name, and Chemovar) — 9 edges

These 55 edges are the bridges that pulled the isolated chemistry pages into the device/reference component.

### 2. Terpene → botanical source (3 edges, evidence-backed)

Only where the page's "Occurrence outside cannabis" section lists a modeled botanical (Citrus/Hops/Lavender):

- `terpenes/TTRP-0019` Valencene → `botanicals/TBOT-0001` (Valencia orange, grapefruit, mandarin)
- `terpenes/TTRP-0015` Fenchol → `botanicals/TBOT-0001` (lime peel, *Citrus aurantiifolia*)
- `terpenes/TTRP-0010` Nerolidol → `botanicals/TBOT-0001` (neroli / bitter orange, *Citrus aurantium*)

Chamomile, eucalyptus, rosemary, fennel, guaiacwood, etc. are **not** linked because those botanicals have no entity (see Missing entities).

### 3. Law-and-use → regulatory graph (26 edges)

All eight California licensing pages are **Department of Cannabis Control license-registry snapshots** (per their own summaries), so each connects to the site's California regulatory spine:

- 8 pages → `jurisdictions/TJUR-0001` (California), `licenses/TLIC-0001` (aggregate registry summary), `datasets/TDTS-0001` (the DCC License Registry dataset) — 24 edges
- `TLAW-0005` Manufacturing and `TLAW-0008` Testing Laboratory additionally → `requirements/TREQ-0001` (the mandatory testing panel that governs manufactured goods and testing labs) — 2 edges

### 4. Guide ↔ device (7 edges)

- `guides/TGDE-0001` (Vaporizer Heating Architectures) → `reference/TREF-0001` (already linked in its body) and → `devices/TED-0001` (Arizer Solo III), `TED-0002` (DynaVap M7), `TED-0003` (Mighty+) — the three devices its own documentation table lists — 4 edges
- Reciprocal: `TED-0001`, `TED-0002`, `TED-0003` → `guides/TGDE-0001` — 3 edges

### 5. Manufacturer edges (2)

- `manufacturers/TMFR-0001` (Arizer) → `devices/TED-0001` — Arizer was the **only manufacturer with zero outgoing edges**; this completes the device↔manufacturer bidirectional pattern used by every other manufacturer.
- `manufacturers/TMFR-0008` (Lotus) → `manufacturers/TMFR-0007` (INHALE/Vapman) — the Lotus page explicitly states "Acquiring Manufacturer: INHALE Vaporizers (South Tyrol, Italy; also produces Vapman)". Verified corporate relationship per `research/_index/verification-ledger.md`.

### 6. Demo-record pair completion (2 edges)

- `cultivars/TCUL-0001` (Blue Dream) → `products/TPRD-0001` — mirrors the existing body link "Associated Commercial Products" and the existing `TPRD-0001 → TCUL-0001` edge.
- `lab-results/TLAB-0001` → `cultivars/TCUL-0001` — mirrors the COA body link "Genetic Cultivar Overview: Blue Dream Cultivar Page".

Both targets are explicitly labeled **demonstration/sample** records; the edges are graph metadata mirroring body assertions and do **not** promote fixture data into verified evidence (their `demo-sample-record-warning` includes are untouched).

### 7. Reference standard linkage (1)

- `reference/TREF-0001` → `reference/TREF-0003` — TREF-0001's body already links the evidence standard; this is the graph version of that assertion.

## Missing high-value edges (not added — need entities or evidence first)

| Gap | Why not added | Next work |
| --- | --- | --- |
| **Devices ↔ recalls** | The Arizer Solo II / Solo III CPSC recalls are documented in `TED-0001`/`arizer.md` with primary CPSC sources, but the `recalls/` collection contains only DCC (California) recall entities. No recall entity exists for any device. | Create `TRCL-` entities for the two Arizer CPSC recalls (primary sources already cited) and link `TED-0001` ↔ recall; extend to future device recalls. |
| **Manufacturers ↔ organizations (corporate parents)** | `organizations/` holds only DCC-licensed CA entities. Verified corporate parents from the research ledger (INHALE, TopGreen/XMAX, Thermodyne/Utillian, Verdampftnochmal/Cuboo, Slang Worldwide/Firefly, Ispire, PAX/Ploom) have no content entity to point at. | Add parent-company organization entities (verification-ledger already confirms several from first-party sources). |
| **Organizations ↔ testing-laboratories (reverse)** | `TSTL-N → TORG-N` exists for all 18 labs (matched by license number), but `TORG → TSTL` reverse edges were not added because org pages are machine-generated by `scripts/dcc_ingest.py`; the generator emits only `relates_to=jurisdictions/TJUR-0001` for orgs. | Extend `scripts/dcc_ingest.py` (org emitter, ~line 953) to add `relates_to=testing-laboratories/TSTL-N`, then regenerate. |
| **Organizations ↔ recalls (reverse)** | `TRCL → TORG` exists for the 4 CA dispensary recall anchors; reverse edges blocked for the same generator reason. | Same generator change (org → `relates_to=recalls/TRCL-N`). |
| **Cultivar ↔ cannabinoid** | Cultivar pages list terpenes but not cannabinoid ratios. Linking a cultivar to a fixed cannabinoid identity would violate the "cultivar name ≠ fixed chemical profile" rule; COA data would be required. | Add only when a linked batch COA provides the chemotype. |
| **Compounds ↔ datasets (COA aggregates)** | No content dataset entity holds compound-level measurements (`TDTS-*` are DCC license/report datasets). | When the cannabis-results dataset (research subject "Terpene Co-Occurrence") is ingested as a dataset entity, link compounds/cultivars to it. |

## Candidate duplicate identities (free text vs entity)

No exact title duplicates exist in content. The candidates below are **concepts expressed as free text** that should become entities or receive identity review as research subjects are ingested:

**Manufacturer brands/aliases verified in the research corpus but not modeled in content** (107 of 120 researched manufacturer subjects are not yet content):

- Cuboo (Verdampftnochmal house brand — parent **confirmed** VDN Berlin GmbH; prior "VapeFully house brand" attribution is an error, per verification-ledger)
- Utillian (Thermodyne Systems brand — TVAPE is a sibling brand under the same umbrella)
- XMAX / XVape (TopGreen Technology — **identity review pending**; keep distinct until primary-source confirmation)
- Smiss / Flowermate (**identity review pending**; do not collapse)
- 7th Floor / Elev8; Firefly / Slang Worldwide; PAX / Ploom; Ispire; QaromaShop / Koma Precision; Pulsar / AFG Distribution; Smono / Reinhart GmbH & Co. KG; The Sublimator / SubCulture Inc.; G-Spot (glass-bong maker, primarily)
- INHALE / element medical AG (**modeled** as TMFR-0007; Lotus TMFR-0008 is its sibling — edge added this pass)

**Device families named inside manufacturer records but not modeled as `TED-` entities** (wave-2 candidates, not duplicates):

- Arizer: Solo II MAX, Air SE, Air MAX, Extreme Q, XQ2, V-Tower (only Solo III = TED-0001 is modeled)
- DynaVap: M, M7 XL, Omni, VonG, HyperDyn families (only M7 = TED-0002 is modeled)
- Storz & Bickel: Venty, Crafty+, Volcano Medic 2, Mighty+ Medic (TED-0003/0034/0035 modeled; Medic variants are distinct certified entities)

**Compounds researched but absent from content:** CBC, CBDVA, CBN, Δ9-THC, THCVA (13 research subjects vs 8 content entities).

**Missing entities that block edges:** Ohio jurisdiction profile (TLAW-0001 orphaned); botanicals mentioned by terpene pages but not modeled (chamomile, eucalyptus, rosemary, fennel, guaiacwood, neroli, rose, geranium); a content entity for the "Manufacturer & Brand Universe" research subject.

## Files added

- `reports/graph-connectivity.md` (this report)

## Files modified (53)

- **Terpenes (19):** alpha-bisabolol, alpha-humulene, alpha-pinene, alpha-terpineol, beta-caryophyllene, beta-myrcene, beta-pinene, camphene, d-limonene, eucalyptol, fenchol, geraniol, guaiol, linalool, nerolidol, ocimene, sabinene, terpinolene, valencene
- **Cannabinoids (8):** cbca, cbd, cbda, cbdv, cbg, cbga, thca, thcv
- **Cultivars (9):** blue-dream, blueberry, durban-poison, jack-herer, mazar, northern-lights, skunk-1, strawberry-cough, super-skunk
- **Law-and-use (8):** TLAW-0002..0009
- **Devices (3):** TED-0001, dynavap-m7 (TED-0002), mighty-plus (TED-0003)
- **Manufacturers (2):** arizer (TMFR-0001), TMFR-0008 (Lotus)
- **Guides (1):** TGDE-0001
- **Reference (1):** TREF-0001
- **Lab-results (1):** example-producer-blue-dream-batch-123 (TLAB-0001)
- **Scripts (1):** `scripts/dcc_sync.py` — law-and-use generator now emits the same regulatory relations (`relations_for_category()`), so regenerated DCC licensing pages keep the new edges instead of reverting to `relations: []`. Verified: generator output for "Testing Laboratory" and "Cultivation" categories matches the committed files byte-for-byte on the relations line.

Every content edit is a single frontmatter `relations` line; no body text, no frontmatter schema changes, no mass reformatting.

## Entities created

None — this is an edge-only connectivity pass. No new entities were needed to express any of the 96 relationships (all targets already existed).

## Graph relationships created

96 `relates_to` edges, grouped above. All targets validated to exist (0 broken edges via `validate_relations` and Boris). Bidirectional pair convention preserved (device↔manufacturer, guide↔device, product↔cultivar); standards remain one-way (TREF pages do not enumerate conforming pages).

## Primary sources verified

No new material claims were published, so no new primary-source verification was required. The relationships added rest on the pages' own documented content, verified by inspection:

- TREF-0001's assertion that every terpene record reports reference pressure — confirmed against all 19 terpene pages (`Reference pressure` row + evidence sections present in each).
- Law-and-use pages' summaries ("Department of Cannabis Control licensed-… establishment registry snapshot") — match the site's California regulatory entities (TJUR-0001, TLIC-0001, TDTS-0001, TREQ-0001).
- Lotus → INHALE corporate relationship — stated on the Lotus page with INHALE official pages cited; corroborated by `research/_index/verification-ledger.md` (INHALE/Vapman verified `primary-sources-verified`).
- TGDE-0001's device documentation table lists TED-0001/0002/0003 — confirmed in the guide body.
- DCC registry identity pairs (TORG ↔ TSTL) matched on license number (e.g., C8-0000013-LIC) for the documented-but-not-added reverse edges.

Research corpus reports were used only as discovery/verification aids, never as evidence for an edge; the manifest's `verification_status` field was used to decide which corporate identities are safe to mention as candidates (verified) versus which need review (Smiss/Flowermate, TopGreen XMAX/XVape).

## Uncertain claims left unresolved

- **TLAW-0001 (Ohio) remains orphaned** — the site has no Ohio jurisdiction entity; creating one is a content task (research subject "US Cannabis Regulatory Data Availability" is `unverified` and does not yet cover Ohio specifically).
- **Device↔recall edges** await recall entities for the Arizer CPSC events (content exists; entities do not).
- **ORG→TSTL / ORG→TRCL reverse edges** not implemented (generator-owned content); correct extension point documented above.
- **Cultivar→cannabinoid edges** deliberately omitted (chemotype variability rule).
- Demo records (TPRD-0001, TLAB-0001) are linked but remain labeled demonstration; their numeric content stays excluded from verified framing.
- 19 `unverified` research records (mostly Priority-3) were not used for any identity or edge decision.

## Validation results

| Check | Result |
| --- | --- |
| `python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl` | PASS — validated 207 pages; no files changed |
| `python3 scripts/audit_markdown_links.py content` | PASS — all local Markdown links resolve |
| `validate_relations(content)` (project's own guard) | PASS — 0 broken relation targets |
| `bin/boris check --input content --format json` | PASS — 0 diagnostics; only baseline `unreferenced_page` findings (178, tolerated by `bin/validate_graph.sh`); frontmatter schema intact |
| `python3 -m unittest discover -s tests` | PASS — 154 tests OK, 4 skipped (network-dependent) |
| `python3 -m py_compile scripts/dcc_sync.py` + generator relations smoke test | PASS — output matches committed law-and-use relations |

`bin/boris` was provisioned locally via `./scripts/ensure-boris.sh --provision` (repo's own mechanism; binary is gitignored).

## Research corpus records consumed

- `research/_index/manifest.jsonl` (195 records) — subject inventory, aliases, verification status, ingestion status, target collections
- `research/_index/ingestion-queue.md` — priority rubric and target-collection guidance (e.g., terpenes → terpenes+botanicals; cannabinoids → botanicals+reference)
- `research/_index/verification-ledger.md` — corporate-identity confirmations and errata (INHALE/Vapman/Lotus, Cuboo/VDN Berlin, Utillian/Thermodyne, Smiss/Flowermate and TopGreen XMAX/XVape identity-review flags)
- `research/README.md` — identity, alias, and duplicate rules (no collapsing without research support; chemically distinct entities never merged)

## Suggested next work

1. **Create device-recall entities** for the Arizer Solo II / Solo III CPSC recalls (primary sources already cited in `TED-0001`/`arizer.md`) and link `TED-0001` ↔ recall; generalize to future device recalls.
2. **Add parent-company organization entities** for the verified corporate relationships (INHALE, TopGreen, Thermodyne, Verdampftnochmal, Slang Worldwide) and link them to `TMFR-` records — this bridges manufacturers into the organizations graph.
3. **Generator reverse edges**: extend `scripts/dcc_ingest.py` org emitter with `relates_to=testing-laboratories/TSTL-N` and `relates_to=recalls/TRCL-N`, then regenerate.
4. **Ingest the missing researched compounds** (CBC, CBDVA, CBN, Δ9-THC, THCVA) and the unmodeled device families (Arizer Air/Extreme Q/XQ2/V-Tower, DynaVap Omni/VonG/HyperDyn, S&B Venty/Crafty+/Medic) as wave-2 entities, then wire their edges.
5. **Ohio jurisdiction profile** so TLAW-0001 can join the regulatory component; treat the "US Regulatory Data Availability" research subject as the starting point but verify before use (currently `unverified`).
6. **Add a graph-connectivity guard test** (e.g., a pytest that fails if any non-trunk satellite collection is fully isolated) so future content waves cannot silently create orphans again.
