---
id: jurisdictions/TJUR-0048
title: "Washington (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "washington", "united-states", "regulatory"]
relations: []
summary: "Jurisdiction profile for the State of Washington: adult-use and medical programs under the LCB, rich dated XLSX lists, no public per-batch chemistry, and an archive-only caution around commercial-use requests for certain public-record lists."
---

# Washington (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| State | Washington (WA) |
| Country | United States |
| Primary cannabis authority | Washington State Liquor and Cannabis Board (LCB) |
| Official website | https://lcb.wa.gov/ |
| Last verified | 2026-08-09 |

## Current Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession | Permitted (21+; up to 1 oz) |
| Adult-use commercial sales | Operational (since July 2014) |
| Medical cannabis | Regulated program (1998); integrated into the LCB framework |
| Home cultivation | Prohibited |
| Hemp relationship | Hemp regulated under the 2018 Farm Bill framework |

## Regulatory Overview

Washington legalized adult use under Initiative 502 (2012), with retail sales from July 2014, regulated by the Liquor and Cannabis Board. The LCB publishes dated XLSX lists (license applicants, approved testing labs, sales activity, enforcement, compliance checks) with history back to FY2015. No public per-batch chemistry is published. **RCW 42.56.070(8) addresses requests for lists of individuals for commercial purposes, so this archive treats Washington list ingestion as legally sensitive and archive-only until the publication posture is cleared.**

## Data Surface

| Data surface | Available? | Official source | Machine-readable? | Notes |
| --- | --- | --- | --- | --- |
| License registry | yes | LCB Frequently Requested Lists (`CannabisApplicants<date>.xlsx`) | partial | Dated XLSX, active + pending-issued |
| Testing-laboratory registry | yes | `Lab-List-<date>.xlsx`; WSDA Cannabis Lab Analysis Program | partial | Dated XLSX of approved labs |
| Laboratory testing rules | yes | WAC 314-55-102/109 | no | Testing + quarantine rules |
| Contaminant/action limits | yes | WAC 314-55 | no | Set in regulation |
| Recalls/advisories | partial | LCB press releases + public health notices | no | No structured feed found |
| Product/package identifiers | partial | Approved infused products list | partial | Published lists; no per-batch public data |
| COAs/batch results | no public source located | — | — | Labs submit to CCRS for LCB review; not public |
| Sales data | yes | Sales activity by license number; FY2015–FY2025 sales & excise tax by county | partial | Dated XLSX lists |
| Plant inventory | partial | Enforcement/visits lists | no | Not published as open data |
| Open-data downloads | partial | data.wa.gov (LCB Cannabis Renewal `brpd-b6zd`, Local Authority Letters `vgcw-qfjm`) | yes | Socrata; main lists are page-discovered XLSX |
| Traceability | yes | Leaf Data Systems / CCRS | no | Traceability via LCB system |

## Data-Ingestion Notes

- Richest license/lab/enforcement/sales **lists** (FY2015+ history) but XLSX-only, no API, no public results.
- **Legal gate**: RCW 42.56.070(8) is narrower than a blanket ban on all public records, but it does restrict commercial-purpose requests for certain lists of individuals; keep WA handling archive-only until publication use is cleared.

## Sources & Provenance

- **Statutory framework**: Initiative 502 (2012, adult use); medical program (1998); WAC 314-55.
- **Regulator**: Washington State Liquor and Cannabis Board — https://lcb.wa.gov/
- **Frequently requested lists**: https://lcb.wa.gov/records/frequently-requested-lists (dated XLSX; verified 2026-08-08, `docs/state-expansion-roadmap.md` §3.6).
- **Retrieval date**: 2026-08-09

## Graph Connections

No existing repository entities are linked to Washington. The page is discoverable from the [Jurisdictions index](../jurisdictions.md).
