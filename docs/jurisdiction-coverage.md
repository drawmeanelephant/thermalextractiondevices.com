# Jurisdiction Coverage

Cannabis regulation and public-data coverage matrix for the jurisdiction collection.
All profiles verified **2026-08-09** from official sources (regulator sites, statutes,
official open-data portals). This document is a project management and ingestion-planning
artifact — it is **not legal advice** and the tier/priority columns are editorial ingestion
metrics, not ratings of any program.

- Index page: `content/jurisdictions.md`
- Source registry: `metadata/jurisdiction-sources.jsonl`
- Quality status report: `reports/jurisdiction-quality-status.md`
- Refresh queue: `reports/jurisdiction-refresh-queue.md`

## Method

Each jurisdiction page records the responsible authority, program status on separate
dimensions (adult-use possession, adult-use commercial sales, medical access, home
cultivation, hemp where relevant), the official regulatory data surface, and source
provenance with effective/retrieval dates. Frameworks are never collapsed into
"legal/illegal"; a jurisdiction can simultaneously permit possession, prohibit sales,
and allow home cultivation.

### Data Readiness Score

The **deep-ingestion priority** is an editorial project metric answering *"which
jurisdiction should we ingest deeply next?"* — not *"which program is best?"*. Dimensions
scored 1–5 (5 = best for this project), consistent with `docs/state-expansion-roadmap.md`:

| Dimension | 5 means |
| --- | --- |
| Chemistry value | public numeric analyte/contaminant results at scale |
| Batch-level value | per-batch/per-sample records (not just aggregates) |
| License value | complete, current license registry |
| Lab value | lab identity + lab-level test attribution |
| Machine readability | documented API / stable CSV/JSON downloads |
| Historical depth | multi-year back catalog retained |
| Source stability | dedicated, maintained publication surface |
| Ingestion complexity | low implementation effort (5 = easiest) |
| Privacy risk | low risk of publishing restricted/sensitive data (5 = safest) |

### Tiers

- **Tier A** — strong deep-ingestion candidates: official structured data, testing/lab
  datasets, stable downloads/APIs, recalls/advisories, meaningful batch or chemistry value.
- **Tier B** — good regulatory information, limited structured data.
- **Tier C** — verified legal/regulatory baseline, poor public machine-readable data.

California, Massachusetts, and Michigan are **deep-data implementation states** (connected
evidence implementations) rather than rescored tier members. Michigan does not yet have a
live bulk adapter because its public license and COA surfaces are portal/document-heavy.

## United States

### States and D.C. (matrix)

Abbreviations: AU = adult use; M = medical; HG = home cultivation; CMR = commercial
regulated market; L = license data; LB = laboratory data; BT = batch/testing data;
R/A = recalls/advisories; MR = machine-readable. Values: Y = yes/operational, P =
partial, N = no / not operational / none located, — = not applicable.

| Jurisdiction | Type | AU | M | CMR | HG | Primary regulator | Testing framework | L | LB | BT | R/A | MR | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Alabama](../content/jurisdictions/alabama.md) | state | N | Y | N | N | AMCC | AMCC rules | P | P | N | N | N | C |
| [Alaska](../content/jurisdictions/alaska.md) | state | Y | Y | Y | Y | AMCO/MCB | 3 AAC 306 | P | P | N | N | N | C |
| [Arizona](../content/jurisdictions/arizona.md) | state | Y | Y | Y | Y | ADHS | A.R.S. 36 + rules | P | P | N | P | N | C |
| [Arkansas](../content/jurisdictions/arkansas.md) | state | N | Y | N | N | ADH / MMC | Commission rules | P | P | N | N | N | C |
| [California](../content/jurisdictions/TJUR-0001.md) | state | Y | Y | Y | Y | DCC | MAUCRSA / DCC | Y | Y | P | Y | P | Deep-ingested |
| [Colorado](../content/jurisdictions/colorado.md) | state | Y | Y | Y | Y | MED (DOR) | 1 CCR 212-3 | Y | P | N | P | Y | A |
| [Connecticut](../content/jurisdictions/connecticut.md) | state | Y | Y | Y | Y | DCP | DCP regs | P | N | P | P | Y | A |
| [Delaware](../content/jurisdictions/delaware.md) | state | Y | Y | Y | N | OMC | OMC regs | P | N | N | P | N | C |
| [District of Columbia](../content/jurisdictions/district-of-columbia.md) | district | possession only | Y | N | Y | ABCA / DOH | DOH regs | P | N | N | P | N | C |
| [Florida](../content/jurisdictions/florida.md) | state | N | Y | N | N | OMMU (DOH) | 64ER / rule 64-4 | P | P | N | P | N | C |
| [Georgia](../content/jurisdictions/georgia.md) | state | N | low-THC | N | N | GMCC | GMCC rules | P | P | N | N | N | C |
| [Hawaii](../content/jurisdictions/hawaii.md) | state | N | Y | N | medical | DOH OMCCR | HAR 11-850 | P | P | N | N | N | C |
| [Idaho](../content/jurisdictions/idaho.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |
| [Illinois](../content/jurisdictions/illinois.md) | state | Y | Y | Y | medical | IDFPR | 68 Ill. Adm. Code 1290 | P | P | N | P | N | C |
| [Indiana](../content/jurisdictions/indiana.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |
| [Iowa](../content/jurisdictions/iowa.md) | state | N | Y | N | N | HHS BCR | IAC ch. 49 | P | P | N | N | N | C |
| [Kansas](../content/jurisdictions/kansas.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |
| [Kentucky](../content/jurisdictions/kentucky.md) | state | N | Y | N | N | OMC (CHFS) | 902 KAR | P | P | N | N | N | C |
| [Louisiana](../content/jurisdictions/louisiana.md) | state | N | Y | N | N | LDH / Pharmacy Bd | LAC | P | P | N | N | N | C |
| [Maine](../content/jurisdictions/maine.md) | state | Y | Y | Y | Y | OCP (DAFS) | OCP rules | P | P | P | P | P | B |
| [Maryland](../content/jurisdictions/maryland.md) | state | Y | Y | Y | Y | MCA | COMAR 27 | P | P | N | P | N | B |
| [Massachusetts](../content/jurisdictions/TJUR-0022.md) | state | Y | Y | Y | Y | CCC | 935 CMR 500 | Y | Y | Y | Y | Y | Deep-ingested |
| [Michigan](../content/jurisdictions/michigan.md) | state | Y | Y | Y | Y | CRA | MRTMA rules | P | P | N | P | P | Deep-ingested |
| [Minnesota](../content/jurisdictions/minnesota.md) | state | Y | Y | Y | Y | OCM | Minn. Stat. 342 | P | P | N | P | N | B |
| [Mississippi](../content/jurisdictions/mississippi.md) | state | N | Y | N | N | MSDH | MSDH regs | P | P | N | N | P | C |
| [Missouri](../content/jurisdictions/missouri.md) | state | Y | Y | Y | Y | DHSS DCR | 19 CSR 30-95 | P | P | N | P | N | C |
| [Montana](../content/jurisdictions/montana.md) | state | Y | Y | Y | Y | DOR CCD | ARM 42.41 | P | P | N | Y | N | B |
| [Nebraska](../content/jurisdictions/nebraska.md) | state | N | implementing | N | N | NMCC | NMCC regs | P | N | N | N | N | C |
| [Nevada](../content/jurisdictions/nevada.md) | state | Y | Y | Y | Y | CCB | NAC 453A | Y | Y | Y | Y | Y | A |
| [New Hampshire](../content/jurisdictions/new-hampshire.md) | state | N | Y | N | N | DHHS TCP | RSA 126-X / He-C 500 | P | P | N | N | N | C |
| [New Jersey](../content/jurisdictions/new-jersey.md) | state | Y | Y | Y | Y | CRC | NJAC 17:30 | P | P | N | P | P | C |
| [New Mexico](../content/jurisdictions/new-mexico.md) | state | Y | Y | Y | Y | RLD CCD | NMAC 16.8 | P | P | N | P | unknown | B |
| [New York](../content/jurisdictions/new-york.md) | state | Y | Y | Y | Y | OCM | 9 NYCRR Part 125 | Y | N | N | P | Y | A |
| [North Carolina](../content/jurisdictions/north-carolina.md) | state | N | N | N | N | none (tribal exception) | none | N | N | N | N | N | C |
| [North Dakota](../content/jurisdictions/north-dakota.md) | state | N | Y | N | N | ND HHS | NDAC 33-39 | P | P | N | N | N | C |
| [Ohio](../content/jurisdictions/ohio.md) | state | Y | Y | Y | Y | DCC (Commerce) | OAC 3796:7 | P | P | N | P | N | C |
| [Oklahoma](../content/jurisdictions/oklahoma.md) | state | N | Y | N | Y | OMMA | OAC 310:681 | P | P | N | P | N | C |
| [Oregon](../content/jurisdictions/oregon.md) | state | Y | Y | Y | Y | OLCC / OHA | OAR 333-007 | Y | Y | N | Y | Y | A |
| [Pennsylvania](../content/jurisdictions/pennsylvania.md) | state | N | Y | N | N | PA DOH | 28 Pa. Code 1171 | P | P | N | P | N | C |
| [Rhode Island](../content/jurisdictions/rhode-island.md) | state | Y | Y | Y | Y | CCC (RI) | 216-RICR-50 | P | P | N | P | N | C |
| [South Carolina](../content/jurisdictions/south-carolina.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |
| [South Dakota](../content/jurisdictions/south-dakota.md) | state | N | Y | N | N | SD DOH | SDCL 34-20G / ARSD | P | P | N | N | N | C |
| [Tennessee](../content/jurisdictions/tennessee.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |
| [Texas](../content/jurisdictions/texas.md) | state | N | low-THC | N | N | DSHS | 25 TAC 460 | P | N | N | P | N | C |
| [Utah](../content/jurisdictions/utah.md) | state | N | Y | N | N | CMC (DHHS) | UAC R523 | P | P | N | P | N | C |
| [Vermont](../content/jurisdictions/vermont.md) | state | Y | Y | Y | Y | CCB (VT) | CVR 41 | P | P | N | P | N | C |
| [Virginia](../content/jurisdictions/virginia.md) | state | possession only | Y | pending 2027 | Y | CCA | 18VAC 111 | N | N | N | N | N | C |
| [Washington](../content/jurisdictions/washington.md) | state | Y | Y | Y | N | LCB | WAC 314-55 | Y | Y | N | P | P | B |
| [West Virginia](../content/jurisdictions/west-virginia.md) | state | N | Y | N | N | OMC (WV) | CSR 110-15 | P | P | N | N | N | C |
| [Wisconsin](../content/jurisdictions/wisconsin.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |
| [Wyoming](../content/jurisdictions/wyoming.md) | state | N | N | N | N | none | none | N | N | N | N | N | C |

### Territories and federal

| Jurisdiction | Type | AU | M | CMR | HG | Regulator | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Puerto Rico](../content/jurisdictions/puerto-rico.md) | territory | N | Y | N | N | PR DOH (Act 42-2017) | C |
| [Guam](../content/jurisdictions/guam.md) | territory | Y | Y | nascent | Y | Cannabis Control Board | C |
| [U.S. Virgin Islands](../content/jurisdictions/us-virgin-islands.md) | territory | Y | Y | licensing | unknown | OCR | C |
| [Northern Mariana Islands](../content/jurisdictions/northern-mariana-islands.md) | territory | Y | Y | N | Y | Cannabis Commission | C |
| [American Samoa](../content/jurisdictions/american-samoa.md) | territory | N | N | N | N | none identified | C (needs-review) |
| [United States (federal context)](../content/jurisdictions/united-states-federal.md) | federal | — | — | — | — | DEA/FDA/USDA | n/a |

## International

| Country | Framework in brief | National authority | Deep-ingestion priority |
| --- | --- | --- | --- |
| [Australia](../content/jurisdictions/australia.md) | Medical (TGA/ODC); ACT personal-use exemption | TGA; ODC | 6-country deepened set |
| [Canada](../content/jurisdictions/canada.md) | Federally legal adult use; provincial retail | Health Canada | 6-country deepened set |
| [Colombia](../content/jurisdictions/colombia.md) | Medical (2016); personal dose not criminalized | INVIMA/ICA/FNE | baseline |
| [Czechia](../content/jurisdictions/czechia.md) | Personal possession/cultivation legal 2026; no sales | MoH; SUKL | baseline |
| [Denmark](../content/jurisdictions/denmark.md) | Permanent medical scheme from 1 Jan 2026 (LOV 439/2025); no adult use | Lægemiddelstyrelsen (DMA) | baseline |
| [Germany](../content/jurisdictions/germany.md) | CanG 2024: possession/cultivation/associations; medical | BMG; BfArM | 6-country deepened set |
| [Israel](../content/jurisdictions/israel.md) | Large medical program; possession decriminalized in practice | MoH Medical Cannabis Unit | baseline |
| [Luxembourg](../content/jurisdictions/luxembourg.md) | Personal possession/cultivation (2023); no sales | Justice MoJ | baseline |
| [Malta](../content/jurisdictions/malta.md) | Personal cultivation + licensed non-profit associations | ARUC | baseline |
| [Mexico](../content/jurisdictions/mexico.md) | Medical regulated; personal use decriminalized by court rulings | COFEPRIS | baseline |
| [Netherlands](../content/jurisdictions/netherlands.md) | Tolerance policy + supply-chain experiment (2025) | VWS; BMC | 6-country deepened set |
| [New Zealand](../content/jurisdictions/new-zealand.md) | Medicinal cannabis scheme; adult use declined 2020 | MoH Agency; Medsafe | baseline |
| [Portugal](../content/jurisdictions/portugal.md) | Decriminalized possession; medical via INFARMED | INFARMED | baseline |
| [South Africa](../content/jurisdictions/south-africa.md) | Private use/cultivation legal (CPPA 2024) | DOJ&CD; SAHPRA | baseline |
| [Spain](../content/jurisdictions/spain.md) | Medical decree (2025); private use tolerated | AEMPS | baseline |
| [Switzerland](../content/jurisdictions/switzerland.md) | Authorized pilot trials; medical by prescription | BAG/FOPH | 6-country deepened set |
| [Thailand](../content/jurisdictions/thailand.md) | Re-restricted to medical/health use (2025) | MoPH; Thai FDA | baseline |
| [Uruguay](../content/jurisdictions/uruguay.md) | Fully regulated non-medical market (2013) | IRCCA | 6-country deepened set |

## Deepened jurisdictions (this wave)

U.S. beyond California, Massachusetts, and Michigan: **Nevada, Colorado, Connecticut, Oregon,
New York** — each page carries regulator history, licensing categories, testing-lab
framework, contaminant-rule links, open datasets, recalls/advisories, traceability,
market status, and ingestion opportunities, sourced from the verified ledger in
`docs/state-expansion-roadmap.md` (primary sources fetched 2026-08-08).

International (6 of 17): **Canada, Germany, Uruguay, Netherlands, Australia,
Switzerland** — each carries regulatory history, licensing structure, laboratory/
quality requirements, recall/advisory system, open data, and future ingestion
opportunities.

## Verification ledger

- All U.S. state/territory and international statuses were verified against official
  sources (regulator sites, statutes, government portals) on **2026-08-08/09**.
- State open-data dataset identifiers (Colorado, Connecticut, New York, Oregon,
  Washington, Nevada, Michigan, New Jersey, Mississippi) were verified live 2026-08-08
  in `docs/state-expansion-roadmap.md` (Socrata SODA probes, HTTP checks, page text).
- Federal rescheduling (Schedule III, effective April 28, 2026) verified against DEA
  and Federal Register (April 28, 2026).
- **Pages withheld / needs-review**: American Samoa (no authoritative cannabis-specific
  official source verified — placeholder only). Puerto Rico regulator identity flagged
  for re-verification before deep ingestion.

## Remaining research gaps

1. Home-cultivation specifics for a handful of states are stated at the dimension level
   and should be re-verified against current statute text before deep ingestion.
2. Connecticut COA/label GUID links (`elicense.ct.gov`) — long-term link stability
   unverified.
3. New Mexico C.R.O.P. catalog contents unverified (dataset list did not render in a
   static fetch).
4. Nevada license-registry full-extract export format unconfirmed.
5. Washington derived-publication legal gate (RCW 42.56.070(8)) unresolved.
6. Germany cultivation-association counts are secondary-reported; verify against state
   authorities before reuse.
