# Terminology Consistency Report

Documents the standardized claim vocabulary applied across `content/`, aligned with the existing `reference/TREF-0003` (Evidence Labels and Claim Grammar) page.

## Evidence class vocabulary (applied to every biological claim)

| Label | Meaning | Example verb |
| --- | --- | --- |
| Human clinical | Controlled human trial or human observational study | "found", "a double-blind trial found" |
| Human observational | Epidemiological/survey/sensory studies | "observational studies suggest" |
| Preclinical / animal | In vivo rodent/animal model | "preclinical rodent models report" |
| In vitro / cellular | Cell culture, enzyme, or receptor assay | "receptor-binding and cell assays report" |
| Traditional use | Ethnographic/historical herbal use | "documented in traditional practice" |
| Manufacturer claim | Promotional statement from a manufacturer | "per manufacturer" / "is DynaVap marketing language" |
| Breeder claim | First-party breeder or seed-bank narrative | "first-party breeder documentation" |
| Retailer claim | Third-party vendor or marketing text | "reported by third parties" |
| Anecdotal report | Self-reported consumer/community reports | "frequently noted by consumers" |
| Editorial inference / unknown | Author inference, no located source | "remains unresolved / uncited in this archive" |

## Conventions enforced during this pass

1. **Boiling point ⇒ pressure required.** Every terpene physical-property table states its reference pressure (101.325 kPa for atmospheric values, or the specific reduced pressure). Where the pressure of a reported value is unknown or only inferred, the page says so (see α-bisabolol, β-pinene, nerolidol).
2. **No "activation temperature" language.** The archive now uses "standard/reference boiling point" and explicitly avoids implying a device "activation" set-point from a chemical boiling point. The shared include `boiling-point-vs-device-note.md` states that a boiling point is not a device setting.
3. **No medical recommendations.** No terpene or device page recommends dosages or treatment temperatures. The two human-clinical rows retained (cineole bronchitis; limonene + cannabis) describe study results, not dosing guidance.
4. **Receptor activity ≠ clinical evidence.** β-caryophyllene CB2-receptor activity was moved out of the "Human evidence" section into the preclinical/in-vitro section and is labeled as an in-vitro observation (Gertsch 2008).
5. **Aroma ≠ proof of content.** Cultivar pages describe aroma only under "breeder notes" / "descriptors", never as measured terpene content; cultivar-identity and first-party-provenance includes shield these.
6. **Cultivar name ≠ fixed chemical profile.** Standardized disclaimer on all cultivar pages and the cultivars trunk; chemovar data is only ever sourced from a linked batch COA.
7. **Marketing terms are attributed, not asserted.** "Medical grade", "isolated airpath", "precision", "certified", "aerospace material" — where present, each is now attributed to the manufacturer or flagged as a marketing term via `manufacturer-claim-note.md`. No such term is presented as an established engineering fact without scope and evidence.
8. **Measured vs calculated vs predicted.** Boiling points: "mean of N determinations" (NIST), "Antoine estimate", or "predicted". COA totals: "calculated value (THCA × 0.877 + Δ9-THC)".
9. **Demo/sample ≠ evidence.** Product and COA records now carry the `demo-sample-record-warning.md` include and are excluded from "verified" framing on cultivar pages and trunks.

## Terminology deltas applied

| Old phrase (pre-audit) | New standard phrase |
| --- | --- |
| "boiling point" (pressure omitted) | boiling point + stated reference pressure |
| "activation temperature" | not used |
| "medical-grade …" | manufacturer marketing language, attributed |
| "Verified certificate of analysis" (sample record) | "Sample/demonstration COA; not verified" |
| "full agonist at CB2" (as human evidence) | "receptor-binding and cell assays report CB2 binding (in vitro)" |
| "confirm/confirms/demonstrate" for unverified claims | "report/reports" or "remains uncited" |
| "190–210 °C click" (DynaVap) | "~230–250 °C Captive Cap / ~205–220 °C Low-Temp (per DynaVap)" |
| "18650 battery" (Mighty+) | "two internal lithium-ion cells, 3300 mAh total (per manufacturer); '18650' is third-party" |
| "Plamondon Enterprises Inc." (Arizer) | "Arizer (Canada-based); third-party business records list 7111495 Canada Inc." |
| "founded 2006" (Arizer) | "founded 2005 (per official history)" |

## Remaining inconsistent usages (not changed)

- `guides/TGDE-0002` (Apex Specimen) intentionally demonstrates ornamental Apex features; it now carries a "illustrative sample data" note but still exercises over-stuffed formatting by design.
- `reference.md`, `specs.md`, `safety.md` trunks use shorthand collection captions; they were updated where they described deleted placeholder content but otherwise kept generic.
- Legacy `law-and-use/` content was not touched (outside the allowed edit scope) even where effective-date language appears; `includes/legal-effective-date-warning.md` was created for adoption there later.