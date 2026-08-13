---
id: jurisdictions
title: "Jurisdictions"
status: published
tags: ["jurisdictions", "regulation", "cannabis", "public-data"]
relations: []
summary: "Jurisdiction profiles: verified baseline pages for all 50 U.S. states, Washington D.C., U.S. territories, the federal context, and an international country layer — each with authority, program status, data surface, and provenance."
---

# Jurisdictions

Cannabis regulation and public-data profiles for United States states, territories, the federal context, and international countries.

Each profile records the responsible authority, program status (adult use, medical, home cultivation, hemp), the official regulatory data surface, and source provenance with retrieval dates. **Not legal advice** — see the shared jurisdiction disclaimer note on every page.

Satellite records in this collection follow the form identifier schema `jurisdictions/TJUR-XXXX`. Content quality status is tracked in the internal report `reports/jurisdiction-quality-status.md` (project management only; not a legal rating). Refresh scheduling is tracked in `reports/jurisdiction-refresh-queue.md`.

- **Last verified (all profiles)**: 2026-08-09
- **Deep-data implementation states**: California (DCC), Massachusetts (CCC), and Michigan (CRA) have connected evidence implementations; see the [California DCC Data Landscape](datasets/TDTS-0004.md), the Massachusetts adapter (`scripts/ingest/states/massachusetts.py`), and the [Michigan profile](jurisdictions/michigan.md).

---

## United States

### States and District of Columbia

| Jurisdiction | Profile | Adult use | Medical | Home grow | Data tier |
| --- | --- | --- | --- | --- | --- |
| Alabama | [profile](jurisdictions/alabama.md) | No | Yes | No | C |
| Alaska | [profile](jurisdictions/alaska.md) | Yes | Yes | Yes | C |
| Arizona | [profile](jurisdictions/arizona.md) | Yes | Yes | Yes | C |
| Arkansas | [profile](jurisdictions/arkansas.md) | No | Yes | No | C |
| California | [profile](jurisdictions/TJUR-0001.md) | Yes | Yes | Yes | Deep-ingested (DCC) |
| Colorado | [profile](jurisdictions/colorado.md) | Yes | Yes | Yes | A |
| Connecticut | [profile](jurisdictions/connecticut.md) | Yes | Yes | Yes | A |
| Delaware | [profile](jurisdictions/delaware.md) | Yes | Yes | No | C |
| District of Columbia | [profile](jurisdictions/district-of-columbia.md) | Possession only | Yes | Yes | C |
| Florida | [profile](jurisdictions/florida.md) | No | Yes | No | C |
| Georgia | [profile](jurisdictions/georgia.md) | No | Low-THC | No | C |
| Hawaii | [profile](jurisdictions/hawaii.md) | No | Yes | Medical only | C |
| Idaho | [profile](jurisdictions/idaho.md) | No | No | No | C |
| Illinois | [profile](jurisdictions/illinois.md) | Yes | Yes | Medical only | C |
| Indiana | [profile](jurisdictions/indiana.md) | No | No | No | C |
| Iowa | [profile](jurisdictions/iowa.md) | No | Yes | No | C |
| Kansas | [profile](jurisdictions/kansas.md) | No | No | No | C |
| Kentucky | [profile](jurisdictions/kentucky.md) | No | Yes | No | C |
| Louisiana | [profile](jurisdictions/louisiana.md) | No | Yes | No | C |
| Maine | [profile](jurisdictions/maine.md) | Yes | Yes | Yes | B |
| Maryland | [profile](jurisdictions/maryland.md) | Yes | Yes | Yes | B |
| Massachusetts | [profile](jurisdictions/TJUR-0022.md) | Yes | Yes | Yes | Deep-data implementation (CCC) |
| Michigan | [profile](jurisdictions/michigan.md) | Yes | Yes | Yes | Deep-data implementation (CRA) |
| Minnesota | [profile](jurisdictions/minnesota.md) | Yes | Yes | Yes | B |
| Mississippi | [profile](jurisdictions/mississippi.md) | No | Yes | No | C |
| Missouri | [profile](jurisdictions/missouri.md) | Yes | Yes | Yes | C |
| Montana | [profile](jurisdictions/montana.md) | Yes | Yes | Yes | B |
| Nebraska | [profile](jurisdictions/nebraska.md) | No | Implementing | No | C |
| Nevada | [profile](jurisdictions/nevada.md) | Yes | Yes | Yes | A |
| New Hampshire | [profile](jurisdictions/new-hampshire.md) | No | Yes | No | C |
| New Jersey | [profile](jurisdictions/new-jersey.md) | Yes | Yes | No | C |
| New Mexico | [profile](jurisdictions/new-mexico.md) | Yes | Yes | Yes | B |
| New York | [profile](jurisdictions/new-york.md) | Yes | Yes | Yes | A |
| North Carolina | [profile](jurisdictions/north-carolina.md) | No | No | No | C |
| North Dakota | [profile](jurisdictions/north-dakota.md) | No | Yes | No | C |
| Ohio | [profile](jurisdictions/ohio.md) | Yes | Yes | Yes | C |
| Oklahoma | [profile](jurisdictions/oklahoma.md) | No | Yes | Yes | C |
| Oregon | [profile](jurisdictions/oregon.md) | Yes | Yes | Yes | A |
| Pennsylvania | [profile](jurisdictions/pennsylvania.md) | No | Yes | No | C |
| Rhode Island | [profile](jurisdictions/rhode-island.md) | Yes | Yes | Yes | C |
| South Carolina | [profile](jurisdictions/south-carolina.md) | No | No | No | C |
| South Dakota | [profile](jurisdictions/south-dakota.md) | No | Yes | No | C |
| Tennessee | [profile](jurisdictions/tennessee.md) | No | No | No | C |
| Texas | [profile](jurisdictions/texas.md) | No | Low-THC | No | C |
| Utah | [profile](jurisdictions/utah.md) | No | Yes | No | C |
| Vermont | [profile](jurisdictions/vermont.md) | Yes | Yes | Yes | C |
| Virginia | [profile](jurisdictions/virginia.md) | Possession only | Yes | Yes | C |
| Washington | [profile](jurisdictions/washington.md) | Yes | Yes | No | B |
| West Virginia | [profile](jurisdictions/west-virginia.md) | No | Yes | No | C |
| Wisconsin | [profile](jurisdictions/wisconsin.md) | No | No | No | C |
| Wyoming | [profile](jurisdictions/wyoming.md) | No | No | No | C |

"Adult use" is a simplification of each state's current framework — possession, commercial sales, and cultivation can each differ (e.g., Virginia permits possession but has no retail yet; D.C. permits possession but has no licensed adult-use retail). Read the individual profile for the precise dimensions. "Data tier" is an editorial ingestion-priority tier (see `docs/jurisdiction-coverage.md`), not a judgment of a state's program.

### U.S. Federal Context

| Jurisdiction | Profile |
| --- | --- |
| United States (federal context) | [profile](jurisdictions/united-states-federal.md) |

### U.S. Territories

| Jurisdiction | Profile | Status |
| --- | --- | --- |
| Puerto Rico | [profile](jurisdictions/puerto-rico.md) | Medical program; adult use not enacted |
| Guam | [profile](jurisdictions/guam.md) | Adult use legal; market nascent (2026) |
| U.S. Virgin Islands | [profile](jurisdictions/us-virgin-islands.md) | Adult use legal; licensing open |
| Northern Mariana Islands | [profile](jurisdictions/northern-mariana-islands.md) | Adult use legal; market not operational |
| American Samoa | [profile](jurisdictions/american-samoa.md) | needs-review — no authoritative source verified |

---

## International

| Country | ISO | Profile | Framework in brief |
| --- | --- | --- | --- |
| Australia | AU | [profile](jurisdictions/australia.md) | Medical (TGA/ODC); ACT personal-use exemption |
| Canada | CA | [profile](jurisdictions/canada.md) | Federally legal adult use; provincial retail |
| Colombia | CO | [profile](jurisdictions/colombia.md) | Medical (2016); personal dose not criminalized |
| Czechia | CZ | [profile](jurisdictions/czechia.md) | Personal possession/cultivation legal 2026; no sales |
| Denmark | DK | [profile](jurisdictions/denmark.md) | Permanent medical scheme from 2026 (LOV 439/2025); no adult use |
| Germany | DE | [profile](jurisdictions/germany.md) | CanG 2024: possession/cultivation/associations; medical |
| Israel | IL | [profile](jurisdictions/israel.md) | Large medical program; possession decriminalized in practice |
| Luxembourg | LU | [profile](jurisdictions/luxembourg.md) | Personal possession/cultivation (2023); no sales |
| Malta | MT | [profile](jurisdictions/malta.md) | Personal cultivation + licensed non-profit associations |
| Mexico | MX | [profile](jurisdictions/mexico.md) | Medical regulated; personal use decriminalized by court rulings |
| Netherlands | NL | [profile](jurisdictions/netherlands.md) | Tolerance policy + supply-chain experiment (2025) |
| New Zealand | NZ | [profile](jurisdictions/new-zealand.md) | Medicinal cannabis scheme; adult use declined 2020 |
| Portugal | PT | [profile](jurisdictions/portugal.md) | Decriminalized possession; medical via INFARMED |
| South Africa | ZA | [profile](jurisdictions/south-africa.md) | Private use/cultivation legal (CPPA 2024) |
| Spain | ES | [profile](jurisdictions/spain.md) | Medical decree (2025); private use tolerated |
| Switzerland | CH | [profile](jurisdictions/switzerland.md) | Authorized pilot trials; medical by prescription |
| Thailand | TH | [profile](jurisdictions/thailand.md) | Re-restricted to medical/health use (2025) |
| Uruguay | UY | [profile](jurisdictions/uruguay.md) | Fully regulated non-medical market (2013) |

International profiles use country-appropriate dimensions (medical access, pharmaceutical cannabinoids, home cultivation, import/export) rather than U.S.-style categories. Original-language official sources are cited where English materials are unavailable.

---

## How to Read a Jurisdiction Profile

Every profile contains:

1. **Jurisdiction Identity** — authority, official website, retrieval date.
2. **Current Framework** — separate dimensions for possession, commercial sales, medical access, home cultivation, and hemp where relevant. Frameworks are never collapsed into "legal"/"illegal".
3. **Data Surface** — a table using `yes` / `partial` / `no public source located` / `unknown`, with the official source for each surface.
4. **Sources & Provenance** — statutory framework with effective dates, regulator links, and retrieval date.
5. **Last verified** — every page exposes its verification date; pages older than ≈180 days are flagged for refresh by the maintenance queue.
