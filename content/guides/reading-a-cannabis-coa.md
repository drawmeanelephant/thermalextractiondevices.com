---
id: guides/TGDE-0005
title: "Reading a Cannabis Certificate of Analysis"
parent: guides
status: published
tags: ["guide", "coa", "analytics", "compliance", "ohio"]
relations: [relates_to=lab-results/TLAB-0001]
summary: Step-by-step guide to interpreting laboratory Certificates of Analysis (COAs), active THC formulas, and contaminant panels.
---

# Reading a Cannabis Certificate of Analysis

## Key Sections of a COA

1. **Header & Chain of Custody**: Testing lab ISO 17025 certification, licensed producer, batch/lot number, sample weight, test date.
2. **Cannabinoid Profile**: HPLC quantitative mass percentages and decarb-adjusted totals.
3. **Terpene Profile**: GC-MS or GC-FID quantitative mass concentrations (mg/g or %).
4. **Contaminant Safety Panels**: Heavy metals, pesticides, mycotoxins, residual solvents, and microbials (Pass/Fail).

## Active THC Calculation (Ohio & Industry Standard)

Raw plant material contains non-psychoactive THCA (tetrahydrocannabinolic acid). Upon thermal extraction, THCA undergoes thermal decarboxylation, releasing carbon dioxide (CO<sub>2</sub>).

The molecular weight ratio yields the conversion factor:

`Total Active THC = Δ⁹-THC + (THCA × 0.877)`

### Example Calculation
If a COA reports:
- THCA: 24.2% (242.0 mg/g)
- Δ⁹-THC: 0.52% (5.2 mg/g)

`Total Active THC = 0.52 + (24.2 × 0.877) = 0.52 + 21.22 = 21.74%`

<Aside kind="note">

This worked example uses the same numeric values as the [Sample COA record (demonstration)](../lab-results/example-producer-blue-dream-batch-123.md) in this archive. Those figures are illustrative sample data used for teaching the calculation; they do not describe a verified real-world product.

</Aside>

## Units, LOD, and LOQ Handling

- **mg/g to Percent**: $10\text{ mg/g} = 1.0\%\text{ by weight}$.
- **LOD (Limit of Detection)**: Smallest concentration the lab instrument can detect.
- **LOQ (Limit of Quantitation)**: Smallest concentration the lab can accurately measure. Values below LOQ should be listed as `< LOQ` or *Trace*, not assumed zero.
