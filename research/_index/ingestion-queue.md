# Research Corpus Ingestion Queue

**Agent 8 — Research Corpus Ingestion Queue**  
**Date:** 2026-08-08  
**Inputs:** `_index/manifest.jsonl` (195 records · 132 subjects), `_index/inventory.md`, `_index/unresolved.md`, `_index/duplicate-groups.md`, `reports/source-verification-wave-01.md`

This queue turns the research corpus itself into an actionable work plan: which subjects are ready to ingest, which need verification or reconciliation first, and where each subject should land on the site. Machine-readable fields were added to every manifest record; this page is the human-readable view.

## Field definitions

| Field | Values | Meaning |
| --- | --- | --- |
| `verification_status` | `unverified` · `partially-verified` · `primary-sources-verified` | Whether the record's material claims have been traced to primary/authoritative sources (official manufacturer documentation, manuals, patents, SEC/regulatory filings, NIST/PubChem/PMC/PubMed, peer-reviewed literature) — see `_index/verification-ledger.md` for per-subject results. **All 195 records (132 subjects) are `primary-sources-verified`** (2026-08-08 verification passes over the Priority-1, Priority-2, Priority-2-remainder, and Priority-3/remaining-Priority-2 subjects, plus two entity-confirmation passes). No records are currently `partially-verified` or `unverified` — the last 19 were promoted in the 2026-08-08 fourth pass (see `_index/verification-ledger.md`). |
| `primary_source_coverage` | `weak` · `moderate` · `strong` | **Reported** ledger composition: how much of the report's material rests on primary/authoritative sources (official manufacturer documentation, manuals, patents, SEC/FDA/regulatory, government, NIST/PubChem/PMC/PubMed, peer-reviewed literature) versus secondary (retailer, review, forum, blog). Assessed from each report's own source ledger. This is **not** an independent verification. |
| `ingestion_status` | `not-started` · `queued` · `in-progress` · `incorporated` · `needs-review` | Pipeline state of the corpus record. `incorporated` = published site content traceable to this corpus exists. `needs-review` = record requires attention before reuse (known ledger errors, unresolved claims, identity ambiguity). |
| `target_collections` | site collection list | The site collections (per `content/` and `metadata/id-policy.json`) the subject should feed. |
| `priority` | 1 · 2 · 3 | Queue position per the rubric below. |

## Priority rubric

- **Priority 1 — ready:** structured artifact **and** export/source present, strong reported primary-source coverage, clear subject identity, no known ledger issues, high project relevance.
- **Priority 2 — needs work:** complete research with gaps — artifact+export pairs with moderate coverage, subjects with multiple independent runs needing reconciliation, export-only subjects with strong coverage (missing artifact), or records with known ledger errors / unresolved claims.
- **Priority 3 — lowest:** export-only with weak or moderate sources and no reconciliation need, identity ambiguity (Smiss/Flowermate, TopGreen XMAX vs XVape), artifact-only records (incomplete research, no source), low-relevance meta material.

## Honesty rules applied

1. Nothing is marked `primary-sources-verified` merely because a Perplexity report cited a primary source — the ledger is reported coverage, not proof. Records were promoted only by the 2026-08-08 verification passes, which traced each promoted subject's material claims to actual primary/authoritative sources; per-subject results are in `_index/verification-ledger.md`.
2. Coverage labels describe the **reported** source ledger of each research report; they are not a substitute for the independent checks recorded in the verification ledger.
3. Corpus documents were **not** rewritten. Ledger citation errors and unresolved claims are flagged via `ingestion_status: needs-review` + `queue_notes`, and identifier errata (CBD/THCA InChIKeys, aroma-chemistry CIDs, sabinene/camphene CAS, Cuboo parentage) are recorded in `_index/verification-ledger.md`.
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

- **P1 · Ashh Inc. (d/b/a Ooze Life / Ooze Tech)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Atmos Nation LLC (d/b/a AtmosRX, Atmos Rx)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Boundless Technology (BMIC)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Dr. Dabber, Inc.** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Green Curative, Inc. (dba Healthy Rips)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · INHALE (formerly element medical AG) — Vapman** — artifact, export, +1 archived duplicate · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Ispire Technology Inc. (NASDAQ: ISPR)** — artifact, export, +1 archived duplicate · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · JTJS Products Oy / JTJS Europe Oy (TinyMight)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Magic-Flight** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · Oglesby & Butler Ltd (IOLITE / WISPR)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P1 · YLL Induction Heaters (YLLVAPE)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices

### Priority 2

- **P2 · 7th Floor, LLC (dba Elev8 Glass Gallery)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · AirVape (Apollo Vaporizer)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Arizer (Arizer Tech Inc.)** — export · strong coverage · primary-sources-verified · **incorporated**
  - → manufacturers, devices · ⚠ Published site content exists; see content/
- **P2 · AroMed (Green Gold GmbH brand)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): entity CONFIRMED — Green Gold GmbH, Am Kavalleriesand 47, 64295 Darmstadt, HRB 96280 (Amtsgericht Darmstadt), Geschäftsführer Hüseyin Yazici, VAT DE 310 203 429, per official shop impressum (greengold-germany.com/impressum); AroMed HQ / AroMed 4.0 sold on the official Green Gold shop. 'AroMed GmbH' corrected to Green Gold GmbH (subject renamed).
- **P2 · BC Vaporizer** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Black Leaf** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Camouflet Ltd.** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Cannabis Hardware, LLC** — artifact, export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Cuboo (Verdampftnochmal House Brand)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): parent company CONFIRMED — Verdampftnochmal (legal entity VDN Berlin GmbH, Karl-Kunger-Str 28, 12435 Berlin) per verdampftnochmal.de/en/cuboo: 'Cuboo is a private label of the German company Verdampftnochmal'. The prior 'VapeFully house brand' attribution is an error — VapeFully is operated by High Experts sp. z o.o. (Kraków, Poland), a distinct legal entity. Cuboo Stick is an XMAX V3 Pro rebrand.
- **P2 · Custom Log Vape Collective / Koolance (Log Vape Lineage)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): NEGATIVE-RESULT subject verified — no entity named 'Custom Log Vape Collective' exists in registries/trademark databases (confirmed); Koolance is an unrelated PC liquid-cooling company (koolance.com, founded 2000, Auburn WA, ISO 9001/14001); the log-vape lineage maps to independently verified makers (Underdog, Ed's TNT, EpicVape/E-Nano, Toasty Top/Heat Island); FlashVap/Purple Days remain community-history.
- **P2 · DaVinci Tech (DVNT Holdings)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion; VERIFIED brand/line; NOTE: legal parent name 'DVNT Holdings' not independently confirmed (export-only) — check business registry at ingestion.
- **P2 · De Verdamper (Evert)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Ditanium Vapor (DitaniumVapor)** — export, +1 archived duplicate · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · DynaVap, LLC** — export · strong coverage · primary-sources-verified · **incorporated**
  - → manufacturers, devices · ⚠ Published site content exists; see content/
- **P2 · Eagle Bill / Shake & Vape (Frank William Wood)** — artifact, export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Ed's TNT (Woodscents)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Element Vaporizer (Element Pocket)** — export, +1 archived duplicate · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): Element Pocket (2011, Switzerland) friction-powered mechanical vaporizer CONFIRMED via the Verdampftnochmal vaporizer-history page (with photos); Element Medical AG/Vapman lineage verified in the Priority-1 pass. The export conflates unrelated 'Element' companies (Element Vape, Element Materials, e-liquid brands) — disambiguate at ingestion.
- **P2 · EpicVape LLC (Epickai)** — artifact, export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Exxus Vape** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Firefly Vapor (Slang Worldwide)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): Slang Worldwide parentage per company/press records.
- **P2 · Firewood Vapes** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Focus V (Focus Vape Technology)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · G-Spot Vaporizer** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): brand identity CONFIRMED first-party — G-SPOT High End Glass, Wertheim, Germany, founded 2000, Panzerschliff 2005, borosilicate 3.3 ISO 3585 (g-spot-bong.de); G-Spot Vaporizer (ca. 2012, German desktop hot-air convection, 100–250 °C) corroborated by Verdampftnochmal history; primarily a glass-bong maker.
- **P2 · Global Dry-Herb Vaporizer Manufacturer & Brand Universe** — artifact, export, +1 archived duplicate · strong coverage · primary-sources-verified
  - → manufacturers, reference, devices · ⚠ NOTE (verification-ledger.md): Tier 1-2 entries corroborated by the 57-subject manufacturer verification pass.
- **P2 · Grenco Science, Inc. (G Pen)** — artifact, export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Hamilton Devices** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): identity CONFIRMED — hamiltondevices.com live; authentic CCELL supplier (partner since 2016), 510/disposable/pod/battery product lines, Folsom CA contact; PS1/PD1 proprietary 510 batteries corroborated by retail and site. Founding-year discrepancy (2012 vs 2018) unresolved.
- **P2 · Haze Technologies, Inc.** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Heat Island / Toasty Top** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · HerbalAire** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Herborizer** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · HoneyStick** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Hopper Labs, Inc. (Grasshopper)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Jaxels Art (VapBong / FlavorMaster)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · KandyPens** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · King Palm (Dry Herb Hardware Line)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · LinX Vapor** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Lookah Tech** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Lotus Vaporizer (Mendocino Therapeutics / INHALE)** — artifact, export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion; VERIFIED product type/maker (Mendocino Therapeutics)/INHALE ownership; NOTE: designer attribution unconfirmed.
- **P2 · Mad Heaters Ltd.** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · MiniVAP** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · PAX Labs, Inc. (formerly Ploom)** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Pharmacopeia Inc. (Inhalater)** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ VERIFIED (2026-08-08 pass): real maker is Pharmacor Technologies (Montreal) per archived official inhalater.com; 'Pharmacopeia Inc.' is a conflation with the Ligand-acquired biotech; caveats: official site sold devices from July 2008; export missed official 5S/6S models (2016–17).
- **P2 · Pulsar Vaporizers (AFG Distribution, Inc.)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · QaromaShop (Koma Precision Sdn. Bhd.)** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Shatterizer** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Shenzhen Crossing Technology Co., Ltd. (Crossing Tech)** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Shenzhen Weecke Technology Co., Ltd. (Fenix / OEM)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Shenzhen Yocan Technology Co., Ltd. (Yocan)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Smono** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): corporate entity CONFIRMED — Reinhart GmbH & Co. KG, Tempelhofer Str. 21, 52068 Aachen, per manufacturer manuals' copyright line and manufacturer info on listings; founding year 2009 not independently confirmed.
- **P2 · Source Vapes (SOURCEvapes)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Sticky Brick Labs** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Storz & Bickel GmbH & Co. KG** — export · strong coverage · primary-sources-verified · **incorporated**
  - → manufacturers, devices · ⚠ Published site content exists; see content/
- **P2 · Sutra Vape** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · The Sublimator** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): official site sublimatorhq.com live; SubCulture Inc. confirmed via official privacy-policy copyright ('Registered Copyright © SubCulture Inc.'); Canadian origin and 2012 founding confirmed on official site ('going beyond the norm in 2012', 'Canadian through and through').
- **P2 · Triihouse (Daisy / Lily)** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Underdog Vaporizers** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Utillian (Thermodyne Systems brand)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): Utillian is a trademark of Thermodyne Systems (Toronto, Canada) per official Utillian manuals on utillian.com; TVAPE is a sibling brand within the same Thermodyne Systems umbrella (Globe Newswire via Yahoo Finance, 2022-12-20). 'TVape house brand' label accurate only at the umbrella level.
- **P2 · VapeXhale, Inc. (later Hanu Labs, Inc.)** — artifact, export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Vapir, Inc.** — artifact, export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Vapolution** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · VaporBlunt** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ NOTE (verification-ledger.md): corporate attribution CONFIRMED via period press release (VaporNation, 2013-02-24): VaporNation = 'an online venture of Better Life Products, Inc.', Marina Del Rey CA; VaporBlunt 2.0 (2013) product details corroborated. Brand defunct today; no current official site.
- **P2 · VaporFi** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · VaporGenie** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Vaporbrothers, Inc.** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Vapvana, LLC** — artifact, export, +1 archived duplicate · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Vivant Inc.** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Wolkenkraft** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices
- **P2 · Wulf Mods LLC** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Zeus Arsenal** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ Multiple independent research runs; reconcile before ingestion

### Priority 3

- **P3 · FlytLab** — export · weak coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ VERIFIED (2026-08-08 pass): first-party flytlab.com/about-us (founded 2013, first tradeshow 2015, H2FLO/FUSE/LIFT/ST!K/CTRL 2.0, 1-yr warranty); summary-only export — full deliverable not in corpus
- **P3 · Goboof Products Limited (Alfa)** — artifact · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ VERIFIED with caveats (2026-08-08 pass): Irish origin + Alfa brand + 2-yr warranty confirmed; CRO 525630 and Castle D Enterprises successor not independently re-verified; artifact address field 'Carlow, Co. Dublin' internally inconsistent — resolve at ingestion
- **P3 · Mig Vapor LLC** — artifact · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ VERIFIED (2026-08-08 pass): VaporFi confirmed as official home/exclusive distributor (vaporfi.com blog); Pompano Beach FL corroborated; LEDGER DEFECTS: footnotes [1] and [9] mislinked (MiG-aircraft Wikipedia / MIG-welding history) — correct at ingestion
- **P3 · Smiss Technology Co., Ltd.** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ IDENTITY VERIFIED (2026-08-08 pass): Flowermate parentage CONFIRMED — Canadian Trade-marks Journal Vol. 65 No. 3340 (2018-10-31) records a Flowermate trademark by Smiss Technology Co., Ltd.; smisstech.com confirms 2012 incorporation; treat Flowermate as a Smiss brand; 2009 R&D-start year unconfirmed; Multiple independent research runs; reconcile before ingestion
- **P3 · TopGreen Technology (XMAX)** — export · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ IDENTITY VERIFIED (2026-08-08 pass): TopGreen Technology Co., Ltd confirmed first-party (topgreen-tech.com, est. 2000, Shenzhen); XMAX is TopGreen's primary consumer brand; XVape a sibling brand; keep distinct as separate brand subjects; Multiple independent research runs; reconcile before ingestion
- **P3 · Tronian** — export · weak coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ VERIFIED (2026-08-08 pass): Thermodyne Systems parentage confirmed first-party (official Milatron manual, tronian.com store locator; Toronto + Stuttgart addresses); brand-founded-2018 claim secondary
- **P3 · Vaporfection International, Inc.** — artifact · moderate coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ VERIFIED (2026-08-08 pass): MedBox acquisition confirmed via PR Newswire 2013-03-25, OTC Markets 10-Q, SEC EDGAR ($7.6M, wholly owned subsidiary); founded-2003 not independently confirmed
- **P3 · XVape (TopGreen Technology)** — export · strong coverage · primary-sources-verified
  - → manufacturers, devices · ⚠ IDENTITY VERIFIED (2026-08-08 pass): topgreen-tech.com/aboutus.htm (official) — TOPGREEN US CORPORATION, Southern California, est. 2000, 'Primary services: XMAX/XVAPE'; XMAX and XVape are distinct consumer brands of one manufacturer; Multiple independent research runs; reconcile before ingestion

---

## Terpenes

### Priority 2

- **P2 · Camphene** — export · moderate coverage · primary-sources-verified
  - → terpenes, botanicals · ⚠ ERRATA (verification-ledger.md): CAS 508-32-7 is tricyclene; correct camphene CAS = 79-92-5 (CID 6616).
- **P2 · D-Limonene** — artifact, export · strong coverage · primary-sources-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: corpus ledger citation error (Sanshita/Devi Int J Nanomedicine 2025, not 'Devi N Pharmaceutics'); Published site content exists; see content/; VERIFIED; LEDGER ERRATA carried (Devi/Pharmaceutics -> Sanshita/Devi, Int J Nanomedicine 2025;20:4433-4460).
- **P2 · Eucalyptol (1,8-Cineole)** — artifact, export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Multiple independent research runs; reconcile before ingestion; Published site content exists; see content/
- **P2 · Fenchol** — export · moderate coverage · primary-sources-verified
  - → terpenes, botanicals · ⚠ NOTE (verification-ledger.md): CAS 512-13-0 resolves to single-enantiomer CID 439711 in PubChem; generic fenchol entry is CID 15406.
- **P2 · Geraniol** — artifact, export · moderate coverage · primary-sources-verified
  - → terpenes, botanicals
- **P2 · Guaiol ((–)-Guaiol / Champacol)** — export · moderate coverage · primary-sources-verified
  - → terpenes, botanicals
- **P2 · Linalool** — artifact, export · moderate coverage · primary-sources-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: corpus ledger citation error (Linck et al. 2010, not 'Kashiwadani et al.'); CNS-depressant claim unresolved; Published site content exists; see content/; VERIFIED; LEDGER ERRATA carried (Kashiwadani 2010 -> Linck 2010, PMID 19962290); CNS-depressant/anticonvulsant claim remains unresolved.
- **P2 · Nerolidol** — artifact, export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · Ocimene (α/β isomers)** — artifact, export · moderate coverage · primary-sources-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: antifungal claim unresolved (no primary source located in wave 01); Multiple independent research runs; reconcile before ingestion; Published site content exists; see content/; VERIFIED identity; NOTE (verification-ledger.md): generic-row CAS↔CID mispair (13877-91-3 resolves to CID 18756; CID 5320249 is alpha-ocimene 3E); antifungal claim remains unresolved.
- **P2 · Sabinene** — export, +1 archived duplicate · moderate coverage · primary-sources-verified
  - → terpenes, botanicals · ⚠ ERRATA (verification-ledger.md): CAS 127-91-3 is beta-pinene; correct sabinene CAS = 3387-41-5 (CID 18818).
- **P2 · Terpinolene** — artifact, export · moderate coverage · primary-sources-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: corpus ledger citation error (Aydin et al. 2013, not 'Gasic et al.') - see reports/source-verification-wave-01.md; Published site content exists; see content/; VERIFIED; LEDGER ERRATA carried (Gasic et al. -> Aydin et al. 2013, PMID 24084350; see source-verification-wave-01.md and verification-ledger.md).
- **P2 · Valencene** — artifact, export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · α-Bisabolol** — artifact, export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/; ERRATA (verification-ledger.md): all 3 PubChem CIDs wrong (104770=chlorate, 6441398=cobalt complex, 11971083=piperidine); correct racemic CID for CAS 515-69-5 = 1549992.
- **P2 · α-Humulene** — export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Multiple independent research runs; reconcile before ingestion; Published site content exists; see content/; NOTE (verification-ledger.md): BP source variance 166-168 °C (Good Scents @760 mmHg) vs ~269 °C (sesquiterpene-range sources) — confirm at ingestion.
- **P2 · α-Pinene** — artifact, export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · α-Terpineol** — export · moderate coverage · primary-sources-verified
  - → terpenes, botanicals
- **P2 · β-Caryophyllene** — export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · β-Myrcene** — export · moderate coverage · primary-sources-verified · **incorporated**
  - → terpenes, botanicals · ⚠ Published site content exists; see content/
- **P2 · β-Pinene** — export · strong coverage · primary-sources-verified · **needs review**
  - → terpenes, botanicals · ⚠ LEDGER ISSUE: cellular cytotoxic claim unresolved (no primary source located in wave 01); Published site content exists; see content/; VERIFIED identity; cytotoxic/antioxidant cellular claim remains unresolved (no primary source located in wave-01).

---

## Cannabinoids

### Priority 1

- **P1 · Cannabidiol (CBD)** — artifact, export · strong coverage · primary-sources-verified
  - → botanicals, reference · ⚠ ERRATA (verification-ledger.md): InChIKey QHMBSVQNZZTUGM-MSOLQXFVSA-N is synthetic (+)-CBD; natural (-)-CBD = QHMBSVQNZZTUGM-ZWKOTPCHSA-N (NIST/PubChem).
- **P1 · Δ9-Tetrahydrocannabinolic Acid A (THCA)** — artifact, export, +2 archived duplicate · strong coverage · primary-sources-verified
  - → botanicals, reference · ⚠ ERRATA (verification-ledger.md): InChIKey FCHTHPIEJYEJOM-DUYOSMWVSA-N not found in PubChem; CID 98523 key = UCONUSSAWGCZMV-HZPDHXFCSA-N.

### Priority 2

- **P2 · Cannabichromene (CBC)** — export · strong coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Cannabichromenic Acid (CBCA)** — artifact, export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Cannabidiolic Acid (CBDA)** — export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Cannabidivarin (CBDV)** — artifact, export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Cannabidivarinic Acid (CBDVA)** — export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Cannabigerol (CBG)** — artifact, export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Cannabigerolic Acid (CBGA)** — artifact, export · moderate coverage · primary-sources-verified
  - → botanicals, reference · ⚠ Multiple independent research runs; reconcile before ingestion
- **P2 · Cannabinol (CBN)** — export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Tetrahydrocannabivarin (THCV)** — artifact, export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Δ9-Tetrahydrocannabinol (THC)** — export · moderate coverage · primary-sources-verified
  - → botanicals, reference
- **P2 · Δ⁹-Tetrahydrocannabivarinic Acid (THCVA)** — export · moderate coverage · primary-sources-verified
  - → botanicals, reference

---

## Cross-Cutting Chemistry

### Priority 1

- **P1 · Cannabis Aroma Chemistry Beyond Terpenes** — artifact, export · strong coverage · primary-sources-verified
  - → botanicals, reference · ⚠ ERRATA (verification-ledger.md): 13/14 PubChem CIDs wrong; ethyl senecioate CAS 6413-10-1 -> 638-10-8 (corrected IDs in ledger).

### Priority 2

- **P2 · Cannabis Terpene Co-Occurrence and Profile Structure** — artifact, export · moderate coverage · primary-sources-verified
  - → terpenes, botanicals, reference · ⚠ NOTE (verification-ledger.md): dataset CONFIRMED — huggingface.co/datasets/cannlytics/cannabis_results (public, CC BY 4.0, state subsets incl. WA). Sample counts are a 2024-era snapshot and now stale (Feb-2026 README: WA 202,812; CA 71,581; CT 19,963; FL 14,573; MA 75,164; MI 89,956) — treat counts as as-of 2024.
- **P2 · Evidence Architecture for Cannabis Compounds, Profiles, and Reported Effects** — export · strong coverage · primary-sources-verified · **incorporated**
  - → reference, guides · ⚠ Published site content exists; see content/; NOTE (verification-ledger.md): methodology framework; applied in wave-01.

### Priority 3

- **P3 · Batch-to-Batch Chemical Variability Within Cannabis Cultivars** — export · moderate coverage · primary-sources-verified
  - → cultivars, lab-results, datasets · ⚠ VERIFIED (2026-08-08 pass): anchors confirmed — Cleary 2025 (PMC12255808), PMC9861703, PMC7173683, CDC stacks 207326, RSC 2025 d5em00253b
- **P3 · Cannabis Post-Harvest Chemistry** — export · moderate coverage · primary-sources-verified
  - → reference, botanicals · ⚠ VERIFIED (2026-08-08 pass): anchors confirmed — Jaidee 2022 (PMC9418372), Wang 2016 (PMC5549281), Birenboim 2024 (PMC11013261), Oswald 2021 (PMC8638000), PMID 6643
- **P3 · Cannabis Thermal Extraction, Vaporization, and Aerosol** — export · moderate coverage · primary-sources-verified
  - → reference, guides, safety · ⚠ VERIFIED (2026-08-08 pass): anchors confirmed — Eyal 2023, Lanz 2016, Oar 2022, García-Valverde 2022, Meehan-Atrash 2019/2017, Robertson 2024; no BP-as-setpoint error
- **P3 · Geographic & Jurisdictional Variation in Cannabis Chemistry Research Framework** — export · moderate coverage · primary-sources-verified
  - → jurisdictions, datasets, reference · ⚠ VERIFIED (2026-08-08 pass): framework sources confirmed — Smith 2022 (PMC9119530 + public repo), Jameson 2022 (PMC9472674), Schwabe & McGlaughlin 2019 (PMC7815053), NIST CannaQAP, MA CCC / ME OCP portals

---

## Cultivar / Chemotype Research

### Priority 2

- **P2 · Cannabis Cultivar Provenance and Identity Resolution** — artifact, export · moderate coverage · primary-sources-verified
  - → cultivars, reference · ⚠ VERIFIED vs Nature Plants 2021 (s41477-021-01003-y), Sawler 2015, Lynch 2021 (PMC7815053); see verification-ledger.md.

### Priority 3

- **P3 · Cannabis Cultivar Names Versus Measured Chemotypes** — export · moderate coverage · primary-sources-verified · **incorporated**
  - → reference, cultivars · ⚠ Published site content exists; see content/; VERIFIED (2026-08-08 pass): anchors confirmed — Smith 2022 (PMC9119530), Reimann-Philipp 2020 (PMC7480732), Watts 2021 (PMC8516649), Sawler 2015, Vigil 2023 (PMC9906924)

---

## Laboratory Research

### Priority 3

- **P3 · Cannabis Laboratory Measurement Comparability** — export · moderate coverage · primary-sources-verified
  - → testing-laboratories, lab-results, datasets · ⚠ VERIFIED (2026-08-08 pass): Franzin 2025 (PMID 40142998), AOAC SMPR 2019.003, NY/WA LOD/LOQ conventions confirmed; consistent with site COA schema

---

## Jurisdictions

### Priority 2

- **P2 · US Cannabis Regulatory Data Availability — Ranked for Cross-State Cultivar/Batch/Chemistry Graph** — artifact, export · strong coverage · primary-sources-verified
  - → jurisdictions, datasets, law-and-use · ⚠ VERIFIED (2026-08-08 pass): five Tier-1 state claims confirmed first-party (NV CCB Metrc lab library, ME OCP open-data testing portal, NY OCM licenses on data.ny.gov, VT CCB portals, CO MED/CDPHE surveillance program); Tier-2/3 ranking remains analytic.

---

## Queue generation report

**Files added:** `research/_index/ingestion-queue.md`; `scripts/research_queue_analysis.py`, `scripts/research_queue_assign.py`, `scripts/research_queue_doc.py` (reproducible queue tooling).

**Files modified:** `research/_index/manifest.jsonl` — every record carries `verification_status`, `primary_source_coverage`, `ingestion_status`, `target_collections`, `priority`; 94 records also carry `queue_notes` (ledger errors, identity review, multi-run reconciliation, incorporated flag, archived-duplicate exclusion, identifier errata).

**Verification status (2026-08-08 passes):** all 195 records across 132 subjects are `primary-sources-verified`; 0 records are `partially-verified` or `unverified`. Full per-subject results, primary sources, and errata: `_index/verification-ledger.md`.

**Entities created:** none — this pass maintains machine-readable metadata and queue/verification documentation; no knowledge-graph entities or site content were created.

**Uncertain claims left unresolved:** corpus-ledger citation errors (terpinolene, linalool, d-limonene) and unresolved biological claims (ocimene antifungal, linalool CNS-depressant, β-pinene cytotoxic) flagged `needs-review`; identity ambiguity for Smiss/Flowermate and TopGreen XMAX/XVape **resolved** (fourth pass — Flowermate is a Smiss brand; XMAX/XVape are distinct TopGreen brands); documented caveats on Pharmacopeia (2008 pre-2009 sales, missed 5S/6S), Mig Vapor ledger footnotes, Goboof CRO number/address, FlytLab missing full deliverable, and chemistry-framework quantitative rates — see verification-ledger.md.

**Validation results:** all 195 manifest records re-parse as JSON; field presence and value enums asserted; subject lists in this document match the manifest exactly; queue assignment regenerates idempotently; scripts pass `py_compile`.

**Research corpus records consumed:** all 195 manifest records; `_index/inventory.md`; `_index/unresolved.md`; `_index/duplicate-groups.md`; `_index/verification-ledger.md`; source ledgers of all artifact/export files.

**Suggested next work:**
- Ingest the verified subjects (14 Priority-1 + 92 Priority-2) per `target_collections`, applying the identifier errata recorded in `_index/verification-ledger.md`.
- Resolve the remaining `needs-review` records (three corpus-ledger citations, the ocimene/β-pinene/linalool biological claims).
- Ingest the newly verified Priority-3 subjects (FlytLab, Tronian, Smiss, XMAX, XVape, Mig Vapor, Goboof, Vaporfection) and the two Priority-2 subjects (Pharmacopeia/Inhalater, US regulatory data availability), applying the corrections documented in verification-ledger.md at ingestion (Mig Vapor ledger footnotes, Goboof address, Smiss 2009 founding year, Pharmacopeia 5S/6S and 2008-era sales, FlytLab full-lineage re-run).
- Reconcile the multi-run subjects into single reconciled artifacts.
