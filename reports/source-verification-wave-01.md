# Source Verification Wave 01 — Claim Ledger

**Agent 3 — Research Verification & Source Hardening**
**Date:** 2026-08-08
**Corpus:** `research/` (organized research corpus, `_index/manifest.jsonl`)
**Method:** Existing site content audited against the research corpus; material claims traced from corpus source ledgers back to authoritative primary sources (PubMed/NIH, CPSC, first-party manufacturer/breeder documentation). No Perplexity synthesis was treated as primary evidence; every new citation added on-page was independently verified against the primary record before inclusion.

## Scope of audit

Collections inspected: `content/terpenes/`, `content/cultivars/`, `content/devices/`, `content/manufacturers/`, `content/guides/`, `content/reference/`, `content/includes/`.

## Claim ledger

| Claim | Existing source | Better source | Evidence class | Action |
| ----- | --------------- | ------------- | -------------- | ------ |
| Terpinolene antioxidant / antiproliferative in brain cells | Uncited ("remain uncited in the archive") | Aydin E, Türkez H, Taşdemir Ş. *Arh Hig Rada Toksikol.* 2013;64(3):415–424. PMID 24084350 | In vitro (rat neurons, N2a cells) | **strengthened** |
| Terpinolene sedative-like effect, inhaled | Not stated | Ito K, Ito M. *J Nat Med.* 2013;67(4):833–837. PMID 23339024 | In vivo (mouse, inhalation) | **strengthened** (added) |
| α-Humulene anti-inflammatory (airways) | Uncited | Rogerio AP, et al. *Br J Pharmacol.* 2009;158(4):1074–1087. PMID 19438512 | In vivo (mouse, oral/aerosol) | **strengthened** |
| Ocimene anti-inflammatory / analgesic (NSAID gastric ulcer model) | Uncited | *ACS Pharmacol Transl Sci.* 2025. doi:10.1021/acsptsci.4c00639. PMID 40109750 | In vivo + in vitro (rodent) | **strengthened** |
| Ocimene antifungal | Uncited | None located in corpus ledgers | — | **marked uncertain** (retained as unresolved; no primary source found) |
| Eucalyptol (cineole) COPD exacerbations, oral | Only bronchitis RCT (Fischer & Dethlefsen 2013) | Worth H, et al. *Respir Res.* 2009;10:69. PMID 19624838 | Human RCT (oral, 200 mg TID) | **strengthened** |
| Eucalyptol preclinical anti-inflammatory / airway claims | Uncited | El Shiekh RA, et al. *Inflammopharmacology.* 2024. doi:10.1007/s10787-024-01588-8. PMID 39499358 | Peer-reviewed review of preclinical data | **strengthened** (labeled review; no inhalation-route human data) |
| Linalool anxiolytic, inhaled (mice) | Uncited | Linck VM, et al. *Phytomedicine.* 2010;17(8–9):679–683. PMID 19962290 | In vivo (mouse, inhalation) | **strengthened** |
| Linalool CNS-depressant / anticonvulsant (high-dose rodent) | Uncited | None located in corpus ledgers | — | **marked uncertain** (retained as unresolved) |
| Nerolidol skin-penetration enhancer; antiparasitic/antifungal/sedative | Uncited | Chan WK, et al. *Molecules.* 2016;21(5):529. PMID 27136520 | Review; in vitro human-tissue + animal | **strengthened** (labeled review) |
| D-Limonene gastroprotective / antioxidant / anti-inflammatory | Uncited | Sanshita, Devi N, et al. *Int J Nanomedicine.* 2025;20:4433–4460. doi:10.2147/IJN.S514247 | Peer-reviewed review (animal/in vitro) | **strengthened** (labeled review) |
| β-Pinene cytotoxic / antioxidant (cellular) | Uncited | None located in corpus ledgers | — | **marked uncertain** (retained as unresolved) |
| α-Bisabolol, β-caryophyllene, β-myrcene, α-pinene boiling points & bioactivity | NIST WebBook (SRD 69); PMID-cited literature | Confirmed consistent with corpus ledgers | Primary physical data; mixed evidence classes | **retained** |
| DynaVap M7 release year (2024) | DynaVap 2024-lineup materials (dynavap.eu blog) | DynaVap first-party pages; one third-party source (VapoChecker) dates M7 to 2023 | Manufacturer claim | **retained** (prefer first-party; discrepancy logged in page footnote context) |
| Mighty+ temperature range 40–210 °C, chamber 1.4 cm³, 3300 mAh | Storz & Bickel support/product pages | Corpus export quotes S&B technical specifications matching the page | Manufacturer spec | **retained** (corpus corroborates) |
| Solo III 80/20 convection/conduction, USB-C, modes | Arizer product page | Corpus device-lineage export corroborates (Solo III v1/v2/v2.0, 80/20 hybrid) | Manufacturer spec | **retained** |
| Solo III battery fire/burn hazard | **Not mentioned on site** | CPSC recall 26-565 (June 18, 2026; ~5,000 units; serial prefixes; free Solo III V2); Health Canada recall | Regulatory / safety | **strengthened** (recall notice added to device + manufacturer pages) |
| Solo II battery fire/burn hazard (2025) | **Not mentioned on site** | CPSC recall (September 18, 2025; ~5,460 US units; serial prefix "M2"; free Solo II MAX) | Regulatory / safety | **strengthened** (added to Arizer manufacturer page) |
| Durban Poison: South African landrace, inbred during the 1970s | None | Dutch Passion strain page (first-party) | First-party breeder claim | **strengthened** |
| Jack Herer: Haze × NL#5 × Shiva Skunk; Sensi Seeds | None; "mid-1990s" development | Sensi Seeds product page + blog (breeding work began in the 1980s) | First-party breeder claim | **strengthened** + **softened** (release-decade conflict noted; third-party accounts date release to mid-1990s) |
| Northern Lights: Thai × Afghani landrace; Sensi redevelopment | None | Sensi Seeds product page (first-party) | First-party breeder claim | **strengthened** |
| Northern Lights: Pacific Northwest, USA origin; arrived 1980s | None | Not on Sensi's first-party page | Secondary/community claim | **softened** (flagged as secondary-account) |
| Blueberry: DJ Short origin; Afghan/Purple Thai/Highland Thai lineage | None | Dutch Passion blog (DJ Short, 1990s); DJ Short breeding accounts | Breeder claim | **strengthened** (labeled breeder-attributed, unverified genetically) |
| Mazar: Afghan (Mazar-i-Sharif) × Skunk #1; improved 1997 | None | Dutch Passion strain page; DP catalog text "improved the variety in 1997" | First-party breeder claim | **strengthened**; "renamed 1997" **marked uncertain** (secondary report, consistent with first-party) |
| Skunk #1: Acapulco Gold × Colombian Gold × Afghan | None | Sensi Seeds blogs (origins; Sam the Skunkman) | First-party breeder claim | **strengthened** |
| Skunk #1: Sacred Seeds / California, 1970s | None | Not asserted by Sensi's own documentation | Community/secondary claim | **softened** (flagged as community-reported) |
| Super Skunk: Skunk #1 × Afghan hash plant; released 1990 | None | Sensi Seeds product page + blog (1990s) | First-party breeder claim | **strengthened**; exact "1990" **softened** to "1990s (per first-party; 1990 in third-party refs)" |
| Strawberry Cough: Strawberry Field(s) × Haze | None | Dutch Passion catalog; consistent secondary references; no first-party pedigree page located | Widely reported | **strengthened** (lineage); breeder credit (Kyle Kushman vs. Jeff Cavanagh) **marked uncertain** (disputed) |
| Blue Dream: Blueberry × Haze | None | DJ Short (djgenetics) "Azure Haze" page — "the same cross as the Blue Dream"; secondary references | Breeder-consistent + secondary | **strengthened**; Santa Cruz origin **marked uncertain** (secondary-account) |
| Cultivar terpene "descriptors" as fixed chemotypes | None written as universal; descriptor lists + warnings present | No universal "Blue Dream contains X" statements found; batch-demo record already labeled | — | **retained** (no unsupported universal claims found) |

## Special safety: marketing-language scoping

| Phrase | Where | Scope on page | Action |
| ------ | ----- | ------------- | ------ |
| "medical grade stainless steel" (DynaVap) | `devices/dynavap-m7.md`, `manufacturers/dynavap.md` | Scoped to marketing language; 316 grade only stated on selected component pages | **retained** (already scoped) |
| "isolated air path" (Arizer) | `devices/TED-0001.md` | Explicitly marked as marketing phrase; not asserted as verified engineering fact | **retained** (already scoped) |
| "medical grade" / EU MDR Medic status (Storz & Bickel) | `devices/mighty-plus.md`, `manufacturers/storz-bickel.md` | Consumer Mighty+ explicitly distinguished from Mighty+ MEDIC / Volcano MEDIC 2 (TÜV SÜD, July 2023) | **retained** (already scoped) |
| "food safe" / "aerospace grade" | — | Not present in audited content | n/a |

## Corpus ledger corrections discovered

These are errors in the research corpus source ledgers that were caught while tracing claims to primary sources. Site citations use the corrected forms.

| Corpus ledger entry | Correct primary record |
| ------------------- | ---------------------- |
| Terpinolene antioxidant/anticancer: "Gasic et al. 2013 (PMID 24084350)" | Aydin E, Türkez H, Taşdemir Ş. *Arh Hig Rada Toksikol.* 2013;64(3):415–424. PMID 24084350 |
| Linalool inhaled anxiolysis: "Kashiwadani et al. 2010 (PMID 19962290)" | Linck VM, et al. *Phytomedicine.* 2010;17(8–9):679–683. PMID 19962290. (Kashiwadani et al. is the 2018 *Front Behav Neurosci* paper, PMID 30405369 — a different study) |
| D-Limonene review: "Devi N, et al. Pharmaceutics 2025;17:102. doi:10.3390/pharmaceutics17050567" | Sanshita, Devi N, et al. *Int J Nanomedicine.* 2025;20:4433–4460. doi:10.2147/IJN.S514247 (not a Pharmaceutics article) |

## Files added

- `reports/source-verification-wave-01.md` (this ledger)

## Files modified

- `content/terpenes/terpinolene.md` — primary citations added (Aydin 2013; Ito & Ito 2013)
- `content/terpenes/alpha-humulene.md` — primary citation added (Rogerio 2009)
- `content/terpenes/ocimene.md` — primary citation added (ACS PT Sci 2025); antifungal flagged unresolved
- `content/terpenes/eucalyptol.md` — human COPD RCT added (Worth 2009); preclinical claims cited to review (El Shiekh 2024)
- `content/terpenes/linalool.md` — primary citation added (Linck 2010); CNS claims flagged unresolved
- `content/terpenes/nerolidol.md` — review citation added (Chan 2016)
- `content/terpenes/d-limonene.md` — review citation added (Sanshita/Devi 2025)
- `content/devices/TED-0001.md` — Solo III CPSC recall notice (recall 26-565) + source
- `content/manufacturers/arizer.md` — Solo II (2025) and Solo III (2026) recall history + sources
- `content/cultivars/durban-poison.md`, `jack-herer.md`, `northern-lights.md`, `blueberry.md`, `mazar.md`, `skunk-1.md`, `super-skunk.md`, `strawberry-cough.md`, `blue-dream.md` — first-party provenance/source sections; contested claims scoped

## Validation

- `./bin/validate_graph.sh` — see run below
- All new on-page citations verified against PubMed/CPSC/first-party pages before inclusion (access date 2026-08-08)

## Research corpus records consumed

- `research/_index/manifest.jsonl`, `research/_index/inventory.md`
- `research/compounds/terpenes/{terpinolene,linalool,nerolidol,d-limonene,ocimene,eucalyptol,alpha-humulene,beta-pinene,alpha-bisabolol,alpha-pinene,beta-caryophyllene,beta-myrcene}/` artifacts + dated exports
- `research/cannabis/cultivar-identity/artifact.md` (source hierarchy, claims model)
- `research/cannabis/effects-evidence/source/2026-08-08-perplexity.md` (evidence architecture)
- `research/devices/manufacturers/{dynavap,storz-bickel,arizer}/source/*.md`

## Suggested next work

- Verify the remaining unresolved claims flagged "marked uncertain" (ocimene antifungal, linalool CNS, β-pinene cellular) against new primary literature when the corpus is extended.
- Run the same ledger treatment on the `content/guides/` and `content/reference/` collections' factual assertions (e.g., THC conversion factor, lab-method guidance) against the laboratory-comparability corpus research.
- Extend the recall treatment to other device records when CPSC/Health Canada publish further notices.
