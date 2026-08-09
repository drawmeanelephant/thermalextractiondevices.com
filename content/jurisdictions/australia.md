---
id: jurisdictions/TJUR-0067
title: "Australia (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "australia", "international", "regulatory", "deep-data-candidate"]
relations: []
summary: "Jurisdiction profile for Australia: nationally regulated medicinal cannabis (TGA/ODC), state-level personal-use differences (ACT exemption), GMP/analytical testing framework, no adult-use program."
---

# Australia (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| Country | Australia |
| ISO country code | AU |
| National authorities | Therapeutic Goods Administration (TGA); Office of Drug Control (ODC); state/territory health departments |
| Official sources | https://www.tga.gov.au/resources/explore-topic/medicinal-cannabis-hub ; https://www.odc.gov.au/medicinal-cannabis |
| Last verified | 2026-08-09 |

## Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Prohibited federally; ACT allows limited personal use (up to 50 g; 2 plants per person, 4 per household); WA personal-use bill introduced 2026 (not enacted) |
| Adult-use cultivation | Prohibited federally (no personal cultivation support under the Act) |
| Adult-use commercial supply | Not legal |
| Medical access | Medicinal cannabis available by prescription via Special Access Scheme (SAS) and Authorised Prescriber (AP) pathways |
| Pharmaceutical cannabinoid access | TGA-regulated products (some registered; most accessed as unapproved products via SAS/AP) |
| Home cultivation | Prohibited federally (ACT personal-use exception) |
| Import/export | Import regulated by TGA (SAS/AP); cultivation/manufacture licensed by the ODC |

## Subnational Systems

Cannabis law is a **state/territory matter for personal use**, while medicinal cannabis is nationally regulated (TGA/ODC). Only the Australian Capital Territory has enacted a personal-use exemption; Western Australia's 2026 Misuse of Drugs Amendment (Lawful Personal Use of Cannabis) Bill was introduced but not enacted as of retrieval. Deeper subnational modeling is warranted for possession law variance.

## Regulatory Overview

Australia regulates medicinal cannabis nationally: the TGA oversees product access (SAS/AP pathways; a 2025 TGA inquiry reviewed unapproved-product use), and the Office of Drug Control licenses cultivation and manufacture under the Narcotic Drugs Act. GMP is required for commercial production; analytical testing labs must meet NATA/ISO 17025 standards. Adult use remains illegal federally.

## Licensing Structure

- **ODC licences/permits**: cultivation, production, research (Narcotic Drugs Act 1967); GMP compliance required.
- **TGA access**: SAS Category B and Authorised Prescriber schemes for patients.

## Laboratory / Quality Framework

- Products must meet TGA quality standards (GMP manufacturing; analytical testing to pharmacopoeial methods; ISO 17025 labs).
- No public per-batch COA database; adverse-event reporting flows to the TGA (27 voluntary cases reported in 2026 through July).

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | partial | ODC licensed cultivators/manufacturers | no | Published information; no API located |
| Testing-laboratory registry | partial | NATA-accredited lab directories | partial | NATA directory (generic, not cannabis-specific) |
| Laboratory testing rules | yes | TGA guidance + pharmacopoeial standards | no | Codified requirements |
| Contaminant/action limits | yes | TGA quality standards | no | Set in standards |
| Recalls/advisories | partial | TGA medicine recalls/alerts | yes | TGA recalls database is searchable |
| Product/package identifiers | partial | TGA ARTG (registered products) | yes | ARTG is a searchable register |
| COAs/batch results | no public source located | — | — | Not public |
| Sales data | partial | TGA/industry statistics | partial | Aggregate access statistics |
| Open-data downloads | partial | TGA ARTG data | partial | Register searchable; bulk formats limited |

## Future Ingestion Opportunities

1. TGA ARTG medicinal-cannabis entries → product/reference records.
2. TGA recalls/alerts → recall entities.
3. ODC licensing stats → aggregate records.
4. Monitor ACT personal-use framework and the WA bill — state-level divergence is an active policy area.

## Sources & Provenance

- **Statutory framework**: Narcotic Drugs Act 1967; Therapeutic Goods Act 1989; ACT Drugs of Dependence (Personal Cannabis Use) Amendment Act 2019 (effective January 2020).
- **TGA hub**: https://www.tga.gov.au/resources/explore-topic/medicinal-cannabis-hub
- **ODC**: https://www.odc.gov.au/medicinal-cannabis
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Australia. The page is discoverable from the [Jurisdictions index](../jurisdictions.md).
