# Research Corpus Ingestion Queue

**Agent 8 — Research Corpus Ingestion Queue**  
**Date:** 2026-08-08  
**Inputs:** `_index/manifest.jsonl` (195 records · 132 subjects), `_index/inventory.md`, `_index/unresolved.md`, `_index/duplicate-groups.md`, `reports/source-verification-wave-01.md`

This queue turns the research corpus itself into an actionable work plan: which subjects are ready to ingest, which need verification or reconciliation first, and where each subject should land on the site. Machine-readable fields were added to every manifest record; this page is the human-readable view.

## Field definitions

| Field | Values | Meaning |
| --- | --- | --- |
| `verification_status` | `unverified` · `partially-verified` · `primary-sources-verified` | Whether the record's material claims have been traced to primary/authoritative sources. The 14 Priority-1 subjects (32 records) are `primary-sources-verified` per `_index/verification-ledger.md` (2026-08-08 pass). `partially-verified` marks the 15 subjects whose **published site content** was checked against primary sources in `reports/source-verification-wave-01.md` (their corpus records remain unverified). |
| `primary_source_coverage` | `weak` · `moderate` · `strong` | **Reported** ledger composition: how much of the report's material rests on primary/authoritative sources (official manufacturer documentation, manuals, patents, SEC/FDA/regulatory, government, NIST/PubChem/PMC/PubMed, peer-reviewed literature) versus secondary (retailer, review, forum, blog). Assessed from each report's own source ledger. This is **not** an independent verification. |
| `ingestion_status` | `not-started` · `queued` · `in-progress` · `incorporated` · `needs-review` | Pipeline state of the corpus record. `incorporated` = published site content traceable to this corpus exists. `needs-review` = record requires attention before reuse (known ledger errors, unresolved claims, identity ambiguity). |
| `target_collections` | site collection list | The site collections (per `content/` and `metadata/id-policy.json`) the subject should feed. |
| `priority` | 1 · 2 · 3 | Queue position per the rubric below. |

## Priority rubric

- **Priority 1 — ready:** structured artifact **and** export/source present, strong reported primary-source coverage, clear subject identity, no known ledger issues, high project relevance.
- **Priority 2 — needs work:** complete research with gaps — artifact+export pairs with moderate coverage, subjects with multiple independent runs needing reconciliation, export-only subjects with strong coverage (missing artifact), or records with known ledger errors / unresolved claims.
- **Priority 3 — lowest:** export-only with weak or moderate sources and no reconciliation need, identity ambiguity (Smiss/Flowermate, TopGreen XMAX vs XVape), artifact-only records (incomplete research, no source), low-relevance meta material.

## Honesty rules applied

1. Nothing is marked `primary-sources-verified` merely because a Perplexity report cited a primary source — the ledger is reported coverage, not proof.
2. Coverage labels describe the **reported** source ledger. For the 14 Priority-1 subjects they were independently re-verified in `_index/verification-ledger.md`; for all other subjects they remain reported-only.
3. Corpus documents were **not** rewritten. Three corpus-ledger citation errors and unresolved claims discovered in the source-verification wave are flagged via `ingestion_status: needs-review` + `queue_notes` instead.
4. Archived duplicates (9 redundant records) and the meta-research prompt template are excluded from all queues.

## Queue summary

| Queue | P1 | P2 | P3 |
| --- | --- | --- | --- |
| Manufacturers & Devices | 11 | 69 | 8 |
| Terpenes | 0 | 19 | 0 |
| Cannabinoids | 2 | 11 | 0 |
| Cross-Cutting Chemistry | 1 | 2 | 4 |
| Cultivar / Chemotype Research | 0 | 1 | 1 |
| Laboratory Research | 0 | 0 | 1 |
| Jurisdictions | 0 | 1 | 0 |

---

## Manufacturers & Devices

### Priority 1

- **P1 · Ashh Inc. (d/b/a Ooze Life / Ooze Tech)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Atmos Nation LLC (d/b/a AtmosRX, Atmos Rx)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Boundless Technology (BMIC)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Dr. Dabber, Inc.** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Green Curative, Inc. (dba Healthy Rips)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · INHALE (formerly element medical AG) — Vapman** — artifact, export, +1 archived duplicate · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Ispire Technology Inc. (NASDAQ: ISPR)** — artifact, export, +1 archived duplicate · strong coverage · unverified
  - → manufacturers, devices
- **P1 · JTJS Products Oy / JTJS Europe Oy (TinyMight)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Magic-Flight** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · Oglesby & Butler Ltd (IOLITE / WISPR)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices
- **P1 · YLL Induction Heaters (YLLVAPE)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices

### Priority 2

- **P2 · 7th Floor, LLC (dba Elev8 Glass Gallery)** — export · strong coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · AirVape (Apollo Vaporizer)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Arizer (Arizer Tech Inc.)** — export · strong coverage · partially-verified · **incorporated**
  - → manufacturers, devices · ⚠ Published site content exists; see content/
- **P2 · AroMed GmbH (Green Gold)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · BC Vaporizer** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Black Leaf** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Camouflet Ltd.** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Cannabis Hardware, LLC** — artifact, export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Cuboo (VapeFully House Brand)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Custom Log Vape Collective / Koolance (Log Vape Lineage)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · DaVinci Tech (DVNT Holdings)** — export · strong coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · De Verdamper (Evert)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Ditanium Vapor (DitaniumVapor)** — export, +1 archived duplicate · moderate coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · DynaVap, LLC** — export · strong coverage · partially-verified · **incorporated**
  - → manufacturers, devices · ⚠ Published site content exists; see content/
- **P2 · Eagle Bill / Shake & Vape (Frank William Wood)** — artifact, export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Ed's TNT (Woodscents)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Element Vaporizer (Element Pocket)** — export, +1 archived duplicate · strong coverage · unverified
  - → manufacturers, devices
- **P2 · EpicVape LLC (Epickai)** — artifact, export · strong coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Exxus Vape** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Firefly Vapor (Slang Worldwide)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Firewood Vapes** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Focus V (Focus Vape Technology)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · G-Spot Vaporizer** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Global Dry-Herb Vaporizer Manufacturer & Brand Universe** — artifact, export, +1 archived duplicate · strong coverage · unverified
  - → manufacturers, reference, devices
- **P2 · Grenco Science, Inc. (G Pen)** — artifact, export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Hamilton Devices** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Haze Technologies, Inc.** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Heat Island / Toasty Top** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · HerbalAire** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Herborizer** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · HoneyStick** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Hopper Labs, Inc. (Grasshopper)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Jaxels Art (VapBong / FlavorMaster)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · KandyPens** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · King Palm (Dry Herb Hardware Line)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · LinX Vapor** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Lookah Tech** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Lotus Vaporizer (Mendocino Therapeutics / INHALE)** — artifact, export · moderate coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Mad Heaters Ltd.** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · MiniVAP** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · PAX Labs, Inc. (formerly Ploom)** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Pharmacopeia Inc. (Inhalater)** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Pulsar Vaporizers (AFG Distribution, Inc.)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · QaromaShop (Koma Precision Sdn. Bhd.)** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Shatterizer** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Shenzhen Crossing Technology Co., Ltd. (Crossing Tech)** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Shenzhen Weecke Technology Co., Ltd. (Fenix / OEM)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Shenzhen Yocan Technology Co., Ltd. (Yocan)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Smono** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Source Vapes (SOURCEvapes)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Sticky Brick Labs** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Storz & Bickel GmbH & Co. KG** — export · strong coverage · partially-verified · **incorporated**
  - → manufacturers, devices · ⚠ Published site content exists; see content/
- **P2 · Sutra Vape** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · The Sublimator** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Triihouse (Daisy / Lily)** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Underdog Vaporizers** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Utillian (TVape house brand)** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · VapeXhale, Inc. (later Hanu Labs, Inc.)** — artifact, export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Vapir, Inc.** — artifact, export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Vapolution** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · VaporBlunt** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · VaporFi** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · VaporGenie** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Vaporbrothers, Inc.** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Vapvana, LLC** — artifact, export, +1 archived duplicate · strong coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Vivant Inc.** — export · strong coverage · unverified
  - → manufacturers, devices
- **P2 · Wolkenkraft** — export · moderate coverage · unverified
  - → manufacturers, devices
- **P2 · Wulf Mods LLC** — export · moderate coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Zeus Arsenal** — export · strong coverage · unverified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion

### Priority 3

- **P3 · FlytLab** — export · weak coverage · unverified
  - → manufacturers, devices
- **P3 · Goboof Products Limited (Alfa)** — artifact · strong coverage · unverified
  - → manufacturers, devices
- **P3 · Mig Vapor LLC** — artifact · moderate coverage · unverified
  - → manufacturers, devices
- **P3 · Smiss Technology Co., Ltd.** — export · strong coverage · unverified · **needs review**
  - → manufacturers, devices · ⚠ IDENTITY REVIEW: Flowermate parentage claimed but unverified; do not collapse without primary-source confirmation; Multiple independent research runs; reconcile before ingestion
- **P3 · TopGreen Technology (XMAX)** — export · moderate coverage · unverified · **needs review**
  - → manufacturers, devices · ⚠ IDENTITY REVIEW: XMAX vs XVape brand split; keep distinct until primary-source confirmation
- **P3 · Tronian** — export · weak coverage · unverified
  - → manufacturers, devices
- **P3 · Vaporfection International, Inc.** — artifact · moderate coverage · unverified
  - → manufacturers, devices
- **P3 · XVape (TopGreen Technology)** — export · strong coverage · unverified · **needs review**
  - → manufacturers, devices · ⚠ IDENTITY REVIEW: XMAX vs XVape brand split; keep distinct until primary-source confirmation

---

## Terpenes

### Priority 2

- **P2 · Camphene** — export · moderate coverage · unverified
  - → terpenes, botanicals
- **P2 · D-Limonene** — artifact, export · strong coverage · partially-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: corpus ledger citation error (Sanshita/Devi Int J Nanomedicine 2025, not 'Devi N Pharmaceutics'); Published site content exists; see content/
- **P2 · Eucalyptol (1,8-Cineole)** — artifact, export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Multiple independent research runs; reconcile before ingestion; Published site content exists; see content/
- **P2 · Fenchol** — export · moderate coverage · unverified
  - → terpenes, botanicals
- **P2 · Geraniol** — artifact, export · moderate coverage · unverified
  - → terpenes, botanicals
- **P2 · Guaiol ((–)-Guaiol / Champacol)** — export · moderate coverage · unverified
  - → terpenes, botanicals
- **P2 · Linalool** — artifact, export · moderate coverage · partially-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: corpus ledger citation error (Linck et al. 2010, not 'Kashiwadani et al.'); CNS-depressant claim unresolved; Published site content exists; see content/
- **P2 · Nerolidol** — artifact, export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · Ocimene (α/β isomers)** — artifact, export · moderate coverage · partially-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: antifungal claim unresolved (no primary source located in wave 01); Multiple independent research runs; reconcile before ingestion; Published site content exists; see content/
- **P2 · Sabinene** — export, +1 archived duplicate · moderate coverage · unverified
  - → terpenes, botanicals
- **P2 · Terpinolene** — artifact, export · moderate coverage · partially-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: corpus ledger citation error (Aydin et al. 2013, not 'Gasic et al.') - see reports/source-verification-wave-01.md; Published site content exists; see content/
- **P2 · Valencene** — artifact, export · moderate coverage · unverified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · α-Bisabolol** — artifact, export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · α-Humulene** — export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Multiple independent research runs; reconcile before ingestion; Published site content exists; see content/
- **P2 · α-Pinene** — artifact, export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · α-Terpineol** — export · moderate coverage · unverified
  - → terpenes, botanicals
- **P2 · β-Caryophyllene** — export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · β-Myrcene** — export · moderate coverage · partially-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · β-Pinene** — export · strong coverage · partially-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: cellular cytotoxic claim unresolved (no primary source located in wave 01); Published site content exists; see content/

---

## Cannabinoids

### Priority 1

- **P1 · Cannabidiol (CBD)** — artifact, export · strong coverage · unverified
  - → botanicals, reference
- **P1 · Δ9-Tetrahydrocannabinolic Acid A (THCA)** — artifact, export, +2 archived duplicate · strong coverage · unverified
  - → botanicals, reference

### Priority 2

- **P2 · Cannabichromene (CBC)** — export · strong coverage · unverified
  - → botanicals, reference
- **P2 · Cannabichromenic Acid (CBCA)** — artifact, export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Cannabidiolic Acid (CBDA)** — export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Cannabidivarin (CBDV)** — artifact, export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Cannabidivarinic Acid (CBDVA)** — export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Cannabigerol (CBG)** — artifact, export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Cannabigerolic Acid (CBGA)** — artifact, export · moderate coverage · unverified
  - → botanicals, reference · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Cannabinol (CBN)** — export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Tetrahydrocannabivarin (THCV)** — artifact, export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Δ9-Tetrahydrocannabinol (THC)** — export · moderate coverage · unverified
  - → botanicals, reference
- **P2 · Δ⁹-Tetrahydrocannabivarinic Acid (THCVA)** — export · moderate coverage · unverified
  - → botanicals, reference

---

## Cross-Cutting Chemistry

### Priority 1

- **P1 · Cannabis Aroma Chemistry Beyond Terpenes** — artifact, export · strong coverage · unverified
  - → botanicals, reference

### Priority 2

- **P2 · Cannabis Terpene Co-Occurrence and Profile Structure** — artifact, export · moderate coverage · unverified
  - → terpenes, botanicals, reference
- **P2 · Evidence Architecture for Cannabis Compounds, Profiles, and Reported Effects** — export · strong coverage · unverified · **incorporated**
  - → reference, guides · ⚠ Published site content exists; see content/

### Priority 3

- **P3 · Batch-to-Batch Chemical Variability Within Cannabis Cultivars** — export · moderate coverage · unverified
  - → cultivars, lab-results, datasets
- **P3 · Cannabis Post-Harvest Chemistry** — export · moderate coverage · unverified
  - → reference, botanicals
- **P3 · Cannabis Thermal Extraction, Vaporization, and Aerosol** — export · moderate coverage · unverified
  - → reference, guides, safety
- **P3 · Geographic & Jurisdictional Variation in Cannabis Chemistry Research Framework** — export · moderate coverage · unverified
  - → jurisdictions, datasets, reference

---

## Cultivar / Chemotype Research

### Priority 2

- **P2 · Cannabis Cultivar Provenance and Identity Resolution** — artifact, export · moderate coverage · unverified
  - → cultivars, reference

### Priority 3

- **P3 · Cannabis Cultivar Names Versus Measured Chemotypes** — export · moderate coverage · unverified · **incorporated**
  - → reference, cultivars · ⚠ Published site content exists; see content/

---

## Laboratory Research

### Priority 3

- **P3 · Cannabis Laboratory Measurement Comparability** — export · moderate coverage · unverified
  - → testing-laboratories, lab-results, datasets

---

## Jurisdictions

### Priority 2

- **P2 · US Cannabis Regulatory Data Availability — Ranked for Cross-State Cultivar/Batch/Chemistry Graph** — artifact, export · strong coverage · unverified
  - → jurisdictions, datasets, law-and-use

---

## Queue generation report

**Files added:** `research/_index/ingestion-queue.md`; `scripts/research_queue_analysis.py`, `scripts/research_queue_assign.py`, `scripts/research_queue_doc.py` (reproducible queue tooling).

**Files modified:** `research/_index/manifest.jsonl` — every record gained `verification_status`, `primary_source_coverage`, `ingestion_status`, `target_collections`, `priority`; 65 records also carry `queue_notes` (ledger errors, identity review, multi-run reconciliation, incorporated flag, archived-duplicate exclusion). No existing field values changed.

**Entities created:** none — this pass adds machine-readable metadata and a queue document; no knowledge-graph entities or site content were created.

**Graph relationships created:** none.

**Primary sources verified:** none in this pass (queue-building, not verification). Site-side verification already recorded in `reports/source-verification-wave-01.md` covers 15 subjects and is reflected as `partially-verified`.

**Uncertain claims left unresolved:** corpus-ledger citation errors (terpinolene, linalool, d-limonene) and unresolved biological claims (ocimene antifungal, linalool CNS-depressant, β-pinene cytotoxic) flagged `needs-review`; identity ambiguity for Smiss/Flowermate and TopGreen XMAX/XVape requires a human decision.

**Validation results:** all 195 manifest records re-parsed as JSON after enrichment; field presence asserted for every record; zero pre-existing field values changed; priority/verification/coverage/ingestion distributions reviewed by hand against the rubric and the wave-01 ledger.

**Research corpus records consumed:** all 195 manifest records; `_index/inventory.md`; `_index/unresolved.md`; `_index/duplicate-groups.md`; source ledgers of all artifact/export files (domain + ledger-type analysis).

**Suggested next work:**
- Ingest the 14 Priority-1 subjects (artifact + export + strong coverage): build site content per `target_collections`.
- Run a verification pass on Priority-1/Priority-2 records, tracing each material claim to its primary source and promoting records to `primary-sources-verified`.
- Resolve the flagged `needs-review` records: correct the three corpus-ledger citations (terpinolene, linalool, d-limonene) via a ledger-errata file, re-check the ocimene/β-pinene/linalool unresolved claims, and take a human decision on Smiss/Flowermate and TopGreen XMAX/XVape identity.
- Reconcile the 13 multi-run subjects into single reconciled artifacts.
