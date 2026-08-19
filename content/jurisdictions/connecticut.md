---
id: jurisdictions/TJUR-0007
title: "Connecticut (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "connecticut", "united-states", "regulatory", "deep-data-candidate"]
relations: []
summary: "Jurisdiction profile for Connecticut: adult-use and medical programs under DCP, Socrata open data with a unique product-level chemistry registry including COA links."
---

# Connecticut (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| State | Connecticut (CT) |
| Country | United States |
| Primary cannabis authority | Connecticut Department of Consumer Protection (DCP) — Cannabis Program |
| Official website | https://portal.ct.gov/DCP |
| Open-data portal | https://data.ct.gov |
| Last verified | 2026-08-09 |

## Current Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Permitted (21+; up to 1.5 oz in public, more at home) |
| Adult-use commercial sales | Operational (since January 2023) |
| Medical cannabis | Regulated program (2012) |
| Home cultivation | Permitted (since July 1, 2023; up to 3 mature + 3 immature per person, 6 mature per household) |
| Hemp relationship | Hemp regulated separately; consumable hemp product rules tracked by DCP |

## Regulatory Overview

Connecticut legalized medical cannabis in 2012 and adult use in 2021 (HB 6501), with adult-use retail beginning January 2023. The Department of Consumer Protection licenses cultivators, producers, retailers, and testing laboratories. Connecticut is notable for publishing **product-level chemistry** — analyte and terpene values with certificate-of-analysis (COA) links — on its open-data portal.

## Regulator History

- **2012**: Medical marijuana program established (Public Act 12-55), administered by DCP.
- **2021**: HB 6501 legalizes adult use; establishes the Cannabis Regulatory Authority transition (DCP retains administration).
- **2023**: Adult-use retail launches (January 2023); home cultivation permitted from July 2023.
- **Present**: DCP continues rulemaking; cannabis product registry and sales datasets published on data.ct.gov.

## Licensing Categories

Cultivator, producer (manufacturer), retailer, micro-cultivator, delivery, hybrid retailer, and testing laboratory licenses; social-equity program provisions.

## Testing Laboratory Framework

- **Rules**: Connecticut cannabis testing regulations administered by DCP.
- **Contaminant limits**: DCP regulations (microbiological, mycotoxins, pesticides, heavy metals, residual solvents, potency).
- **Lab registry**: No distinct public testing-lab registry found.
- **Public results**: Product-level analyte/terpene values plus COA document links in the Cannabis Product Registry.

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | partial | data.ct.gov: Cannabis Applications `bqby-dyzr`; lottery/application reports `w85q-8cfm`, `y64a-qj22`, `7kwc-wvc8` | yes | Socrata SODA |
| Testing-laboratory registry | no public source located | — | — | Not found as a distinct public list |
| Laboratory testing rules | yes | DCP regulations | no | Testing rules in regulation |
| Contaminant/action limits | yes | DCP regulations | no | Panels in regulation |
| Recalls/advisories | partial | DCP consumer alerts | no | Not structured |
| Product/package identifiers | yes | Cannabis Product Registry `egd5-wb6r` | yes | ≈35k rows (verified): brand, dosage form, producer, THC/THCA/CBD/CBDA, terpenes |
| COAs/batch results | partial | Registry `lab_analysis` COA URL field | yes | COA documents are GUID links on elicense.ct.gov (link-stability caveat) |
| Sales data | yes | data.ct.gov: monthly/weekly sales `f382-bnu5`, `ucaf-96h6`; price per gram `ttwq-xhyz`; product-type sales `twgv-a8qu`, `jyg4-yu7v`; avg product price `crdh-m57i`; products sold `t3s5-39as`; cannabis tax `jey2-vq68` | yes | Socrata SODA |
| Open-data downloads | yes | data.ct.gov | yes | Socrata SODA API + CSV |
| Traceability | yes | METRC | no | Seed-to-sale |

## Data-Ingestion Opportunities

1. **Cannabis Product Registry** (`egd5-wb6r`): unique product-level chemistry (analytes + terpenes) with COA links — highest chemistry value per implementation dollar among candidates reviewed in `docs/state-expansion-roadmap.md`.
2. **Sales/price datasets**: weekly/monthly updates on Socrata.
3. **COA link handling**: GUID URLs on elicense.ct.gov are treated as unstable link targets; do not hotlink images into content.

## Sources & Provenance

- **Statutory framework**: Public Act 12-55 (2012, medical); HB 6501 (2021, adult use); DCP regulations.
- **Regulator**: Connecticut DCP — https://portal.ct.gov/DCP
- **Open data**: data.ct.gov (views verified live 2026-08-08; see `docs/state-expansion-roadmap.md` §3.3).
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Connecticut. Future dataset records generated by a Connecticut adapter should add `relates_to=jurisdictions/TJUR-0007`.
