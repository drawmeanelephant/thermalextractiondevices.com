# Jurisdiction Expansion v1 — Final Report

- **Branch**: `agent/jurisdiction-expansion-v1`
- **Base**: `github/main` @ `05a14d7` (fast-forwarded before work began)
- **Completed**: 2026-08-09
- **Scope**: Complete U.S. scaffold (50 states + D.C.), U.S. federal context, U.S. territories, international country seed set, generalized navigation, source manifest, coverage and refresh documentation.

## Executive summary

The `jurisdictions` collection grew from a single canonical California profile (TJUR-0001)
to **74 satellite jurisdiction pages** (73 new). Every page contains verified identity,
program status per legal dimension (never collapsed to a single legal/illegal field),
official sources, retrieval dates, and a data-surface map. California remains the canonical
deep-data implementation and was not modified; Massachusetts is reconciled as the
reference state adapter with a verified data-ready page.

## U.S. jurisdictions completed

- **50 states + Washington, D.C.** — all present with verified baseline content
  (TJUR-0002..TJUR-0051). No empty shells: every page carries authority, program
  status, official source, and `Last verified` date.
- **U.S. federal context** (TJUR-0074): Controlled Substances Act context, the
  April 28, 2026 Schedule III rescheduling rule, FDA-approved cannabis-related drugs,
  the 2018 farm-bill hemp framework, federal research context, and state-law
  divergence — sourced from DEA/Federal Register and FDA.
- **U.S. territories** (TJUR-0052..TJUR-0056): Puerto Rico, Guam, U.S. Virgin Islands,
  Northern Mariana Islands, American Samoa.

## International jurisdictions completed

17 country pages (TJUR-0057..TJUR-0073): Canada, Uruguay, Germany, Netherlands, Malta,
Luxembourg, Switzerland, Czechia, Portugal, Spain, Australia, New Zealand, Israel,
South Africa, Thailand, Mexico, Colombia. Each page reports possession/cultivation/
commercial-supply/medical/pharmaceutical/home-grow/import dimensions separately and
documents subnational structures where they exist (e.g., Canada provinces, Australia
states/territories, Spain autonomous communities, Switzerland cantons).

## Deepened jurisdictions

- **U.S. beyond CA/MA (5)**: Nevada, Colorado, Connecticut, Oregon, New York — each
  with regulator history, program structure, licensing categories, testing-laboratory
  framework, testing panel, official contaminant-rule links, open datasets,
  recalls/advisories, traceability system, market status, and implementation-ready
  source inventories (no pipelines built this wave).
- **International (6 of 17)**: Canada, Germany, Uruguay, Netherlands, Australia,
  Switzerland — each with regulatory history, licensing structure, laboratory/quality
  requirements, product standards, recall/advisory system, open data, and future
  ingestion opportunities. National medical-cannabis testing systems are described as
  pharmaceutical (GMP/EU-GMP, pharmacopoeial) systems, not equated with U.S.
  state compliance-lab programs.
- **Canonical implementations**: California (deep-ingested, unchanged) and
  Massachusetts (data-ingestion-ready, adapter fixture-tested at
  `scripts/ingest/states/massachusetts.py`; live sync pending privacy-safe handling
  of regulated data).

## Official sources checked

- ~90 web searches executed across the wave; statuses verified against official
  sources on **2026-08-08/09**: state legislature/statute pages, regulator sites
  (DCC, CCC, CRA/WSLCB, CCB, OCM, AMCC, OMMA, DCR/ODCM, ABCA, etc.), state health
  departments, and official open-data portals (Socrata SODA probes and page-text
  checks for Colorado, Connecticut, New York, Oregon, Washington, Nevada, Michigan,
  New Jersey, Mississippi).
- Federal: DEA and Federal Register (Schedule III rule, effective April 28, 2026).
- International: national legislation databases, ministries of health, medicines
  regulators (BfArM, Health Canada, IRCCA, TGA, INFARMED, Medsafe, SAHPRA, Thai FDA,
  COFEPRIS, INVIMA/ICA), and government gazettes; original-language sources cited
  where English is not authoritative.
- Every cited source is recorded in `metadata/jurisdiction-sources.jsonl`
  (jurisdiction_id, source_type, title, url, retrieved_at, language, authority_level).

## Pages withheld / flagged

- **American Samoa** (TJUR-0056): no authoritative cannabis-specific official source
  verified; page is an honest placeholder flagged `needs-review` in
  `reports/jurisdiction-quality-status.md` — no fabricated certainty.
- **Puerto Rico** (TJUR-0052): regulator identity flagged for re-verification before
  deep ingestion (`needs-review`).
- No other page was withheld; all 50 states + D.C. had verifiable official sources.

## Data-ready states (deep-ingestion candidates)

- **Tier A (strongest)**: Colorado, Connecticut, Nevada, New York, Oregon — official
  structured data, license/lab registries, recall/advisory surfaces, machine-readable
  portals.
- **Data-ready beyond Tier A**: Massachusetts (adapter ready), Michigan, Minnesota,
  Washington, New Jersey, Mississippi (verified open-data identifiers in
  `docs/state-expansion-roadmap.md`).
- Tier definitions and per-state data-surface matrices: `docs/jurisdiction-coverage.md`.
- Editorial ingestion-priority scores (project metric, not a legal rating) and method:
  `docs/jurisdiction-coverage.md#data-readiness-score`.

## Data-ready countries

- **Deep set (6)**: Canada, Germany, Uruguay, Netherlands, Australia, Switzerland —
  mature frameworks with official data surfaces (Health Canada licensed-producer
  open data; BfArM/BfArM-Cannabisagentur; IRCCA; BMC experiment data; TGA/ODC;
  BAG pilot trials).
- Baseline set: Malta, Luxembourg, Czechia, Portugal, Spain, New Zealand, Israel,
  South Africa, Thailand, Mexico, Colombia — official source recorded, ingestion
  priority lower.

## New graph relationships

- `jurisdictions/TJUR-0036` (Ohio) ↔ `law-and-use/TLAW-0001` (Ohio Medical Cannabis:
  Permitted Forms and Vaporization Rules) — bidirectional `relates_to`.
- Existing entity-side links to `jurisdictions/TJUR-0001` (California) were already in
  place and remain untouched (labs, recalls, datasets, requirements, organizations,
  licenses).
- Deepened pages embed explicit wiring guidance for future adapters (e.g., "future
  dataset/license records should add `relates_to=jurisdictions/TJUR-00XX` per the
  California pattern") so downstream records land on the right jurisdiction.
- No device → legal_in assertions were added; device legality is not inferred from
  cannabis legality.

## ID changes

- **None renumbered.** New IDs TJUR-0002..TJUR-0074 were appended; TJUR-0001
  (California) is unchanged. `legacy_id == id` for every jurisdiction record.
- `metadata/id-map.jsonl` now covers 296 pages; `ted_ids --write` produced no
  renumbering diff.

## Validation results

| Gate | Result |
| --- | --- |
| `ted_ids --write` + revalidate | ✅ 296 pages normalized; validate run: no files changed |
| `audit_markdown_links.py content` | ✅ all local Markdown links resolve |
| Boris graph diagnostics (`validate_graph.sh`) | ✅ baseline-only `unreferenced_page` findings tolerated; parent edges valid |
| Device taxonomy audit | ✅ |
| `ted-publish.sh` (BORIS_BIN=./bin/boris) | ✅ publishing export complete; llms.txt valid UTF-8 |
| Tests (`pytest tests/`) | ✅ 150 passed, 4 skipped (same 154 total as baseline) |
| Frontmatter/schema audit (all 74 pages) | ✅ closed schema respected; no illegal keys; all pages `published` |
| Public-release audit (ted-build hook) | ⚠️ **pre-existing baseline failure, unrelated to this wave** — 172,516 blocking (HIGH) findings, **0 in any new file**; all are in `data/dcc/` raw ingestion files (committed before this branch, e.g., commit `3628c64`), plus pre-existing content/devices/manufacturers, tests/fixtures, and git history. The audit is an artifact-storage/privacy gate for the raw DCC registry data, not a jurisdiction-content issue. |

## Remaining research gaps

1. Home-cultivation specifics for a handful of states are stated at the dimension
   level; re-verify against current statute text before deep ingestion.
2. Connecticut COA/label GUID links (`elicense.ct.gov`) — long-term link stability
   unverified.
3. New Mexico C.R.O.P. catalog contents unverified (static fetch did not render the
   dataset list).
4. Puerto Rico regulator identity re-verification before any deep ingestion.
5. American Samoa requires an authoritative source before promotion from placeholder.
6. Refresh cadence: pages older than 180 days are flagged by
   `reports/jurisdiction-refresh-queue.md` (editorial policy, not a claim that law
   changed); highest-volatility pages: federal rescheduling (hearing ongoing),
   Georgia (SB 220 effective 2026-07-01), Virginia (retail 2027), Louisiana
   (2026 recriminalization measure), Ohio (SB 56 2026), Vermont (Acts 176/178 2026),
   Tennessee and Texas (2026 THC rules).

## Definition of Done

- [x] California remains stable (untouched, TJUR-0001)
- [x] Massachusetts reconciled, not duplicated (adapter + data-ready page)
- [x] Every U.S. state + D.C. has a verified baseline page
- [x] No U.S. page is empty boilerplate
- [x] Legal dimensions are not collapsed into legal/illegal
- [x] Every page cites current official sources with retrieval dates
- [x] International seed set exists (17 countries), 6 deepened
- [x] Testing/data availability mapped per jurisdiction
- [x] State ingestion priority ranked (tiers + score method)
- [x] Jurisdiction navigation usable (nav group + catalog index)
- [x] Homepage language no longer implies California is the entire regulatory layer
- [x] No canonical IDs renumbered
- [x] Boris validation passes; links pass; publication passes
- [ ] Release-audit hook is green — **blocked by pre-existing PII in `data/dcc/` raw
      files** (see validation results; requires artifact-storage migration of the raw
      DCC registry, out of scope for this wave)
