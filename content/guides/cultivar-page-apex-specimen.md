---
id: guides/TGDE-0002
title: "Cultivar Page Apex Specimen"
parent: guides
status: published
tags: ["guide", "specimen", "formatting", "boris"]
relations: [relates_to=cultivars/TCUL-0001, relates_to=terpenes/TTRP-0005]
summary: Formatting specimen exercising Boris includes, Aside components, footnotes, tables, and wiki-links on the Oliver rendering path.
---

# Cultivar Page Apex Specimen

{{include includes/cultivar-identity-warning.md}}

{{include includes/first-party-provenance-warning.md}}

## Overview & Demonstration Scope

This page is an intentionally overstuffed formatting specimen, validating what Boris
actually publishes across its compilation targets. It was written against the retired
ApexMarkdown renderer; the constructs Apex alone supported (math, checkbox task lists,
callout extensions) have been rewritten as renderer-independent markup, so the page now
exercises the Oliver rendering path. It still needs a deliberate pass to cover Oliver's
own feature set rather than Apex's.

<Aside kind="info">

The numeric values used below are **illustrative sample data** for demonstrating formatting and the Total THC calculation. They do not describe a verified real-world batch.

</Aside>

## Formatting Feature Demonstration

### GFM Callouts

<Aside kind="note">

Standard informational callout for secondary botanical context.

</Aside>

<Aside kind="tip">

Formatting specimen placeholder: no operating temperature, airflow, or terpene-preservation recommendation is provided by this demonstration page.

</Aside>

<Aside kind="info">

COA values are batch-specific. Always cross-reference batch lot numbers.

</Aside>

<Aside kind="warning">

Do not heat plant material to pyrolytic combustion temperatures.

</Aside>

### Wiki-Links & Entity References

- Link to Cultivar: [[cultivars/TCUL-0001|Blue Dream]]
- Link to Terpene Node: [[terpenes/TTRP-0005|β-Myrcene]]
- Link to COA Guide: [[guides/TGDE-0005|Reading a Cannabis COA]]

### Advanced Tables & Subscript Math

| Chemical Parameter | Measured Value | Standard Formula | Unit |
| --- | --- | --- | --- |
| THCA Mass | 242.0 mg/g | C<sub>22</sub>H<sub>30</sub>O<sub>4</sub> | mg/g |
| Δ⁹-THC Mass | 5.2 mg/g | C<sub>21</sub>H<sub>30</sub>O<sub>2</sub> | mg/g |
| Total Active THC | 217.4 mg/g | `Δ⁹-THC + (THCA × 0.877)` | mg/g |

### Footnotes & Status Lists

- **Done** — Verified frontmatter schema compliance
- **Done** — Validated include file resolution
- **Done** — Audited markdown link targets
- **Outstanding** — Submitted batch laboratory report [^1]

[^1]: Laboratory Certificates of Analysis must be verified by accredited ISO 17025 testing facilities.
