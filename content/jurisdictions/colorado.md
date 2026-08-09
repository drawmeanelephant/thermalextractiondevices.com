---
id: jurisdictions/TJUR-0006
title: "Colorado (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "colorado", "united-states", "regulatory", "deep-data-candidate"]
relations: []
summary: "Jurisdiction profile for Colorado: first regulated adult-use market (MED), mature Socrata open-data surface for sales/tax, METRC traceability, no public per-batch chemistry."
---

# Colorado (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| State | Colorado (CO) |
| Country | United States |
| Primary cannabis authority | Marijuana Enforcement Division (MED), Colorado Department of Revenue |
| Official website | https://med.colorado.gov/ |
| Open-data portal | https://data.colorado.gov |
| Last verified | 2026-08-09 |

## Current Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Permitted (21+; up to 2 oz in public, more at home) |
| Adult-use commercial sales | Operational (first retail market in the U.S., January 2014) |
| Medical cannabis | Regulated program (Amendment 20, 2000) |
| Home cultivation | Permitted (up to 6 plants per person, 3 mature; 12 per household) |
| Hemp relationship | Hemp regulated separately under the Colorado Department of Agriculture hemp program |

## Regulatory Overview

Colorado was the first U.S. state to regulate adult-use cannabis retail (Amendment 64, 2012; sales from January 2014). The Marijuana Enforcement Division (MED) of the Department of Revenue licenses cultivation, product manufacturing, testing facilities, and retail. The medical program dates to 2000 (Amendment 20). Traceability runs through METRC.

## Regulator History

- **2000**: Amendment 20 establishes the medical cannabis program.
- **2012**: Amendment 64 legalizes adult use; the MED is established within the Department of Revenue.
- **2014**: First adult-use retail sales in the United States (January 2014).
- **Present**: MED publishes rules (1 CCR 212-3) and a quarterly market dashboard derived from METRC.

## Licensing Categories

Cultivation (A–E tiers), product manufacturing (infused products), testing facility, retail store, and transporter (with dual-license options). The licensee lookup tool publishes licensed facilities.

## Testing Laboratory Framework

- **Rules**: Regulated Marijuana Rules, 1 CCR 212-3; laboratory testing requirements codified by the MED.
- **Contaminant limits**: Set in 1 CCR 212-3 testing panels (microbiological, mycotoxins, pesticides, heavy metals, residual solvents, moisture/water activity, potency).
- **Lab registry**: MED licensed facilities list / licensee lookup.
- **Public results**: No public per-batch numeric results; the MED publishes aggregate market data only.

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | yes | MED Licensed Facilities + Licensee Lookup; data.colorado.gov view `93ae-ftjz` (href view) | partial | Socrata view is an href link into the MED lookup; no full-table dump |
| Testing-laboratory registry | partial | MED licensed facilities list | no | Part of license records |
| Laboratory testing rules | yes | 1 CCR 212-3 | no | Regulated Marijuana Rules |
| Contaminant/action limits | yes | 1 CCR 212-3 panels | no | Testing panels in regulation |
| Recalls/advisories | partial | MED enforcement + Final Administrative Enforcement Actions | no | No structured recall feed found |
| Product/package identifiers | partial | METRC-based | no | Traceability only; no public registry |
| COAs/batch results | no public source located | — | — | Per-batch results are not public |
| Sales data | yes | data.colorado.gov: Sales by County `j7a3-jgd3`, Sales Revenue `p6y8-s74x`, Tax Revenue `v9m8-x8dh` / `qvd3-njpu`, Tax & Fee Revenue `3sm5-jtur` | yes | Socrata SODA + CSV exports; monthly, 2014–present |
| Plant inventory | partial | METRC-derived quarterly dashboard | no | Aggregate-only market update |
| Open-data downloads | yes | data.colorado.gov | yes | Socrata SODA API |
| Traceability | yes | METRC | no | Seed-to-sale |

## Recalls / Advisories

MED publishes enforcement activity and final administrative enforcement actions. No structured machine-readable recall feed was located (verified 2026-08-08).

## Data-Ingestion Opportunities

1. **SocrataSource adapter** for data.colorado.gov (sales/tax/revenue datasets — cheapest high-value ingestion).
2. License registry via MED licensee lookup; the `93ae-ftjz` Socrata view is an href view that must be resolved to the lookup tool, not treated as tabular data.
3. Quarterly METRC-derived market dashboard as aggregate signal (dashboard-only; not counted as a machine-readable source).

## Sources & Provenance

- **Statutory framework**: Amendment 64 (2012, adult use); Amendment 20 (2000, medical); Regulated Marijuana Rules 1 CCR 212-3.
- **Regulator**: MED — https://med.colorado.gov/
- **Open data**: data.colorado.gov (views verified live 2026-08-08; see `docs/state-expansion-roadmap.md` §3.2).
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Colorado. Future dataset/license records generated by a Colorado adapter should add `relates_to=jurisdictions/TJUR-0006` per the California pattern.
