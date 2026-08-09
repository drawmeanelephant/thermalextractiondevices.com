---
id: jurisdictions/TJUR-0058
title: "Germany (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "germany", "international", "regulatory", "deep-data-candidate"]
relations: []
summary: "Jurisdiction profile for Germany: Cannabis Act (CanG, 2024) legalizes personal possession/cultivation and cultivation associations; medical cannabis under pharmaceutical law; no commercial adult-use sales."
---

# Germany (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| Country | Germany |
| ISO country code | DE |
| National authorities | Bundesministerium für Gesundheit (BMG); Bundesinstitut für Arzneimittel und Medizinprodukte (BfArM, medical cannabis); BLE (cultivation licensing) |
| Official sources | https://www.bundesgesundheitsministerium.de/en/themen/cannabis/faq-cannabis-act ; https://www.bfarm.de/ |
| Last verified | 2026-08-09 |

## Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Permitted (adults 18+; up to 25 g in public, 50 g at home) |
| Adult-use cultivation | Home cultivation permitted (up to 3 plants); non-commercial cultivation associations from July 2024 |
| Adult-use commercial supply | Not permitted (no commercial adult-use sales) |
| Medical access | Medical cannabis available by prescription; reimbursable under statutory health insurance in defined cases |
| Pharmaceutical cannabinoid access | Regulated drug products (e.g., dronabinol, Sativex, Epidyolex) under pharmaceutical law |
| Home cultivation | Permitted (3 plants per adult) |
| Import/export | Medical cannabis import regulated (BfArM tenders historically; now part of medical supply chain) |

## Regulatory Overview

Germany's Cannabis Act (CanG) took effect April 1, 2024: possession and home cultivation were legalized, and non-commercial cultivation associations ("Anbauvereinigungen") began operating in July 2024. As of mid-2026, ~440–455 cultivation associations have been approved; the 2025 coalition agreement contained no specific repeal plan and the Act remains in force. Medical cannabis has been legal since 2017 and was removed from the Narcotics Act (BtMG) by the 2024 reform, with quality governed by pharmaceutical/GMP requirements.

## Licensing Structure

- **Cultivation associations**: non-commercial, member-based, licensed by state authorities; ~500 mature total (approx. 443–455 approved by mid-2026).
- **Medical production**: licensed cultivation/manufacturing under GMP; BfArM registration of medical cannabis qualities.
- No commercial adult-use retail licences exist.

## Laboratory / Quality Framework

- **Medical cannabis**: tested to pharmaceutical quality standards (GMP; European Pharmacopoeia monographs apply to cannabinoid preparations), with mandatory quality controls per the German Medicines Act (AMG).
- **Adult-use (associations)**: CanG requires defined quality controls; not equivalent to a U.S. state compliance-lab program — do not conflate the two systems.
- **Public data**: No public per-batch COA database; BfArM publishes medical cannabis quality information.

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | partial | State authorities' cultivation-association approvals | no | Approval counts published; no national registry located |
| Testing-laboratory registry | partial | BfArM/state records | no | No distinct public list located |
| Laboratory testing rules | yes | CanG + AMG/GMP requirements | no | Codified requirements |
| Contaminant/action limits | yes | Pharmacopoeial monographs + CanG | no | Set in standards |
| Recalls/advisories | partial | BfArM recalls and safety notices | partial | Medicines recalls database covers medical products |
| Product/package identifiers | partial | BfArM medical cannabis qualities | partial | Registered qualities published |
| COAs/batch results | no public source located | — | — | No public batch database |
| Sales data | partial | Official statistics (Destatis/medical billing data) | partial | Aggregate only |
| Open-data downloads | no public source located | — | — | No cannabis open-data portal located |

## Future Ingestion Opportunities

1. Cultivation-association approval statistics (state authorities) — aggregate records.
2. BfArM medical cannabis quality list — reference data.
3. Monitor CanG stability: the 2025–26 political debate around revision/repeal is an active risk; the refresh queue should rank Germany as high-volatility.

## Sources & Provenance

- **Statutory framework**: Cannabisgesetz (CanG), in force April 1, 2024; BtMG reform; AMG/GMP for medical products.
- **Government**: BMG FAQ — https://www.bundesgesundheitsministerium.de/en/themen/cannabis/faq-cannabis-act
- **Medical cannabis**: BfArM — https://www.bfarm.de/
- **Association counts**: ~443–455 approved as of June 2026 (secondary reporting; verify against state authorities before reuse).
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Germany. The page is discoverable from the [Jurisdictions index](../jurisdictions.md).
