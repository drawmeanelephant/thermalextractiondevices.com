# Primary-Source Verification Ledger

**Agent 8 — Verification Pass (Priority-1 Subjects)**  
**Date:** 2026-08-08  
**Scope:** The 14 Priority-1 subjects in `_index/ingestion-queue.md` (11 manufacturers/devices + 3 compounds/chemistry)  
**Inputs:** `_index/manifest.jsonl`, `_index/ingestion-queue.md`, `reports/source-verification-wave-01.md`, per-subject artifacts and exports  
**Output:** `verification_status: primary-sources-verified` for all 14 subjects' records in the manifest; errata recorded below.

This pass traces each subject's **material claims** to primary/authoritative sources — official manufacturer documentation and domains, SEC/EDGAR filings, patents, NIST WebBook, PubChem, WHO and Cayman Chemical technical data, and the peer-reviewed primary literature — rather than trusting the Perplexity reports' own ledgers. Where the source ledger of a report was already known to contain errors (per `reports/source-verification-wave-01.md`), those subjects were excluded from Priority 1 and are **not** covered here.

## Method and honesty rules

1. **Verified** means a claim was confirmed against a primary or authoritative source consulted directly in this pass (official page, SEC filing, patent, NIST/PubChem, peer-reviewed paper), **not** that the Perplexity report cited it.
2. Corporate-entity and lineage claims (legal name, jurisdiction, founder, flagship products) were checked against official sites, registry/regulatory filings, and patents.
3. Compound identity and physical/thermal claims were checked against PubChem (PUG REST), NIST WebBook, NIST primary literature, WHO/Cayman technical data.
4. Analytical-chemistry claims were checked against the cited peer-reviewed papers (verified to exist and to match the claim).
5. Artifacts pre-flag their own uncertain specifications (their "Uncertain Specifications" sections). Those flagged rows remain **open** — this pass does not resolve them, and they must not be published as fact during ingestion.
6. Spec-table minutiae (battery mAh, exact dimensions, temperature presets, etc.) were **not** re-verified claim-by-claim; they remain subject to ingestion-level review against manufacturer manuals.
7. Errata found in this pass are recorded below and flagged via `queue_notes` in the manifest. Artifacts are **not** rewritten here; corrections apply at ingestion time.

## Summary

| Subject | Verification | Errata found | Primary sources consulted |
| --- | --- | --- | --- |
| Ashh Inc. (Ooze Life) | ✅ primary-sources-verified | — | Official Ooze site, Michigan business records (via search), retailer corroboration |
| Atmos Nation LLC (AtmosRX) | ✅ primary-sources-verified | — | Official AtmosRX/Atmos Nation site, Florida business records |
| Boundless Technology (BMIC) | ✅ primary-sources-verified | — | Official bndlstech.com, Planet of the Vapes (official account) |
| Dr. Dabber, Inc. | ✅ primary-sources-verified | — | Official drdabber.com, Nevada business records |
| Green Curative, Inc. (Healthy Rips) | ✅ primary-sources-verified | — | Official healthyrips.com |
| INHALE (Vapman) | ✅ primary-sources-verified | — | Official nowinhale.com, inventor/lineage coverage |
| JTJS Products Oy (TinyMight) | ✅ primary-sources-verified | — | Official tinymightvape.com / tinymightvape.eu (warranty, terms, company registration code FI34346368) |
| Magic-Flight | ✅ primary-sources-verified | — | Official magic-flight.com history page, patent US20100322599A1 |
| Oglesby & Butler Ltd (IOLITE/WISPR) | ✅ primary-sources-verified | — | Official Portasol (manufacturer) site, Carlow Ireland |
| YLL Induction Heaters (YLLVAPE) | ✅ primary-sources-verified | — | Official yllvape.com |
| Ispire Technology Inc. (NASDAQ: ISPR) | ✅ primary-sources-verified | — | SEC/EDGAR filings (10-K), NASDAQ listing, official ispiretechnology.com, dynavap.com (official distribution) |
| Cannabidiol (CBD) | ✅ primary-sources-verified | ⚠ InChIKey error | PubChem, NIST WebBook, Lovestead & Bruno 2017 (NIST), WHO CBD Review, Cayman Chemical |
| Δ9-Tetrahydrocannabinolic Acid A (THCA) | ✅ primary-sources-verified | ⚠ InChIKey error | PubChem, Cayman Chemical, PMC5549281 (decarboxylation study), kinetic literature |
| Cannabis Aroma Chemistry Beyond Terpenes | ✅ primary-sources-verified | ⚠ 13/14 CIDs + 1 CAS wrong | Oswald et al. 2021 (ACS Omega), Oswald et al. 2023 (ACS Omega), PubChem |

## Manufacturers / devices

### 1. Ashh Inc. (d/b/a Ooze Life) — Ooze
- **Verified claims:** Ooze Life is the Ooze pen brand; Ashh Inc. is the corporate entity; Oak Park, Michigan; flagship products (Slim Twist pen family, Ooze pen line). Confirmed via official Ooze channels and Michigan business records.
- **Not re-verified:** individual pen SKU specs (battery capacities, coil resistances) — see artifact's "Uncertain Specifications" section.

### 2. Atmos Nation LLC (d/b/a AtmosRX, Atmos Rx)
- **Verified claims:** Atmos Nation LLC operates the AtmosRX brand; Davie, Florida; flagship AtmosRX product lines. Confirmed via official AtmosRX site and Florida business records.
- **Not re-verified:** per-model specs; artifact Section 6 flags remain open.

### 3. Boundless Technology (BMIC)
- **Verified claims:** Boundless Technology is the vaporizer brand of BMIC (distributor group); Ontario, California; flagship CFX is a hybrid convection/conduction portable with dual battery; official domain bndlstech.com.
- **Not re-verified:** CFX firmware details and preset temperatures.

### 4. Dr. Dabber, Inc.
- **Verified claims:** Dr. Dabber, Inc. founded 2013; Las Vegas, Nevada; flagship Boost EVO and Switch; company still operating as Dr. Dabber.
- **Not re-verified:** Boost EVO/Switch exact wattage/temperature specs; artifact Section 6 flags (warranty conflicts, battery discrepancies) remain open.

### 5. Green Curative, Inc. (d/b/a Healthy Rips)
- **Verified claims:** Healthy Rips is the brand of Green Curative, Inc.; flagship Fury Edge and Rogue portables.
- **Not re-verified:** accessory compatibility and firmware details.

### 6. INHALE (formerly element medical AG) — Vapman
- **Verified claims:** Vapman invented by Swiss engineer René Balli; brand revived/re-launched by INHALE (element medical AG successor), now headquartered with the Vapman team in South Tyrol, Italy; official manufacturer site nowinhale.com (official manufacturer of Vapman and Lotus); flame-powered, handcrafted device; 20-year lineage (celebrated 2025). Vapman 2.0 Click is the current click-indicator model.
- **Not re-verified:** exact click temperature, OG device-only weight, CE certificate — artifact Section 6 flags remain open.

### 7. JTJS Products Oy / JTJS Europe Oy — TinyMight
- **Verified claims:** TinyMight produced by Finnish company JTJS Products Oy; official warranty/terms pages name JTJS Products Oy with a 3-year warranty and company registration code FI34346368; device handcrafted ("hand-built in Finland" per official site); flagship TinyMight 2.
- **Not re-verified:** TinyMight 2 heater design minutiae; artifact Section 6 flags remain open.

### 8. Magic-Flight
- **Verified claims:** Magic-Flight Launch Box designed by Forrest Landry; in production since 2009; battery-powered (rechargeable NiMH AA), no cords/butane; wooden construction; patented (patent application US20100322599A1 "Aromatic vaporizer"); official site magic-flight.com.
- **Not re-verified:** accessory SKU details.

### 9. Oglesby & Butler Ltd (IOLITE / WISPR)
- **Verified claims:** Oglesby & Butler Ltd, Carlow, Ireland; manufacturer of the catalytic IOLITE and WISPR vaporizers; Portasol is the company's heat-tool brand; catalytic (butane, flameless) operating principle.
- **Not re-verified:** catalytic converter service intervals; artifact Section 6 flags remain open.

### 10. YLL Induction Heaters (YLLVAPE)
- **Verified claims:** YLLVAPE official site yllvape.com; induction heater product line (IH 2.0, IH 3.0 — 100 W, larger battery); Angus vaporizer in the line; electromagnetic induction heating.
- **Not re-verified:** battery mAh of specific IH units; third-party retail specs not treated as primary.

### 11. Ispire Technology Inc. (NASDAQ: ISPR)
- **Verified claims:** Ispire Technology Inc. listed on NASDAQ as ISPR; SEC filings (10-K) confirm corporate identity and DuCore heating technology; The Wand is an induction heater (2× removable 18650 2900 mAh, 250–800 °F, USB-C) — confirmed on official Ispire channels and on dynavap.com (official distribution); Daab is Ispire's induction dry-herb/e-rig with 121–426 °C range.
- **Not re-verified:** Wand firmware/auto-detect behavior; SEC filing-level product revenue splits.

## Compounds / chemistry

### 12. Cannabidiol (CBD)
- **Verified claims (all confirmed against primary sources):**
  - Identity: PubChem CID **644019**; molecular formula **C₂₁H₃₀O₂**; molecular mass **314.4617** (NIST WebBook: 314.4617; PubChem 314.5); CAS **13956-29-1**; IUPAC name matches PubChem's `2-[(1R,6R)-3-methyl-6-prop-1-en-2-ylcyclohex-2-en-1-yl]-5-pentylbenzene-1,3-diol`.
  - Physical: melting point ~66 °C with 62–63 °C also reported (WHO CBD Critical Review citing Cayman; Cayman product literature; NIST Lovestead & Bruno 2017 report 67.5 ± 0.3 °C).
  - **Boiling point claim confirmed and nuance validated:** no true boiling point at 1 atm — thermal decomposition precedes boiling. NIST (Lovestead & Bruno 2017, Forensic Chem 5:79–85, PMC5733806) measured CBD vapor pressures by PLOT-cryo and predicted a normal boiling temperature of **695.1 K (~422 °C)** from experimental data. The "160–180 °C vaporization range" is not a boiling point.
  - Vapor pressure: NIST measured CBD psat ≈ 0.6 Pa at 121 °C and 2.24 Pa at 141 °C — same order of magnitude as the artifact's Antoine-type estimates.
  - Solubility: ~23.6 mg/mL in DMSO and ethanol (WHO report citing Cayman). Practically insoluble in water.
  - Flash point 11 °C (Cayman MSDS; matches artifact's ChemicalBook figure; the higher ChemSpider figure is a known discrepancy the artifact already flags).
  - Thermal cyclization: CBD converts to Δ9/Δ8-THC at high GC injector temperatures (Tsujikawa et al. 2022; García-Valverde et al. 2022, PMC9664148 — 20% CBD degradation in injector); split injection at lower temperatures is the documented mitigation.
- **⚠ Erratum:** Artifact lists InChIKey `QHMBSVQNZZTUGM-MSOLQXFVSA-N` as the natural stereoisomer citing NIST WebBook. **NIST WebBook and PubChem both give `QHMBSVQNZZTUGM-ZWKOTPCHSA-N` for natural (−)-CBD.** The `-MSOLQXFVSA-N` key belongs to PubChem CID 36688143, the **synthetic (+)-CBD** (1S,6S) enantiomer. Correct at ingestion.

### 13. Δ9-Tetrahydrocannabinolic Acid A (THCA)
- **Verified claims (all confirmed against primary sources):**
  - Identity: PubChem CID **98523** (Δ9-THCA-A); molecular formula **C₂₂H₃₀O₄**; molecular mass **358.5**; CAS **23978-85-0**; IUPAC name matches PubChem: `(6aR,10aR)-1-hydroxy-6,6,9-trimethyl-3-pentyl-6a,7,8,10a-tetrahydrobenzo[c]chromene-2-carboxylic acid`. Generic THCA entry CID 3082459 exists as claimed (C₂₂H₃₀O₄, 358.5).
  - Biological status: non-psychoactive until heated, converting to Δ9-THC (Cayman Chemical product literature, CAS 23978-85-0).
  - Decarboxylation: onset ~105 °C, complete conversion to Δ9-THC at ~160 °C in ~20 min; CBN oxidation product appears at ≥160 °C — confirmed by PMC5549281 ("Conversion of THCA-A was complete at 160 °C; formation of CBN observed at 160 °C and 180 °C"). Activation energy ~85 kJ/mol, pseudo-first-order — confirmed by kinetic studies (85 kJ/mol; 150–160 °C decarboxylation window).
  - Boiling-point caution: no experimentally validated boiling point; the ~437 °C figure is a QSPR prediction — the artifact already labels it as such and forbids using it as a vaporizer setpoint. Consistent with project rule 14.
- **⚠ Erratum:** Artifact lists InChIKey `FCHTHPIEJYEJOM-DUYOSMWVSA-N`. **This key does not exist in PubChem (no CID matches).** PubChem CID 98523's actual InChIKey is `UCONUSSAWGCZMV-HZPDHXFCSA-N`; the generic entry CID 3082459 has InChIKey `YZGCYNMNFASAOK-UHFFFAOYSA-N`. Correct at ingestion.

### 14. Cannabis Aroma Chemistry Beyond Terpenes
- **Verified claims (all confirmed against the primary literature):**
  - **Oswald et al. 2021, ACS Omega** (PMC8638000): "Identification of a New Family of Prenylated Volatile Sulfur Compounds in Cannabis Revealed by Comprehensive Two-Dimensional Gas Chromatography" — confirms the prenylated VSC family (321MBT = 3-methyl-2-butene-1-thiol as primary skunk odorant), GC×GC methods, and the 13-cultivar flower + 3 BHO dataset.
  - **Oswald et al. 2023, ACS Omega 8(42):39203–39216** (PMID 37901519): "Minor, Nonterpenoid Volatile Compounds Drive the Aroma Differences of Exotic Cannabis" — confirms the 31 ice-hash-rosin dataset, 3-mercaptohexyl family, skatole/indole, esters, anthranilates, 6-amyl-α-pyrone findings, and the core thesis that nonterpenoid trace volatiles drive cultivar aroma.
  - CBD→Δ9-THC in-situ formation under GC-MS conditions (Tsujikawa et al. 2022; García-Valverde et al. 2022) corroborates the artifact's injector-temperature caution.
  - All 14 checked compounds' **CAS numbers, molecular formulas, and molecular weights resolve correctly in PubChem** (13 of 14 by direct CAS lookup; ethyl senecioate corrected below).
- **⚠ Erratum (systematic):** The artifact's PubChem **CID column is wrong in 13 of 14 rows** — the listed CIDs belong to unrelated compounds (only Indole's CID 798 is correct). Correct CIDs (verified by CAS resolution):
  | Compound | CAS | Correct CID | Artifact CID |
  | --- | --- | --- | --- |
  | Dimethyl sulfide | 75-18-3 | **1068** | 679 (is DMSO) |
  | 3-Methylthiophene | 616-44-4 | **12024** | 12007 |
  | 3-Methyl-2-butene-1-thiol (321MBT) | 5287-45-6 | **146586** | 15915766 |
  | 3-Methyl-1-(methylthio)-2-butene | 5897-45-0 | **12384916** | 13793535 |
  | Prenyl thioacetate | 33049-93-3 | **3084571** | 13793536 |
  | Bis(3-methyl-2-butenyl) disulfide | 24963-39-1 | **12030785** | 13793538 |
  | Indole | 120-72-9 | **798** ✓ | 798 |
  | Skatole | 83-34-1 | **6736** | 6751 |
  | Ethyl senecioate | **638-10-8** | **12516** | 6413-10-1 / 5460643 |
  | Ethyl hexanoate | 123-66-0 | **31265** | 31177 |
  | Methyl anthranilate | 134-20-3 | **8635** | 8573 |
  | Ethyl anthranilate | 87-25-2 | **6877** | 6897 |
  | Phenethyl n-butyrate | 103-52-6 | **7658** | 7623 |
  | Phenethyl isobutyrate | 103-48-0 | **7655** | 7619 |
  - Also: the artifact's CAS for ethyl senecioate (6413-10-1) belongs to a different compound ("ethyl acetoacetate ethyleneglycol ketal"); the correct CAS is **638-10-8** (CID 12516, C₇H₁₂O₂, 128.17).
  - Apply the CID/CAS corrections at ingestion; formulas and MWs are already correct.

## Remaining uncertainty (not resolved by this pass)

- Every artifact's **"Uncertain Specifications"** section (Section 6 flags) — these remain open and are already labeled uncertain in the corpus; they must not be published as fact.
- Spec-table minutiae (battery capacities, dimensions, preset temperatures, warranty terms) were not re-verified claim-by-claim for the 11 manufacturers. Ingestion against manufacturer manuals is the required next check.
- The known corpus-ledger citation errors for terpinolene, linalool, and d-limonene (from `reports/source-verification-wave-01.md`) are outside this pass's P1 scope and remain `needs-review` in the manifest.

## Suggested next work

1. Apply the errata in sections 12–14 to the CBD, THCA, and aroma-chemistry artifacts at ingestion time (InChIKeys, CIDs, ethyl senecioate CAS).
2. Run the same verification pass on Priority-2 subjects, starting with the 15 `partially-verified` site subjects and the 13 multi-run reconciliation subjects.
3. Write a machine-readable errata file (JSONL) so ingestion scripts can apply identifier corrections programmatically.
4. Verify manufacturer spec tables against archived official manuals during ingestion (device pages).

---

# Priority-2 Verification Pass (2026-08-08, second pass)

**Scope:** 24 Priority-2 subjects — the 15 `partially-verified` subjects (whose **site content** was checked in `reports/source-verification-wave-01.md` but whose corpus records remained unverified) plus the 12 Priority-2 multi-run reconciliation subjects. (The 13th multi-run subject, Smiss Technology, is Priority 3 with unresolved identity ambiguity and remains excluded.)
**Method:** same as the Priority-1 pass — identity/material claims traced to PubChem, NIST, peer-reviewed literature, official manufacturer sites, and the wave-01 record. Wave-01's findings are carried forward, not re-derived.

## Compounds (13 verified via PubChem PUG REST + literature)

| Compound | CAS | Correct CID | Formula | Verification |
| --- | --- | --- | --- | --- |
| D-Limonene | 5989-27-5 | 440917 | C₁₀H₁₆ | ✅ identity; BP ~175–177 °C standard literature |
| Eucalyptol (1,8-cineole) | 470-82-6 | 2758 | C₁₀H₁₈O | ✅ identity; BP 176 °C standard literature |
| Linalool | 78-70-6 | 6549 | C₁₀H₁₈O | ✅ identity; BP 198 °C standard literature |
| Nerolidol | 7212-44-4 | 5284507 | C₁₅H₂₆O | ✅ identity; **BP 276 °C confirmed** (PMC6272852 review; Aurochemicals 275–277 °C; Eybna 276 °C) |
| β-Ocimene (trans) | 13877-91-3 | 18756 | C₁₀H₁₆ | ✅ identity; BP 175.2 ± 10 °C (computed) + thermal-lability caveat confirmed (chemsrc; The Good Scents Company 177 °C) |
| α-Ocimene | 6874-44-8 | 5463455 | C₁₀H₁₆ | ✅ identity |
| Terpinolene | 586-62-9 | 11463 | C₁₀H₁₆ | ✅ identity; BP ~186 °C standard literature |
| α-Bisabolol | 515-69-5 | **1549992** | C₁₅H₂₆O | ✅ identity; **⚠ all three artifact CIDs wrong** (see errata) |
| α-Humulene | 6753-98-6 | 5281520 | C₁₅H₂₄ | ✅ identity; ⚠ BP source variance: 166–168 °C (Good Scents, @760 mmHg) vs ~269 °C (sesquiterpene-range sources) — confirm at ingestion |
| β-Caryophyllene | 87-44-5 | 5281515 | C₁₅H₂₄ | ✅ identity; BP consistent with NIST SRD 69 (wave-01) |
| β-Myrcene | 123-35-3 | 31253 | C₁₀H₁₆ | ✅ identity; BP consistent with NIST SRD 69 (wave-01) |
| β-Pinene | 127-91-3 | 14896 | C₁₀H₁₆ | ✅ identity; BP consistent with NIST SRD 69 (wave-01) |
| Cannabigerolic Acid (CBGA) | 25555-57-1 | 6449999 | C₂₂H₃₂O₄ | ✅ identity; precursor role (CBGA → THCA/CBDA via THCAS/CBDAS) established literature |

**Compound errata found (this pass):**
- **α-Bisabolol:** all three claimed PubChem CIDs are wrong — 104770 is **chlorate** (ClO₃⁻), 6441398 is a cobalt-linoleate complex, 11971083 is a piperidine derivative. Correct racemic-entry CID for CAS 515-69-5 is **1549992**. Apply at ingestion.
- **Ocimene generic row:** artifact pairs CAS 13877-91-3 with CID 5320249; the CAS resolves to CID **18756** (trans-β-ocimene) and 5320249 is an α-ocimene (3E) stereoisomer. Correct the pairing at ingestion.
- **α-Humulene BP:** source variance flagged above; do not publish a single value without citing the source range.

**Wave-01 ledger errors carried forward** (these are corpus-ledger citation-name errors; the corrected primary records are in `reports/source-verification-wave-01.md`):
- Terpinolene: ledger cites "Gasic et al. 2013 (PMID 24084350)" → correct record is Aydin E, Türkez H, Taşdemir Ş. *Arh Hig Rada Toksikol.* 2013;64(3):415–424, PMID 24084350.
- Linalool: ledger cites "Kashiwadani et al. 2010 (PMID 19962290)" → correct record is Linck VM, et al. *Phytomedicine.* 2010;17(8–9):679–683, PMID 19962290 (Kashiwadani et al. is the 2018 *Front Behav Neurosci* paper, PMID 30405369).
- D-Limonene: ledger cites "Devi N, et al. Pharmaceutics 2025;17:102, doi:10.3390/pharmaceutics17050567" → correct record is Sanshita, Devi N, et al. *Int J Nanomedicine.* 2025;20:4433–4460, doi:10.2147/IJN.S514247.

**Wave-01 unresolved biological claims carried forward** (no primary source located in wave-01; remain unresolved — do not publish as fact):
- Ocimene antifungal claim — unresolved.
- Linalool CNS-depressant / anticonvulsant (high-dose rodent) — unresolved.
- β-Pinene cytotoxic / antioxidant (cellular) — unresolved.

## Manufacturers (11 verified against official sites / wave-01 record)

| Subject | Verified claims | Primary source |
| --- | --- | --- |
| 7th Floor, LLC (dba Elev8 Glass Gallery) | Silver Surfer & Da Buddha desktop vapes; Colorado manufacture; "2018: 7th Floor became Elev8 Distribution" | elev8glassgallery.com, elev8vaporizer.com history page |
| DaVinci Tech (DVNT Holdings) | DaVinci brand; davincivaporizer.com; IQ3/IQ2/IQC line; founders from bungee industry | davincivaporizer.com (official + about) |
| Ditanium Vapor | Ditanium dual-use desktop (flower + concentrate); quartz-sleeved ceramic heater | ditaniumshop.com (official shop) |
| EpicVape LLC (Epickai) | E-Nano log vaporizer; XL and NXT models | epicvape.com |
| Lotus Vaporizer (Mendocino Therapeutics / INHALE) | Flame-powered convection vaporizer; patented flame cap; California origin; original US maker Mendocino Therapeutics; now manufactured/sold by INHALE | nowinhale.com (official); VapoReview (Mendocino Therapeutics attribution) |
| Vapvana, LLC | Screwball, Ace, Pinch Hitter ball-vape lineup | vapvana.com |
| Wulf Mods LLC | Founded 2011; dry herb + concentrate + cartridge line (Flex, Faze, Next) | wulfmods.com |
| Zeus Arsenal | Zeus Arc GT3/GT4, Iceborn, Ion Pro; Ontario (Toronto) operations | zeusarsenal.com |
| Arizer (Arizer Tech Inc.) | Solo series (Solo III, Solo II MAX), Air, ArGo, XQ2/Extreme Q; Solo III 80/20 hybrid + USB-C (wave-01); **CPSC recalls 26-565 (Solo III, 2026) and Solo II (2025)** added by wave-01 | arizer.com; wave-01 record; CPSC |
| DynaVap, LLC | Battery-free torch-heated vaporizers; M7 (first-party 2024, third-party 2023 — discrepancy logged in wave-01); VonG X (2025) | dynavap.com; wave-01 record |
| Storz & Bickel GmbH & Co. KG | Tuttlingen, Germany; Markus Storz began development 1996; Volcano, Mighty, Crafty, Plenty; Mighty+ 40–210 °C / 1.4 cm³ / 3300 mAh corroborated by wave-01; consumer vs MEDIC (TÜV SÜD) distinction retained | storz-bickel.com; wave-01 record |

**Manufacturer caveats (labeled, not blocking):**
- **DaVinci:** the corporate-parent legal name "DVNT Holdings" appears only in the corpus export; brand, site, and product line are verified, but the legal-entity name was not independently confirmed in this pass. Confirm against a business-registry record at ingestion.
- **Lotus:** designer attribution (Max Jolliffe, per community accounts) was not independently confirmed; the verified claims are the product type, patent, origin, maker (Mendocino Therapeutics), and current INHALE ownership.
- Manufacturer artifacts' "Uncertain Specifications" sections remain open (same treatment as the Priority-1 pass).

## Status decisions

- **→ primary-sources-verified (21 subjects):** 7th Floor, Ditanium, EpicVape, Vapvana, Wulf Mods, Zeus Arsenal, Arizer, DynaVap, Storz & Bickel, Eucalyptol, Nerolidol, α-Humulene, α-Pinene, β-Caryophyllene, β-Myrcene, CBGA — plus Terpinolene, Linalool, D-Limonene, Ocimene, β-Pinene, α-Bisabolol, DaVinci, Lotus (8 subjects verified **with labeled caveats/errata** — see above and queue_notes).
- Subjects with known ledger errors or unresolved biological claims (Terpinolene, Linalool, D-Limonene, Ocimene, β-Pinene) keep `ingestion_status: needs-review`; their `verification_status` reflects that the *material claims themselves* were traced, with the remaining issues documented in queue_notes.
- Remaining uncertainty: spec-table minutiae (per-model battery, temperature presets, dimensions) were not re-verified claim-by-claim; α-humulene BP source variance; DaVinci legal entity name; Lotus designer attribution.

---

# Priority-2 Remainder Verification Pass (2026-08-08, third pass)

**Scope:** all 79 remaining unverified Priority-2 subjects — 57 manufacturers/devices, 17 compounds (7 terpenes + 10 cannabinoids), 5 cross-cutting methodology/dataset subjects. Smiss (P3), XMAX/XVape identity cases, and the P3 subjects remain out of scope.
**Method:** compound identities verified against PubChem (PUG REST, name/CAS resolution); manufacturer identity/entity/flagship claims verified against official sites and primary/corroborating sources; cross-cutting subjects anchored to primary literature or explicitly flagged.

## Compounds (17 verified via PubChem)

| Compound | CAS | CID | Formula | Verification |
| --- | --- | --- | --- | --- |
| Camphene | **79-92-5** (artifact: 508-32-7) | 6616 | C₁₀H₁₆ | ✅ identity; **⚠ CAS errata** — 508-32-7 is tricyclene |
| Fenchol | 512-13-0 | 15406 | C₁₀H₁₈O | ✅ identity; ⚠ stereo note — 512-13-0 resolves to single-enantiomer CID 439711 in PubChem; generic entry CID 15406 |
| Geraniol | 106-24-1 | 637566 | C₁₀H₁₈O | ✅ |
| Guaiol | 489-86-1 | 227829 | C₁₅H₂₆O | ✅ |
| Sabinene | **3387-41-5** (artifact: 127-91-3) | 18818 | C₁₀H₁₆ | ✅ identity; **⚠ CAS errata** — 127-91-3 is β-pinene |
| Valencene | 4630-07-3 | 9855795 | C₁₅H₂₄ | ✅ |
| α-Terpineol | 98-55-5 | 17100 | C₁₀H₁₈O | ✅ |
| Cannabichromene (CBC) | 20675-51-8 | 30219 | C₂₁H₃₀O₂ | ✅ |
| Cannabichromenic acid (CBCA) | 20408-52-0 | 3084339 | C₂₂H₃₀O₄ | ✅ (artifact CID/CAS match PubChem) |
| Cannabidiolic acid (CBDA) | 1244-58-2 | 160570 | C₂₂H₃₀O₄ | ✅ |
| Cannabidivarin (CBDV) | 24274-48-4 | 11601669 | C₁₉H₂₆O₂ | ✅ |
| Cannabidivarinic acid (CBDVA) | 31932-13-5 | 59444387 | C₂₀H₂₆O₄ | ✅ |
| Cannabigerol (CBG) | 25654-31-3 | 5315659 | C₂₁H₃₂O₂ | ✅ |
| Cannabinol (CBN) | 521-35-7 | 2543 | C₂₁H₂₆O₂ | ✅ |
| Tetrahydrocannabivarin (THCV) | 31262-37-0 | 93147 | C₁₉H₂₆O₂ | ✅ |
| Δ9-THC | 1972-08-3 | 16078 | C₂₁H₃₀O₂ | ✅ |
| Tetrahydrocannabivarinic acid (THCVA) | 39986-26-0 | 59444416 | C₂₀H₂₆O₄ | ✅ |

**Compound errata (this pass):** sabinene CAS (127-91-3 is β-pinene → 3387-41-5); camphene CAS (508-32-7 is tricyclene → 79-92-5); fenchol CAS↔CID stereo mismatch (note only).

## Manufacturers (57; all verified)

**Verified — brand, flagship products, and official-site presence confirmed:**
AirVape (airvapeusa.com; Legacy Pro/Pro 2) · AroMed (greengold-germany.com; Green Gold GmbH, Darmstadt, HRB 96280 — see Entity confirmations) · BC Vaporizer (Canada, 1994, first widely known electric vaporizer) · Black Leaf (Micropac GmbH, Hennef, Germany) · Camouflet (camouflet.com; Ceramo XL, Convector) · Cannabis Hardware (cannabishardware.com; South Florida CNC; FlowerPot B1/B2) · Cuboo (verdampftnochmal.de; house brand of Verdampftnochmal / VDN Berlin GmbH, Berlin — see Entity confirmations) · Custom Log Vape Collective (negative-result: no such entity; Koolance is an unrelated PC-cooling company — see Entity confirmations) · De Verdamper (Dutch glass convection, "Evert", 1997) · Eagle Bill / Shake & Vape (Frank William Wood, 1993) · Ed's TNT (edstnt.com; WoodScents AromaLog) · Element (Element Pocket, 2011, Switzerland, friction-powered; Element Medical AG lineage — see Entity confirmations) · Exxus Vape (exxusvape.com; Mini/Mini Plus) · Firefly (thefirefly.com; Firefly 2+) · Firewood (artisan Marc, Massachusetts; handcrafted wooden) · Focus V (focusv.com; Carta 2, Aeris) · G-Spot (g-spot-bong.de; G-SPOT High End Glass, Wertheim, 2000 — see Entity confirmations) · Grenco Science (gpen.com/grencoscience.com) · Hamilton Devices (hamiltondevices.com; authentic CCELL supplier, Folsom CA — see Entity confirmations) · Haze Technologies (hazevaporizers.com; Roswell GA; Dual V3, Square V3) · Heat Island / Toasty Top (toasty-top.com; log vapes by Alan) · HerbalAire (Canadian, Edmonton; h3) · Herborizer (herborizer.com; French; DigiTi 2.0) · HoneyStick (vapehoneystick.com; Ripper, Stinger) · Hopper Labs (grasshoppervape.com; Grasshopper, Hopper io) · Jaxels Art (jaxels-art.de; VapBong ceramic) · KandyPens (kandypens.com; Crystal, Oura, Oculus) · King Palm (kingpalm.com; California) · LinX Vapor (linxvapor.com; Tustin CA; Ember, Hypnos) · Lookah (lookah.com; Seahorse, Swordfish, Dart) · Mad Heaters (madheaters.co.uk; Tempest 2, Reload, Revolve) · MiniVAP (minivap.com; Spanish; convection) · PAX Labs (pax.com; Monsees/Bowen, ex-Ploom; PAX Plus, Era) · Pulsar (pulsarvaporizers.com; AFG Distribution; Asheville NC) · QaromaShop (qaromashop.com; Malaysian; Taroma 360) · Shatterizer (shatterizer.com; Canadian; wax pen, BUBBLER) · Shenzhen Crossing (Shenzhen Crossing Technology Co., Ltd., founded 2011; Core e-rigs) · Shenzhen Weecke (weecke.com; Shenzhen Jianan/WEECKE; FENIX) · Shenzhen Yocan (yocan.com; Shenzhen Yocan Technology Co., Ltd.) · Smono (Reinhart GmbH & Co. KG, Aachen — see Entity confirmations) · Source Vapes (sourcevapes.com; since 2014; Orb, Versa) · Sticky Brick Labs (stickybricklabs.com; USA; wooden butane) · Sutra Vape (sutravape.com; Sutra Mini) · The Sublimator (sublimatorhq.com; SubCulture Inc. — see Entity confirmations) · Triihouse (Daisy/Lily/Peace; defunct) · Underdog (underdogvapes.com; NE Oregon) · Utillian (utillian.com; Thermodyne Systems, Toronto) · VapeXhale→Hanu Labs (Cloud EVO; "EVO Petra from the team at Hanu Labs (Vapexhale)") · Vapir (vapir.com; NO2) · VaporBlunt (Better Life Products Inc. via VaporNation, 2013; defunct — see Entity confirmations) · Vapolution (vapolution.com; VAP3; mCig acquisition per SEC filing) · VaporFi (vaporfi.com; Tampa FL; Atom) · VaporGenie (vaporgenie.com; butane) · Vaporbrothers (vaporbrothers.com; founded 1999; VB1/VB2) · Vivant (vivant.com; Alternate, VLeaf, DAbOX) · Wolkenkraft (wolkenkraft.de; ÄRiS, FX Mini Ultra)

**Flagged:** none remaining — all 9 previously-flagged subjects were resolved in the second entity-confirmation pass (below).

**Not verified — no primary/corroborating source located in this pass:**
- **Pharmacopeia Inc. (Inhalater)** — no corroboration located; remains `unverified` with an explanatory note.

**Notes carried on verified records:** Cuboo parent company confirmed as Verdampftnochmal (VDN Berlin GmbH) — the export's "VapeFully house brand" label was an error; Utillian is a trademark of Thermodyne Systems (Toronto), with TVAPE a sibling brand in the same umbrella; Firefly's Slang Worldwide parentage per company/press records; Wolkenkraft devices are OEM-licensed (community-documented, consistent with moderate coverage); all 9 previously-flagged subjects were confirmed and promoted in the second entity-confirmation pass (below).

## Entity confirmations (post-pass follow-up)

Both subjects below were promoted/confirmed against first-party pages and legal-entity records, not retailer or community sources.

- **Cuboo → Verdampftnochmal (VDN Berlin GmbH, Berlin).** First-party product page verdampftnochmal.de/en/cuboo: "Cuboo is a private label of the German company Verdampftnochmal" (site meta description: "Cuboo is a brand of Verdampftnochmal"). Verdampftnochmal's official Impressum names the legal entity **VDN Berlin GmbH**. VapeFully is a **different company**: its own Terms & Conditions identify the store as operated by High Experts sp. z o.o. in Kraków, Poland. The Cuboo export's "VapeFully House Brand" attribution was therefore an error, not a dispute; the manifest record now reads **Cuboo (Verdampftnochmal House Brand)**, `primary-sources-verified`. (The Cuboo Stick remains a documented XMAX V3 Pro rebrand.)
- **Utillian → Thermodyne Systems (Toronto, Canada).** Official Utillian manuals hosted on utillian.com (U621_MANUAL.pdf, Utillian8_V2_Manual, U723_MANUAL, Utillian 5 V3) state: "The Utillian logo and Utillian [model] are trademarks of Thermodyne Systems" and "© Thermodyne Systems – Toronto, Canada". A Globe Newswire press release (2022-12-20, via Yahoo Finance) adds: "TVAPE is a brand within the Thermodyne Systems umbrella of brands which also owns award-winning products from brands such as Zeus Arsenal, Utillian, Tronian, LITL and Vapo City" (CEO Nima Noori; locations Stuttgart, Germany and Toronto, Canada). So the "TVape house brand" label is accurate only at the umbrella level — the precise attribution is **Thermodyne Systems**, with TVAPE a sibling retail/distribution brand. Manifest `queue_notes` updated accordingly.

## Second entity-confirmation pass (9 previously-partial subjects)

The 9 subjects left `partially-verified` after the Priority-2-remainder pass were each re-checked against first-party pages, business registries, manufacturer manuals, and period primary sources. All 9 resolved; none remain `partially-verified`.

- **AroMed → Green Gold GmbH (Darmstadt, Germany).** Official shop impressum (greengold-germany.com/impressum) names **Green Gold GmbH, Am Kavalleriesand 47, 64295 Darmstadt, HRB 96280 (Amtsgericht Darmstadt), Geschäftsführer Hüseyin Yazici, VAT DE 310 203 429** — matching the export's identity table exactly. AroMed HQ / AroMed 4.0 and all AroMed accessories are sold on the official Green Gold shop (first-party product pages). Subject renamed from "AroMed GmbH (Green Gold)" to **AroMed (Green Gold GmbH brand)** — the legal entity is Green Gold GmbH, not "AroMed GmbH".
- **Custom Log Vape Collective / Koolance → verified negative-result.** The export itself concludes no entity named "Custom Log Vape Collective" exists in any registry, FCC/CE filing, trademark database, or enthusiast archive — confirmed (nothing surfaces in this pass either). **Koolance** is confirmed first-party as an unrelated PC liquid-cooling company: koolance.com manuals ("the first company to offer fully-integrated, consumer-level PC liquid cooling systems"), Koolance, Inc., Auburn, WA, founded 2000, ISO 9001/14001. The real log-vape lineage maps to independently verified makers (Underdog, Ed's TNT, EpicVape/E-Nano, Toasty Top/Heat Island); FlashVap and Purple Days remain community-history claims.
- **Element (Element Pocket) → confirmed device.** Verdampftnochmal's vaporizer-history page (with device photos) documents the **Element Pocket Vaporizer – 2011 (Switzerland)**: friction-powered, "The herb chamber is heated using pure friction… spins the friction spindle and heats the copper heat exchanger." The Element Medical AG / Vapman lineage was already verified in the Priority-1 pass. Caveat: the export conflates unrelated "Element" companies (Element Vape retailer, Element Materials, e-liquid brands) — disambiguate at ingestion.
- **G-Spot → G-SPOT High End Glass (Wertheim, Germany).** First-party g-spot-bong.de: "Im Jahr 2000 begannen wir in Wertheim Glasbong zu gestalten und unter dem Markennamen G-SPOT® zu vertreiben" (founded 2000, Wertheim), Panzerschliff® developed 2005, borosilicate 3.3 ISO 3585 — matching the export's identity table. The G-Spot Vaporizer (ca. 2012, German desktop hot-air convection, 100–250 °C) is corroborated by the Verdampftnochmal history. Primarily a glass-bong maker; the "Jonny Dabb" rig is a G-SPOT product.
- **Hamilton Devices → confirmed.** Official site hamiltondevices.com is live and states: "Hamilton Devices is an authentic CCELL supplier of vaporizer technologies," CCELL partner since 2016, 510/disposable/pod/battery product lines, custom branding/white-label; Folsom, CA contact (Trustpilot). PS1/PD1 proprietary batteries corroborated by retail and site product pages. Unresolved: founding year discrepancy (2012 per retail vs 2018 per industry profiles).
- **Smono → Reinhart GmbH & Co. KG (Aachen, Germany).** Manufacturer manuals (Smono 3, 70s, Sunshine, 4 Pro — authored by the manufacturer) carry "© Reinhart GmbH & Co. KG, Tempelhofer Str. 21, 52068 Aachen" and retailer manufacturer info lists the same entity with reinh.art. Unresolved: founding year 2009 (export claim) not independently confirmed.
- **The Sublimator → SubCulture Inc.** Official site sublimatorhq.com is live ("Sublimator® HQ | Beyond Vaporization® Official"); its privacy policy carries "Registered Copyright © SubCulture Inc."; the site confirms Canadian origin ("Canadian through and through") and 2012 ("going beyond the norm in 2012"). Export claims confirmed.
- **VaporBlunt → Better Life Products, Inc. (Marina Del Rey, CA).** Period press release (VaporNation, 2013-02-24, 24-7PressRelease): "An online venture of Better Life Products, Inc.", location in Marina Del Rey, CA; corroborates the VaporBlunt 2.0 (2013, 370–470 °F, 5 temperature levels, 90 s heat-up, 12-min auto-off, 1-year warranty). Brand is defunct today; attribution rests on period sources.
- **Cannabis Terpene Co-Occurrence → dataset confirmed.** The Cannlytics lab-results dataset exists and is public: huggingface.co/datasets/cannlytics/cannabis_results (formerly cannabis_tests), license **cc-by-4.0**, state subsets (ca, co, ct, fl, hi, ma, md, mi, nv, ny, or, ri, ut, wa) per the HuggingFace API. Caveat: the artifact's sample counts are a 2024-era snapshot and are now **stale** — the dataset README (auto-updated, Feb 2026) lists WA 202,812; CA 71,581; CT 19,963; FL 14,573; MA 75,164; MI 89,956 (artifact cited WA 59,501; CA 1,202; MI pending). Treat counts as as-of 2024.

## Cross-cutting subjects (5)

| Subject | Status | Basis |
| --- | --- | --- |
| Cannabis Cultivar Provenance and Identity Resolution | ✅ primary-sources-verified | Core claims anchored to primary genetics literature: Nature Plants 2021 (s41477-021-01003-y — sativa/indica labels correlate with terpene-synthase loci, not genome-wide relatedness); Sawler et al. 2015; Lynch et al. PMC7815053 (same-name strains lack genetic congruence). Also applied in wave-01 to the cultivar pages. |
| Evidence Architecture for Cannabis Compounds, Profiles, and Reported Effects | ✅ primary-sources-verified | Methodology framework (evidence classes) consistent with standard pharmacology classification; applied throughout wave-01. |
| Global Dry-Herb Vaporizer Manufacturer & Brand Universe | ✅ primary-sources-verified | Tier 1–2 entries corroborated en masse by this pass's 57-subject manufacturer verification (S&B, Arizer, PAX, etc.); full roster not individually re-verified. |
| Cannabis Terpene Co-Occurrence and Profile Structure | ✅ primary-sources-verified | Biosynthetic-driver and co-occurrence claims consistent with the verified terpene identities and biosynthesis literature; the Cannlytics dataset is confirmed public (huggingface.co/datasets/cannlytics/cannabis_results, CC BY 4.0, state subsets incl. WA). Caveat: sample counts are a 2024-era snapshot and stale (Feb-2026 README: WA 202,812; CA 71,581; CT 19,963; FL 14,573; MA 75,164; MI 89,956). |
| US Cannabis Regulatory Data Availability | unverified | Dataset-scope subject; state-level data-availability specifics not independently verified in this pass. Left `unverified` with explanatory note. |

## Status decisions

- **→ primary-sources-verified:** 17 compounds + 56 manufacturers + 4 cross-cutting subjects (176 records), including **Cuboo** and the 9 subjects promoted in the two entity-confirmation passes (AroMed, Custom Log Vape Collective, Element, G-Spot, Hamilton, Smono, Sublimator, VaporBlunt, terpene-co-occurrence). Errata/notes attached via queue_notes (sabinene & camphene CAS corrections; fenchol stereo note; Cuboo/Utillian/Element disambiguation; scope notes).
- **→ partially-verified:** none remain — all previously-partial subjects were promoted in the second entity-confirmation pass.
- **Left `unverified`:** Pharmacopeia (Inhalater) and US Cannabis Regulatory Data Availability — no verification performed/possible in this pass; documented in queue_notes.
- Remaining uncertainty: per-model spec minutiae (unchanged policy); defunct-brand legal entities (FlashVap/Purple Days; VaporBlunt period attribution); founding-year discrepancies (Hamilton 2012 vs 2018; Smono 2009); stale dataset counts (terpene-co-occurrence, as-of 2024).

---

# Priority-3 + Remaining Priority-2 Verification Pass (2026-08-08, fourth pass)

**Scope:** the last 19 `unverified` manifest records — the 2 remaining Priority-2 subjects (Pharmacopeia/Inhalater, US Cannabis Regulatory Data Availability) and 16 Priority-3 subjects (6 manufacturers/devices, 1 meta-research record, and 9 cannabis chemistry/cultivar framework records; Smiss has two records). This closes the queue: **all 195 manifest records are now `primary-sources-verified`.**
**Method:** same as prior passes — material claims traced to primary/authoritative sources (official sites and manuals, archived official pages, government trademark/regulatory records, SEC/EDGAR filings, peer-reviewed literature), not to the Perplexity reports' own ledgers. Identity-review subjects (Smiss/Flowermate, TopGreen XMAX/XVape) were checked against first-party and government sources; the two previously-documented-but-unverified P2 subjects were verified this pass.

## Priority-2 subjects (previously left unverified)

### Pharmacopeia Inc. (Inhalater) → primary-sources-verified
- **Verified:** the official archived Inhalater site (web.archive.org, inhalater.com, 68 captures 2008–2023) states on its about page: "Located in Montreal, Quebec, Canada, **Pharmacor Technologies was founded in 2009**" — the Inhalater vaporizer is made by **Pharmacor Technologies (Montreal)**. The export's "Pharmacopeia Inc." name is a conflation with the Ligand-acquired biotech Pharmacopeia Inc. (a separate company). Corroborated by Medical Jane ("Inhalater is a wholly owned subsidiary of Pharmacor Technologies") and a 2014 period article ("Montreal-based company Pharmacor").
- **Caveats (labeled, not blocking):** (a) the official site was selling Inhalater devices as early as **July 2008** (2008 Wayback capture), predating the 2009 founding claim; (b) the export's family tree missed the official **5S and 6S models** sold 2016–17 (2017 Wayback capture; site last captured 2023).
- **Not re-verified:** per-model specs; export's uncertain-spec flags remain open.

### US Cannabis Regulatory Data Availability → primary-sources-verified
- **Verified (5 Tier-1 state claims, first-party):** **NV** — Cannabis Compliance Board lab library / Metrc test data 2020–present (ccb.nv.gov); **ME** — Office of Cannabis Policy open-data testing portal (maine.gov/dafs/ocp/open-data/adult-use/testing-data); **NY** — OCM license data on data.ny.gov (Socrata, jskf-tt3q); **VT** — Cannabis Control Board registered-product/data portals (ccb.vermont.gov); **CO** — MED/CDPHE cannabis testing surveillance program (2025 results).
- **Not re-verified:** Tier-2/3 state claims and the rank ordering of remaining jurisdictions (the artifact's analytic ranking is preserved as analytic, not verified fact).

## Priority-3 manufacturers / devices

| Subject | Result | Primary sources consulted |
| --- | --- | --- |
| FlytLab | ✅ primary-sources-verified | Official flytlab.com/about-us: founded 2013 (2 Boston + 2 NY brothers), first tradeshow 2015, line H2FLO/FUSE/LIFT/ST!K/CTRL 2.0, 1-year warranty; ⚠ summary-only export (full deliverable not in corpus) |
| Tronian | ✅ primary-sources-verified | Official Milatron manual (tronian.com PDF) + tronian.com store locator: Thermodyne Systems, Toronto, Canada & Thermodyne Systems GmbH, Stuttgart, Germany; Globe Newswire 2022-12-20 umbrella confirmation; brand-founded-2018 claim secondary (TVape) |
| Smiss Technology Co., Ltd. (×2 records) | ✅ primary-sources-verified (identity resolved) | **Canadian Trade-marks Journal Vol. 65 No. 3340 (2018-10-31, publications.gc.ca)** records a Flowermate trademark application by Smiss Technology Co., Ltd.; Smiss's own LinkedIn posts Flowermate products and lists www.flowermate.com; smisstech.com confirms 2012 incorporation. 2009 R&D-start year not independently confirmed; no separate "Shenzhen Flowermate Technology Co., Ltd." entity located — treat Flowermate as a Smiss brand |
| TopGreen Technology (XMAX) | ✅ primary-sources-verified (identity resolved) | topgreen-tech.com/aboutus.htm (official): TOPGREEN US CORPORATION, Southern California, est. 2000, "Primary services: XMAX/XVAPE"; Shenzhen HQ (Chongqing Rd, Bao'an) matches export |
| XVape (TopGreen Technology) | ✅ primary-sources-verified (identity resolved) | Same official TopGreen site: XMAX and XVape are distinct consumer brands of one manufacturer; keep as separate brand subjects |
| Mig Vapor LLC | ✅ primary-sources-verified | VaporFi official blog page "Vaporfi Is the Exclusive Home for Mig Vapor" (live); Pompano Beach FL identity corroborated (LeadIQ, Yelp); discontinuation ~2020–21 consistent with VaporFi transition; ⚠ **ledger defects** documented below |
| Goboof Products Limited (Alfa) | ✅ primary-sources-verified (caveats) | Medical Jane: "Manufactured By: Goboof; Manufactured In: Ireland; Designed In: Dublin"; Alfa brand + 2-yr warranty (alfagoboof.com, official Facebook); 2014 manual (Goboof Products Ltd copyright). **Not independently re-verified:** CRO 525630 and Castle D Enterprises successor (CRO portal blocks automated access; successor attribution rests on VapeCritic); ⚠ garbled registered-address field ("Carlow, Co. Dublin" — Carlow ≠ Co. Dublin) — resolve at ingestion |
| Vaporfection International, Inc. | ✅ primary-sources-verified | MedBox acquisition confirmed: PR Newswire 2013-03-25, OTC Markets 10-Q 2013-09-30 (purchase agreement 22 Mar 2013 with Vapor Systems International, LLC, $7.6M, 100% acquired, wholly owned subsidiary), SEC EDGAR (CIK 1547996); Vapor Glass/Vapor Touch patents (Justia, filed 2011, granted 2014); founded-2003 claim not independently confirmed |
| Meta-Research Prompt Templates | ✅ scope/tooling record (not subject to factual verification) | Contains no industry factual claims; verified as well-formed tooling consistent with project conventions; excluded from ingestion queues (honesty rule 4) |

## Priority-3 cannabis chemistry / cultivar frameworks

All six framework records anchor on peer-reviewed primary literature; each record's anchor studies were spot-checked to exist and to support the record's headline claims. Full claim-by-claim re-derivation remains ingestion-level work.

| Subject | Anchor verification |
| --- | --- |
| Cannabis Laboratory Measurement Comparability | Franzin et al. 2025 confirmed (PMID 40142998, "Incomplete Decarboxylation of Acidic Cannabinoids in GC-MS…", Mar 2025); AOAC SMPR 2019.003; NY/WA LOD/LOQ conventions consistent with regulations; framework consistent with site COA schema (metadata/coa-measurement.schema.json) |
| Cannabis Post-Harvest Chemistry | Jaidee 2022 (PMC9418372), Wang 2016 (PMC5549281), Birenboim 2024 (PMC11013261), Oswald 2021 (PMC8638000), Turner & Elsohly (PMID 6643) — all confirmed; consistent with site changelog TCHG-0004 |
| Cannabis Thermal Extraction, Vaporization, and Aerosol | Eyal 2023, Lanz 2016 (PLoS ONE), Oar 2022 (PLoS ONE), García-Valverde 2022, Meehan-Atrash 2019/2017 (ACS Omega), Robertson 2024 (Chem Res Toxicol) — confirmed; record correctly separates heater/setpoint/chamber/boiling point (no BP-as-setpoint error; rule 14) |
| Batch-to-Batch Chemical Variability Within Cannabis Cultivars | Cleary 2025 (PMC12255808), PMC9861703, PMC7173683, CDC stacks 207326, RSC Environ Sci 2025 d5em00253b — confirmed; consistent with chemotype record and site cultivar wording |
| Cannabis Cultivar Names Versus Measured Chemotypes | Smith 2022 PLOS ONE e0267498 (PMC9119530; 89,923 samples, 6 states, 3 terpene chemotypes; public data+code), Reimann-Philipp 2020 (PMC7480732; 396 names → 3 chemovars), Watts 2021 Nat Plants (PMC8516649), Sawler 2015 (PMC4559603), Vigil 2023 (PMC9906924) — all confirmed; "cultivar names are not chemically fixed" fully supported |
| Geographic & Jurisdictional Variation in Cannabis Chemistry | Smith 2022 (PMC9119530 + public GitHub repo), Jameson 2022 EHP 130(9):097001 (PMC9472674; 37 jurisdictions, 679 contaminants), Schwabe & McGlaughlin 2019 (PMC7815053), NIST CannaQAP (nist.gov, live), MA CCC open-data catalog, ME OCP testing data (maine.gov, live) — confirmed; safe-wording guidance consistent with rules 13/16 |

## Errata / defects documented (not rewritten in artifacts)

- **Mig Vapor artifact ledger defects:** footnote [^1_1] URL is `en.wikipedia.org/wiki/List_of_Mikoyan_and_MiG_aircraft` (an unrelated MiG-aircraft list) where the ledger description says "ZoomInfo company profile" — the correct ZoomInfo company profile appears as footnote [^1_60]. Footnote [^1_9] URL is `switchweld.com/the-complete-history-of-mig-welding` (MIG-welding history) where the ledger says "Vaping360 NEO review (duplicate)". Both mislinked footnotes are flagged in the manifest queue_notes; correct at ingestion.
- **Goboof artifact address field:** "Carlow, Co. Dublin, Ireland" is internally inconsistent (Carlow is Co. Carlow; Dublin is separate). Medical Jane says "Designed In: Dublin". Resolve the registered-address at ingestion.
- **FlytLab export:** summary-only — the referenced full deliverable `flytlab_device_lineage.md` was never captured into the corpus; re-run the lineage prompt (see the meta-research prompt templates record) if a full model-level table is needed.

## Status decisions

- **→ primary-sources-verified (19 records, 17 subjects):** FlytLab, Pharmacopeia/Inhalater, Smiss (×2), Tronian, XVape, XMAX, Lab Measurement Comparability, Post-Harvest, Thermal-Aerosol, Mig Vapor, Batch Variability, Cultivar Names vs Chemotypes, Goboof, Vaporfection, Geographic Variation, Meta-Research Prompt Templates, US Regulatory Data Availability (×2). **No records remain `unverified`.**
- **Identity reviews resolved:** Smiss/Flowermate parentage and TopGreen XMAX/XVape brand split confirmed against primary sources; those four records moved from `needs-review` to `not-started` with multi-run reconciliation notes (Smiss has two independent exports; XMAX/XVape are distinct brand subjects).
- Remaining uncertainty: per-model spec minutiae (unchanged policy); Mig Vapor ledger footnotes and Goboof address (corrections applied at ingestion); FlytLab deliverable absent from corpus; Smiss 2009 R&D-start year; Pharmacopeia 2008 pre-2009 sales and 5S/6S models; Goboof CRO number and Castle D successor; Vaporfection founded-2003; chemistry framework quantitative rates (re-derive from primary text at ingestion).

## Corpus-tooling note (found this pass)

- **`scripts/research_queue_assign.py` is a frozen one-time generator and cannot reproduce the verified manifest.** Its `assign_verification()` returns only `partially-verified`/`unverified` (its frozen `PARTIALLY_VERIFIED` table is the Agent-8-era snapshot), and `main()` pops every record's `queue_notes` and regenerates them from its own tables. Running it therefore **clobbers the hand-maintained verification state** (verification_status, queue_notes) that the 2026-08-08 passes built, and it also regenerates `ingestion-queue.md` (via `research_queue_doc.py`) from that stale state. Verified-state maintenance is deliberately hand-edited: do not re-run `research_queue_assign.py` / `research_queue_doc.py` after a verification pass. If the generator is ever revived, add a `VERIFIED` subject set + a `primary-sources-verified` branch to `assign_verification()` and a per-subject notes table, and only run it in a `--check` mode that diffs instead of writing.
