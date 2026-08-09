---
id: jurisdictions/TJUR-0029
title: "Nevada (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "nevada", "united-states", "regulatory", "deep-data-candidate"]
relations: []
summary: "Jurisdiction profile for Nevada: Cannabis Compliance Board (CCB), the only remaining U.S. state after Massachusetts publishing public per-batch numeric lab results (2020–present monthly archive)."
---

# Nevada (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| State | Nevada (NV) |
| Country | United States |
| Primary cannabis authority | Nevada Cannabis Compliance Board (CCB) |
| Official website | https://ccb.nv.gov/ |
| Lab data library | https://ccb.nv.gov/lab-library/ |
| Last verified | 2026-08-09 |

## Current Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Permitted (21+; up to 1 oz flower / ⅛ oz concentrate) |
| Adult-use commercial sales | Operational (since July 2017) |
| Medical cannabis | Regulated program (2000) |
| Home cultivation | Permitted (up to 6 plants per person, 12 per household; within distance restrictions) |
| Hemp relationship | Hemp regulated under the 2018 Farm Bill framework |

## Regulatory Overview

Nevada legalized adult use in 2016 (Question 2), with retail sales from July 2017. The Cannabis Compliance Board regulates the industry under NRS 678C and NAC Chapter 453A. Nevada is the **highest-ranked deep-ingestion candidate** in this repository's state roadmap: it publishes public per-batch numeric test results from 2020 through the previous month in monthly and full-year ZIP archives of CSVs, plus machine-readable advisory posts.

## Regulator History

- **2000**: Medical marijuana program established (Question 9).
- **2016**: Question 2 legalizes adult use; retail begins July 2017.
- **2019**: Cannabis Compliance Board established (AB 533).
- **2026**: Regulatory package R152-24-RP1 adopted (June 2026); NAC Chapter 453A remains the testing/regulation framework.

## Licensing Categories

Cultivation, production (manufacturing), dispensary, distribution, testing laboratory, and cannabis consumption lounge licenses under the CCB.

## Testing Laboratory Framework

- **Rules**: NAC Chapter 453A; 2026 regulatory package R152-24-RP1 (adopted 2026-06-18).
- **Contaminant limits**: NAC 453A panels.
- **Lab registry**: `Testing Facility Name` field in the lab data; approved labs appear in the Metrc extracts.
- **Public results**: Per-sample `PackageLabSampleId`, `PackageLabel`, product category, quantity/UOM, test type, pass/fail, numeric result — 14-column schema documented in `READ_ME_FIRST_LAB_DATA.xlsx`.

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | yes | CCB License Search + List of Licensees | partial | Searchable (~4,617 records); interactive; full-extract export not confirmed |
| Testing-laboratory registry | yes | Lab data `Testing Facility Name` field | yes | In the Metrc lab extracts |
| Laboratory testing rules | yes | NAC 453A | no | Codified testing regulations |
| Contaminant/action limits | yes | NAC 453A panels | no | Set in regulation |
| Recalls/advisories | yes | CCB Public Health & Safety Bulletins | yes | Machine-readable via WordPress REST API (`/wp-json/wp/v2/posts?search=bulletin`) |
| Product/package identifiers | yes | Lab Library extracts (`PackageLabSampleId`, `PackageLabel`) | yes | Per-package identifiers |
| COAs/batch results | yes | Lab Library (2020 → previous month, monthly + full-year ZIPs of CSVs) | yes | Public per-batch numeric results — the project's primary chemistry value |
| Sales data | no public source located | — | — | Not published as open data |
| Plant inventory | partial | License records | no | Not published as open data |
| Open-data downloads | yes | https://ccb.nv.gov/lab-library/ | yes | Manual ZIP downloads behind dated URLs; no SODA |
| Traceability | yes | METRC | no | Seed-to-sale (catalog.metrc.com reference) |

## Recalls / Advisories

CCB publishes "Public Health and Safety Bulletins" / advisories (2023–present verified) with an amended 2025 bulletin dated 2025-12-12. Posts are machine-readable via the site's WordPress REST API.

## Data-Ingestion Opportunities

1. **Lab Library monthly ZIPs** → lab-results + contaminant entities against the batch/laboratory measurement model (`tests/test_coa_model.py`). Natural key: `PackageLabSampleId`.
2. **License registry snapshot** (`list-of-licensees` / `license-search`) — keep owner names/addresses out of content (privacy gate).
3. **Bulletins via `wp-json`** → advisory entities, preserving the regulator's "bulletin" terminology (never relabel as recall).
4. Wave-1 scope: 2026 monthly files; backfill 2020–2025 in a second pass (per `docs/state-expansion-roadmap.md` §5).

## Sources & Provenance

- **Statutory framework**: NRS 678C; NAC Chapter 453A; R152-24-RP1 (adopted 2026-06-18).
- **Regulator**: Nevada Cannabis Compliance Board — https://ccb.nv.gov/
- **Lab library**: https://ccb.nv.gov/lab-library/ (verified 2026-08-08; `docs/state-expansion-roadmap.md` §3.1).
- **Bulletins API**: https://ccb.nv.gov/wp-json/wp/v2/posts?search=bulletin (verified live 2026-08-08).
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Nevada. Future lab-result, contaminant, advisory, and license records generated by a Nevada adapter should add `relates_to=jurisdictions/TJUR-0029`.
