---
id: lab-results/TLAB-0001
title: "Sample COA: Buckeye Relief Blue Dream Batch 123 (Demonstration)"
parent: lab-results
status: published
tags: ["lab-results", "coa", "analytics", "batch", "sample", "demonstration", "synthetic-data"]
relations: [relates_to=products/TPRD-0001, relates_to=terpenes/TTRP-0005, relates_to=terpenes/TTRP-0007, relates_to=terpenes/TTRP-0004, relates_to=cultivars/TCUL-0001, relates_to=contaminants/TCNT-0007, relates_to=contaminants/TCNT-0003]
summary: Illustrative sample certificate of analysis record (demonstration) showing the archive's COA format with sample data, including ND, <LOQ, missing, and not-tested qualifier rows.
---

# Sample COA Report: Buckeye Relief Blue Dream #123

{{include includes/demo-sample-record-warning.md}}

{{include includes/unavailable-report-disclosure.md}}

> [!WARNING]
> **DEMONSTRATION / SYNTHETIC DATA.** This record is a synthetic fixture built to exercise the archive's COA data model
> (see `docs/coa-data-model.md` in the repository root). The laboratory name, producer, batch identifier, cultivar
> claim, and every quantitative value below are **illustrative sample placeholders** — they are not a verified laboratory
> report and must never be presented as real evidence for any product, batch, or cultivar.

## Certificate Header

| Field | Value |
| --- | --- |
| Testing Laboratory | North Coast Testing Laboratories *(sample placeholder)* |
| Producer | Buckeye Relief *(sample placeholder)* |
| Product | Blue Dream Dried Flower (2.83g) *(sample placeholder)* |
| Batch / Lot ID | BR-BD-20260315-123 *(sample placeholder identifier, not a real lot)* |
| Lot Number | LOT-2026-0315-AB *(sample placeholder)* |
| Sample ID | S-2026-0315-0042 *(sample placeholder)* |
| Test Date | 2026-03-15 *(sample placeholder)* |
| Jurisdiction | OH *(sample placeholder)* |
| Test Panels | Cannabinoid, Terpene, Contaminant *(sample placeholder)* |

## Cultivar Claim (Demonstration)

| Claim field | Value |
| --- | --- |
| Claimed label (as printed) | Blue Dream |
| Resolution | Unresolved (demonstration) |
| Canonical cultivar record | [Blue Dream Cultivar Page](../cultivars/TCUL-0001.html) (`cultivars/TCUL-0001`) |

The label "Blue Dream" is the **identity claimed for this batch**, not a measurement. In this demonstration record the
claim is left unresolved: resolving it to a canonical cultivar is a separate act with an explicit confidence grade
(`resolved` / `tentative` / `ambiguous` / `unresolved`), and the model never attaches chemistry to a cultivar name.
None of the numbers on this page describe "Blue Dream" as a cultivar — they describe this one synthetic batch.

## Quantitative Terpene Measurements (sample)

| Terpene Compound | Concentration (mg/g) | Percent by Weight (%) | Status |
| --- | --- | --- | --- |
| [β-Myrcene](../terpenes/TTRP-0005.html) | 8.45 mg/g | 0.845 % | Detected (Dominant) |
| [α-Pinene](../terpenes/alpha-pinene.md) | 3.12 mg/g | 0.312 % | Detected |
| [D-Limonene](../terpenes/TTRP-0007.html) | 2.80 mg/g | 0.280 % | Detected |
| [β-Caryophyllene](../terpenes/beta-caryophyllene.md) | 2.15 mg/g | 0.215 % | Detected |
| Total Terpenes | 18.70 mg/g | 1.870 % | **Calculated** (sum of the measured rows above) |

All terpene concentrations are reported as measured values in mass-per-mass units (mg/g). The "Total Terpenes" row is a
**calculated** sum of the individually measured terpenes listed above — it is a report-derived quantity, not a separate
chemical compound.

## Quantitative Cannabinoid Measurements (sample)

| Cannabinoid | Concentration (mg/g) | Percent by Weight (%) |
| --- | --- | --- |
| THCA | 242.0 mg/g | 24.20 % |
| Δ9-THC | 5.2 mg/g | 0.52 % |
| CBGA | 8.1 mg/g | 0.81 % |
| Total Potential THC (calculated) | 217.4 mg/g (Decarb Equivalent) | 21.74 % |

> [!NOTE]
> **Measured vs calculated.** THCA, Δ9-THC, and CBGA are reported as individually measured values. The "Total Potential THC (calculated)" row uses the decarboxylation conversion formula Δ9-THC + (THCA × 0.877), i.e. 5.2 + (242.0 × 0.877) = 217.4 mg/g. It estimates potential THC after thermal decarboxylation; it is not total cannabinoids and is not a directly measured compound. The model retains the formula alongside the row; acid and neutral cannabinoids (THCA vs Δ9-THC) are never collapsed into one value.

## Contaminant & Pesticide Panel (sample)

| Analyte | Result | Status / Qualifier | Note |
| --- | --- | --- | --- |
| [Lead (Pb)](../contaminants/TCNT-0007.html) | ND | **Not Detected** | Below the laboratory's detection capability; recorded as `nd`, never as zero |
| [Ochratoxin A](../contaminants/TCNT-0003.html) | &lt;LOQ | **Below Limit of Quantitation** | Reporting limit 5 ppb; recorded as `below_loq`, never as zero |
| Bifenthrin | *(blank)* | **Missing** | Analyte listed in the source panel excerpt but the result field is blank; recorded as `missing` |
| Spinosad | — | **Not Tested** | Absent from this panel; recorded as `not_tested` — absence of a result is not evidence of absence |

> [!IMPORTANT]
> **Qualifier semantics (demonstration).** `ND`, `<LOQ`, blank, `0.0`, and "not tested" are five different facts. None
> of them may be converted to zero, and a missing analyte is never inferred to be "not detected". This panel exercises
> those distinctions exactly as the model's result states (`nd`, `below_loq`, `missing`, `not_tested`) define them.

## Source / Provenance (Placeholder)

| Field | Value |
| --- | --- |
| Source URL | `https://example.com/coas/BR-BD-20260315-123.pdf` *(placeholder — not a real document)* |
| Retrieval date | 2026-03-16 *(placeholder)* |
| Document hash | `sha256:<placeholder — 64 hex chars when a real artifact is archived>` |
| Upstream record id | `example-coa:BR-BD-20260315-123` *(placeholder)* |
| Parser / import version | `coa-demo-fixture/1.0` |

Every real observation in the archive must trace to a source: `AnalyteResult → LabReport → source document / official
endpoint → retrieval metadata`. This demonstration record's provenance fields are **placeholders**; they exist to show
the shape of the provenance chain, not to assert that the source above exists.

## Related Graph Connections

- **Associated Commercial Product**: [Buckeye Relief Blue Dream Flower (sample record)](../products/TPRD-0001.html)
- **Genetic Cultivar Overview**: [Blue Dream Cultivar Page](../cultivars/TCUL-0001.html)
- **Compound records referenced by this report**: [Lead](../contaminants/TCNT-0007.html), [Ochratoxin A](../contaminants/TCNT-0003.html), [β-Myrcene](../terpenes/TTRP-0005.html), [D-Limonene](../terpenes/TTRP-0007.html)
