# Unresolved-Claims Report

Columns: **Page · Claim · Current wording · Problem · Needed source · Recommended action · Severity**

Severity: `high` = potentially misleading if read as fact; `med` = needs citation but hedged; `low` = cosmetic/descriptive.

Bulk of the floral/aromatic "dominant terpene descriptor" claims on cultivar pages (`content/cultivars/*.md`) are breeder/consumer marketing descriptors, not measured values. They are already shielded by the `cultivar-identity-warning` include, so they are not enumerated individually below.

## 1. Terpenes (`content/terpenes/`)

| Page | Claim | Current wording after edit | Problem | Needed source | Recommended action | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| alpha-pinene | Bronchodilator in humans | "No verified controlled human study of inhaled α-pinene as a bronchodilator was identified … remains unresolved" | Widely circulated claim; no human inhalation study found | Controlled human study of inhaled α-pinene | Keep as "unresolved"; add source when located | high |
| alpha-pinene | AChE inhibition + antimicrobial (in vitro) | "In vitro assays report acetylcholinesterase inhibition, antimicrobial activity, and suppression of inflammatory signaling" | Only anti-inflammatory (Kim 2015) is cited; AChE/antimicrobial uncited | Primary in vitro assays for AChE inhibition and antimicrobial activity | Cite or split claim; log | med |
| alpha-bisabolol | Topical anti-inflammatory in humans | "Topical application research reports … limited human trials" | Review (Eddin 2022) cited; primary human topical data limited | Controlled human topical trials | Keep hedged; add primary human study if found | med |
| alpha-humulene | Atmospheric bp 264 °C | "Standard boiling point 264 °C (atmospheric; unconfirmed by NIST)" | NIST lists only ≈123 °C @ 0.013 bar | A measured atmospheric bp | Keep flagged; replace when a measured value is sourced | high |
| alpha-humulene | Animal anti-inflammatory | "Animal inflammation models report topical and systemic anti-inflammatory markers; … uncited" | Uncited | Primary animal anti-inflammatory study | Cite or remove | med |
| beta-caryophyllene | Atmospheric bp 263 °C | "Standard boiling point 263 °C (atmospheric; unconfirmed by NIST)" | NIST (CAS 87-44-5) lists no bp | Measured atmospheric bp | Keep flagged | high |
| beta-caryophyllene | Human benefit | "No controlled human clinical trials establishing a benefit … were identified" | No human RCT | Controlled human trial | Keep as "unresolved" | high |
| beta-caryophyllene | Preclinical anti-inflammatory/antinociceptive via CB2 | "receptor-binding and cell assays report … rodent models report … attributed to CB2 pathways" | Gertsch 2008 cited for receptor; additional rodent studies uncited | Primary rodent anti-nociception study | Add additional primary refs or split | med |
| beta-pinene | Atmospheric bp 166 °C | "Standard boiling point 166 °C (Antoine estimate; not explicitly listed by NIST)" | NIST lists no explicit bp; Antoine-consistent only | Measured atmospheric bp | Keep flagged | med |
| beta-pinene | In vitro cytotoxic/antioxidant | "Cellular studies report cytotoxic and antioxidant properties; … uncited" | Uncited | Primary in vitro study | Cite or remove | med |
| d-limonene | Standalone mood/anxiolytic | "A standalone mood-lifting or anxiolytic effect … is not established by that trial" | Only THC co-administration RCT (Spindle 2024) located | Standalone d-limonene RCT | Keep as "unresolved" | high |
| d-limonene | Gastroprotective/antioxidant (in vitro) | "…report gastroprotective, antioxidant, and anti-inflammatory properties; … uncited" | Uncited | Primary studies | Cite or remove | med |
| eucalyptol | Preclinical airway anti-spasmodic + cytokine | "Preclinical studies report inhibition of inflammatory cytokine signaling and anti-spasmodic airway activity; … uncited" | Only human bronchitis RCT (Fischer 2013) cited | Primary preclinical airway/cytokine studies | Cite or remove | med |
| linalool | Rodent CNS depressant/anticonvulsant | "Rodent assays report central nervous system depressant and anticonvulsant potential; … uncited" | Uncited | Primary rodent studies | Cite or remove | med |
| linalool | Human anxiety (pure linalool) | "No randomized controlled trial of pure linalool for anxiety was located …" | Only non-RCT physiology study (Sugawara 1998) cited | Pure-linalool anxiety RCT | Keep as "unresolved" | med |
| nerolidol | Atmospheric bp 276 °C | "Standard boiling point 276 °C" with isomer-record caveat | NIST value from nerolidol isomer record (549.2 K); CAS 7212-44-4 lists reduced-pressure only | Consistent measured bp for CAS 7212-44-4 | Keep flagged | low |
| nerolidol | Penetration enhancer + antiparasitic/antifungal/sedative | "…no human clinical evaluation … identified … remain uncited" | Uncited | Primary studies | Cite or remove | med |
| ocimene | Atmospheric bp 176 °C | "Standard boiling point 176 °C (predicted; unconfirmed by NIST)" | NIST (CAS 13877-91-3) lists no bp | Measured atmospheric bp | Keep flagged | med |
| ocimene | Antifungal/anti-inflammatory screens | "Laboratory screens report antifungal and anti-inflammatory properties; … uncited" | Uncited | Primary studies | Cite or remove | med |
| terpinolene | In vitro antioxidant + cancer-cell growth inhibition | "In vitro research reports antioxidant activity and growth inhibition in selected cancer cell lines; … uncited" | Uncited | Primary studies | Cite or remove | med |

## 2. Botanicals

| Page | Claim | Current wording | Problem | Needed source | Recommended action | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| botanicals/citrus | 90–95% monoterpene in peel oil | "…commonly reported to contain roughly 90–95% monoterpene content" | Industry figure; species/cultivar dependent | Primary analytical measurement | Keep attributed; attach a measurement source | med |

## 3. Devices

| Page | Claim | Current wording | Problem | Needed source | Recommended action | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| devices/dynavap-m7 | Heat-up times | "~5–10 seconds (induction) / ~10–15 seconds (flame) — per DynaVap marketing" | Manufacturer/advertised figures, not independently timed | Independent timing or official spec | Keep attributed | low |
| devices/mighty-plus | Battery is "18650" format | "…'18650' cell format is reported by third parties, not stated officially" | Official docs specify 2 Li-ion cells, 3300 mAh total; no cell format | Teardown/official documentation of cell format | Keep attributed | low |
| devices/mighty-plus | Chamber ≈0.25 g | "≈0.25 g raw flower is a third-party estimate, not an official figure" | Official figure is 1.4 cm³ | Official mass-capacity figure | Keep attributed | low |
| devices/mighty-plus | "Full charge ~2 h" | Removed; replaced with "~80 % in ~40 minutes" (official) | No official full-charge time | Official full-charge figure | Re-add only if sourced | low |

## 4. Manufacturers

| Page | Claim | Current wording | Problem | Needed source | Recommended action | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| manufacturers/arizer | Legal entity "Plamondon Enterprises Inc." | Replaced with "Arizer (Canada-based; third-party business records list 7111495 Canada Inc.)" | "Plamondon Enterprises" could not be verified as Arizer's entity | Primary corporate registry record | Keep attributed | med |
| manufacturers/arizer | "isolated stainless/ceramic chamber" | retained with manufacturer-claim include | Description; structural detail | Arizer engineering spec | Attribute explicitly | low |
| manufacturers/dynavap | M7 specific "316" grade | "the specific '316' grade … not stated on the M7 pages" | 316 stated only on some component pages | DynaVap M7 material spec sheet | Keep flagged | low |
| manufacturers/storz-bickel | EU MDR risk class "IIa" | Not stated; only says "certified under EU MDR (July 2023, TÜV SÜD)" | Risk class IIa appears only in third-party/ARTG sources | Official MDR certificate classification | Leave unstated until sourced | low |

## 5. Cultivars / other

| Page | Claim | Current wording | Problem | Needed source | Recommended action | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| cultivars/* | Lineage + breeder dates/details | Labeled as first-party breeder claims (include) | Single-source breeder narratives | Original breeder archives | Keep attributed; add breeder primary docs | low |
| cultivars/blue-dream | Attached batch "evidence" | Relabeled "Sample Laboratory Records (Demonstration)" | COA is a fabricated sample batch | Real batch COA | Replace sample with a verified COA when available | high |

## Claims intentionally left unresolved (summary)

The 22 terpene/botanical rows above, the four device rows, and the four manufacturer rows. None were fabricated; every unresolved numeric/biological claim was softened and marked "unresolved"/"uncited" in the page content, and each is recoverable once a primary source is attached.