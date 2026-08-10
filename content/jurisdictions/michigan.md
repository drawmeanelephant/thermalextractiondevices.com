---
id: jurisdictions/TJUR-0023
title: "Michigan (Jurisdiction Profile)"
parent: jurisdictions
status: published
tags: ["jurisdiction", "michigan", "united-states", "regulatory", "deep-ingested"]
relations: [relates_to=datasets/TDTS-0023, relates_to=datasets/TDTS-0024, relates_to=datasets/TDTS-0025, relates_to=datasets/TDTS-0026, relates_to=datasets/TDTS-0027, relates_to=requirements/TREQ-0003, relates_to=testing-laboratories/TSTL-0029, relates_to=testing-laboratories/TSTL-0030, relates_to=testing-laboratories/TSTL-0031]
---

# Michigan (Jurisdiction Profile)

{{include includes/jurisdiction-legal-disclaimer.md}}

Michigan is the project's third deeply implemented U.S. jurisdiction. Its public
evidence surface is strong for rules, testing guidance, recalls, enforcement,
and aggregate reports, but materially weaker than Massachusetts for machine-
readable licenses and batch-level chemistry.

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| State | Michigan (MI) |
| Primary regulator | [Cannabis Regulatory Agency (CRA)](https://www.michigan.gov/cra) |
| Parent department | Michigan Department of Licensing and Regulatory Affairs (LARA) |
| Medical statute | [Medical Marihuana Facilities Licensing Act, MCL 333.27101–333.27801](https://legislature.mi.gov/Laws/MCL?objectName=mcl-333-27101) |
| Adult-use statute | [Michigan Regulation and Taxation of Marihuana Act, MCL 333.27951–333.27967](https://legislature.mi.gov/Laws/MCL?objectName=mcl-333-27951) |
| Last verified | 2026-08-09 |

## Current Cannabis Framework

| Dimension | Status |
| --- | --- |
| Adult-use possession and commercial sales | Operational under MRTMA; CRA regulates adult-use establishments |
| Medical cannabis | MMMP patient/caregiver program plus MMFLA facility licensing |
| Home cultivation | MRTMA permits personal cultivation subject to statutory limits |
| Statewide monitoring | Metrc statewide seed-to-sale system; plant and wholesale package tags are part of the traceability model |
| Local interaction | Municipal authorization/zoning remains material to facility licensing; CRA publishes a municipal guide |
| Hemp | Separate statutory/program surface; not merged into this marijuana evidence pass |

## License and Entity Graph

CRA exposes separate adult-use and medical verification workflows in Accela and
publishes periodic DOC/DOCX licensing reports. No stable public bulk registry was
found. The archive therefore preserves source-connected license records as
individual licenses and keeps legal entity, DBA, premises, and brand separate.

- [Michigan license evidence dataset](../datasets/TDTS-0025.md)
- [House Brands Distro processor license](../licenses/TLIC-0031.md)
- [Sky Cannabis processor license](../licenses/TLIC-0032.md)
- [Exhale Systems / BLOOM processor license](../licenses/TLIC-0033.md)

These are not a complete registry extract. Their status should be rechecked in
the CRA [adult-use verification search](https://aca-prod.accela.com/LARA/Cap/CapHome.aspx?module=Licenses&TabName=Licenses).

## Testing Framework

The CRA's [Sampling and Testing Technical Guidance v5.2](https://www.michigan.gov/cra/-/media/Project/Websites/cra/bulletin/5Technical/Sampling_and_Testing-_Technical_Guidance_for_Marijuana_Products_694124_7.pdf?rev=8e1a89c3519f4ff89889f66a38930f8c), revised September 23, 2024, is unusually specific. It requires or addresses cannabinoid potency, foreign matter, microbial screening, chemical residues, heavy metals, residual solvents, water activity, mycotoxins, target analytes, product homogeneity, and beverage pH. It requires results to be reported as pass/fail in Metrc and on the COA, while retaining `<LOQ` semantics rather than treating them as zero.

See the [Michigan testing requirements record](../requirements/TREQ-0003.html) and the normalized [testing requirements data](../datasets/TDTS-0024.html) for product-category differences and numeric limits.

## Testing Laboratories

The CRA requires laboratory accreditation and validated methods, but it does not
publish a complete machine-readable laboratory directory. This pass identified
three first-party laboratory records and deliberately labels their coverage as a
discovery sample:

- [PSI Labs](../testing-laboratories/TSTL-0029.html)
- [ACT Laboratories — Michigan](../testing-laboratories/TSTL-0030.html)
- [Reassure Labs](../testing-laboratories/TSTL-0031.html)

## Recalls, Advisories, and Enforcement

Michigan uses multiple notice forms. The archive preserves the CRA's terms:
voluntary recall, mandatory recall, consumer advisory, and enforcement action.
The three representative recall records below demonstrate product, licensee,
license-number, reason, consumer-instruction, and analyte linkage where the
notice names one.

- [House Brands Distro / Top Smoke vape recall](../recalls/TRCL-0007.html)
- [Sky Cannabis / Motor City Cannacarts and RIPZ recall](../recalls/TRCL-0008.html)
- [BLOOM / Exhale Systems recall](../recalls/TRCL-0009.html)

CRA enforcement documents also show that investigations may compare invoices,
COAs, and Metrc inventory. That makes the COA-to-batch relationship important
even though CRA does not expose a public statewide COA repository.

## Public Data and Evidence Gaps

| Surface | Result in this pass |
| --- | --- |
| License registry | Public search and periodic aggregate reports; no bulk endpoint located |
| Laboratory registry | Public verification/search surface; no complete machine-readable list located |
| Testing requirements | Deep PDF guidance and rule citations; normalized requirement/action-limit extract added |
| Recalls/advisories | Public CRA bulletin and news-release history; small structured corpus added |
| Metrc/package identifiers | Described by CRA and visible in notices/enforcement documents; no public bulk feed located |
| COAs/batch chemistry | No public Michigan corpus suitable for normalized ingestion found |
| Sales/market totals | CRA monthly/statistical DOC/DOCX reports; aggregate only |

## Sources and Provenance

The expanded Michigan source manifest at
`data/source-manifests/stubs/michigan.json` records authority, source class,
format, update cadence, retrieval date, machine-readability, and archival
caveats. The implementation and design friction are recorded in the repository
reports `michigan-coa-source-discovery.md`, `michigan-jurisdiction-friction.md`,
and `jurisdiction-three-state-review.md`.
