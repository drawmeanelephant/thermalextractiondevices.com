---
id: jurisdictions/TJUR-0063
title: "Switzerland (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "switzerland", "international", "regulatory", "deep-data-candidate"]
relations: []
summary: "Jurisdiction profile for Switzerland: federal pilot-trial framework for adult-use cannabis (BAG-authorized trials, ≈7 trials), medical cannabis via prescription, hemp <1% THC."
---

# Switzerland (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| Country | Switzerland |
| ISO country code | CH |
| National authorities | Federal Office of Public Health (BAG/FOPH); Swissmedic (medicines) |
| Official sources | https://www.bag.admin.ch/en/overview-of-authorised-pilot-trials-with-cannabis |
| Last verified | 2026-08-09 |

## Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Not legal generally (small-quantity enforcement discretion varies by canton) |
| Adult-use cultivation | Not legal generally |
| Adult-use commercial supply | Only within authorized scientific pilot trials (regulated sales to enrolled participants) |
| Medical access | Cannabis-based medicines by prescription (narcotics-law revision 2022; doctor prescription without special authorization since 2024 under the revised framework) |
| Pharmaceutical cannabinoid access | Swissmedic-registered cannabis-based medicines |
| Home cultivation | Prohibited |
| Import/export | Regulated; import of medical cannabis per narcotics law |
| Hemp relationship | Hemp ≤1.0% THC not subject to narcotics law (low-THC products legal) |

## Regulatory Overview

Switzerland has authorized **scientific pilot trials** for regulated adult-use cannabis under a 2021 legal amendment: the Federal Office of Public Health has approved about seven trials (Zürich's Züri Can is the flagship; ≈10,400 adults enrolled across trials as of mid-2025). Zürich's trial was extended to October 2028. Medical cannabis has been available by prescription under the 2022 narcotics-law revision. Hemp with ≤1.0% THC is not regulated as a narcotic.

## Regulatory History

- **2011**: Narcotics Act revision (cannabis pilot-trial provision).
- **2021**: Implementing ordinance (Verordnung Pilotversuche) permits authorized trials.
- **2022**: Narcotics-law revision allows medical cannabis by prescription.
- **2023–2026**: Trials running in Basel, Zürich, Bern, Geneva, and others; Zürich extended to October 2028.

## Licensing Structure

- Pilot trials: canton-approved, BAG-authorized; sales through pharmacies/designated outlets to enrolled adult participants with quantity/quality limits.
- Medical: prescribed cannabis medicines from licensed pharmacies; no producer licensing register made public in the pilot context.

## Laboratory / Quality Framework

- Pilot-trial product quality is monitored per trial protocols (analysis, contaminant limits).
- Medical cannabis follows Swissmedic pharmaceutical quality standards.
- Trial evaluations are published; no public per-batch COA database located.

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | partial | BAG trial overview page | no | Trial list published; no API |
| Testing-laboratory registry | no public source located | — | — | No distinct public list located |
| Laboratory testing rules | yes | Pilot-trial ordinance + trial protocols | no | Codified requirements |
| Contaminant/action limits | yes | Trial protocols | no | Set in standards |
| Recalls/advisories | no public source located | — | — | No structured feed located |
| Product/package identifiers | no public source located | — | — | Trial-internal tracking |
| COAs/batch results | no public source located | — | — | Not public |
| Sales data | partial | Trial evaluation reports | partial | Züri Can reported ≈88,000 transactions / ≈750 kg |
| Open-data downloads | no public source located | — | — | No cannabis open-data portal located |

## Future Ingestion Opportunities

1. Trial evaluation reports (BAG/Züri Can) — aggregate records and comparative data for pilot frameworks.
2. Monitor federal legalization referendum/political developments (2026–2028) — high-volatility page for the refresh queue.

## Sources & Provenance

- **Statutory framework**: Narcotics Act (BetmG) + pilot-trial ordinance (2021/2022).
- **Regulator**: Federal Office of Public Health — https://www.bag.admin.ch/en/overview-of-authorised-pilot-trials-with-cannabis
- **Trial extension**: Zürich's Züri Can extended to October 2028 (2026).
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Switzerland. The page is discoverable from the [Jurisdictions index](../jurisdictions.md).
