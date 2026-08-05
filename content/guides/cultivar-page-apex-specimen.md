---
id: guides/TGDE-0002
title: "Cultivar Page Apex Specimen"
parent: guides
status: published
tags: ["guide", "specimen", "apex", "formatting", "boris"]
relations: [relates_to=cultivars/TCUL-0001, relates_to=terpenes/TTRP-0005]
summary: Comprehensive feature specimen exercising Boris markdown extensions, includes, callouts, footnotes, tables, and wiki-links.
---

# Cultivar Page Apex Specimen

{{include includes/cultivar-identity-warning.md}}

{{include includes/first-party-provenance-warning.md}}

## Overview & Demonstration Scope

This page serves as an intentionally overstuffed Apex Markdown specimen, validating formatting capabilities across Boris compilation targets.

> [!IMPORTANT]
> The numeric values used below are **illustrative sample data** for demonstrating formatting and the Total THC calculation. They do not describe a verified real-world batch.

## Formatting Feature Demonstration

### GFM Callouts

> [!NOTE]
> Standard informational callout for secondary botanical context.

> [!TIP]
> Operational tip: Maintain thermal convection airflow between 180 °C and 200 °C for optimal terpene preservation.

> [!IMPORTANT]
> COA values are batch-specific. Always cross-reference batch lot numbers.

> [!WARNING]
> Do not heat plant material to pyrolytic combustion temperatures.

### Wiki-Links & Entity References

- Link to Cultivar: [[cultivars/TCUL-0001|Blue Dream]]
- Link to Terpene Node: [[terpenes/TTRP-0005|β-Myrcene]]
- Link to COA Guide: [[guides/TGDE-0005|Reading a Cannabis COA]]

### Advanced Tables & Subscript Math

| Chemical Parameter | Measured Value | Standard Formula | Unit |
| --- | --- | --- | --- |
| $\text{THCA}$ Mass | 242.0 mg/g | $\text{C}_{22}\text{H}_{30}\text{O}_4$ | mg/g |
| $\Delta^9\text{-THC}$ Mass | 5.2 mg/g | $\text{C}_{21}\text{H}_{30}\text{O}_2$ | mg/g |
| Total Active THC | 217.4 mg/g | $\Delta^9\text{-THC} + (\text{THCA} \times 0.877)$ | mg/g |

### Footnotes & Task Lists

- [x] Verified frontmatter schema compliance
- [x] Validated include file resolution
- [x] Audited markdown link targets
- [ ] Submitted batch laboratory report [^1]

[^1]: Laboratory Certificates of Analysis must be verified by accredited ISO 17025 testing facilities.
