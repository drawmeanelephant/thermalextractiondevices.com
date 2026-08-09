# Jurisdiction Refresh Queue

Editorial maintenance queue for jurisdiction pages. Refresh policy: a **legal summary
older than 180 days** triggers re-verification (a maintenance policy, not a statement
that the law changed). All pages currently carry `Last verified: 2026-08-09`; ranking
below reflects **legal volatility**, **data-source volatility**, and **importance**
rather than age. This queue is designed to feed scheduled jurisdiction refresh agents.

Ranking inputs:

- **Legal volatility** — active legislation, court cases, or policy reversals.
- **Data-source volatility** — changing datasets, portals, contracts, or formats.
- **Importance** — deep-ingestion priority and market relevance.

## Priority 1 — re-verify within 30 days (high volatility, high importance)

| Rank | Jurisdiction | Why |
| --- | --- | --- |
| 1 | United States (Federal Context) | Schedule III rescheduling hearing (from 2026-06-29) and final hemp rule (2026-11-12) pending — most volatile page |
| 2 | Georgia | SB 220 took effect 2026-07-01; implementation and rulemaking in motion |
| 3 | Virginia | Retail licensing from 2026-09-01; sales earliest 2027-05-01; hemp rule changed 2026-08-15 |
| 4 | Germany | CanG revision/repeal debate in the 2025–26 coalition; cultivation-association counts moving |
| 5 | Thailand | Policy reversal (2025) still settling; licences expiring 2026–27 |
| 6 | Nebraska | Medical program implementation; licensing periods opening mid-2026 |

## Priority 2 — re-verify within 90 days (moderate volatility)

| Rank | Jurisdiction | Why |
| --- | --- | --- |
| 7 | Nevada | Top ingestion candidate; monthly lab-library cadence changes data surfaces |
| 8 | Netherlands | Supply-chain experiment evaluation and extension decisions |
| 9 | Ohio | SB 56 (2026) implementation; intoxicating-hemp market restructuring |
| 10 | Mexico | COFEPRIS July 2026 clarification; court-driven policy flux |
| 11 | South Africa | CPPA draft regulations (Feb 2026) finalization expected through 2026 |
| 12 | Louisiana | 2026 recriminalization measure; adult-use pilot bill died |
| 13 | Oklahoma | New rules 2026-07-11; labeling law enforcement 2026-11-01; license moratorium to 2026-08-01 |
| 14 | Washington | RCW 42.56.070(8) legal gate; dated XLSX lists refresh weekly/monthly |
| 15 | Massachusetts | Live ingestion sync decision; CCC data catalog cadence |

## Priority 3 — re-verify within 180 days (standard)

| Rank | Jurisdiction | Why |
| --- | --- | --- |
| 16 | Connecticut | Product registry + sales datasets weekly/monthly; COA GUID link stability |
| 17 | Colorado | Monthly sales/tax datasets; quarterly dashboard |
| 18 | New York | License registry refresh cadence |
| 19 | Oregon | Socrata story-view resolution; daily license data |
| 20 | Alabama | Dispensary openings through summer 2026 |
| 21 | Kentucky | Program maturation; conditions EO 2026-06 |
| 22 | Canada | Omnibus regulatory updates; producer list refresh |
| 23 | Uruguay | IRCCA rule revisions and price adjustments |
| 24 | Switzerland | Pilot-trial extensions (Züri Can to 2028); federal debate |
| 25 | Australia | TGA unapproved-product inquiry; WA bill status |
| 26–74 | All remaining pages | Baseline 180-day policy |

## Refresh automation notes

- A future scheduled agent can parse `Last verified` from each page and the volatility
  weights above to generate a work queue.
- After re-verification, update `Last verified`, the framework table, the data-surface
  table, and the provenance rows; do **not** silently rewrite history — add
  former-rule / effective-to / superseded-by notes where a rule changed.
- Update `metadata/jurisdiction-sources.jsonl` with `retrieved_at` and any new URLs.
- Mark `needs-review` pages (Puerto Rico, American Samoa) resolved only after
  authoritative verification.
