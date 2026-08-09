# Massachusetts Fixture Provenance Inventory

Status: **verified 2026-08-05** · Scope: `tests/fixtures/massachusetts/`

## Policy

Fixtures are **test-only inputs**. They exist so unit tests and
`--fixtures-only` runs never need network access. No fixture row set —
verbatim, redacted, synthetic, or handcrafted — may contribute to published
totals, analyte distributions, market statistics, testing summaries, official
dataset manifests, source-derived Markdown, or revision reports presented as
real data.

The hard guard in `scripts/ingest/states/massachusetts.py` (both
`MassachusettsSync.run_dataset` — manifest/snapshot writes — and
`MassachusettsSync.generate_content` — page writes) and `scripts/state_ingest.py`
refuses fixture-only execution unless the explicit development flag
`--allow-fixture-content` is supplied. When that flag is used, the CLI routes
output to an isolated, gitignored demo directory
(`var/ingest/<state>-ccc/demo-content`) — never the real `content/` tree.
The public content tree on `main` must only ever be generated from a
complete verified live snapshot.

## Row-set labels

| Fixture | Rows | Label | Notes |
| --- | --- | --- | --- |
| `l_licenses_all_details_public.csv` | 14 | **redacted source excerpt** | Verbatim rows from the official license tracker (all 10 active ITLs + representative others); sensitive columns (`EIN_TIN`, emails, phones, addresses, coords, ZIPs, SE/equity numbers) blanked. |
| `l_licenses_commence_ops.csv` | 8 | **redacted source excerpt** | Verbatim rows, sensitive columns blanked. |
| `l_licenses_mtc.csv` | 5 | **redacted source excerpt** | Verbatim rows; coordinates/street addresses scrubbed. |
| `CCC_Testing_Results_2025.csv` | 39 | **verbatim source excerpt** | First slice of the official 2025 testing CSV, copied unchanged. |
| `Testing_Results_2024_20260415_OpenData.csv` | 41 | **mixed: verbatim source excerpt (30) + synthetic schema fixture (11)** | First 30 rows copied unchanged from the official 2024 file; 11 additional rows crafted from the official analyte-naming convention to exercise Potency/Microbial/Metal categories. The 11 synthetic rows must never appear in published testing aggregates. |
| `a_sales_au_gross.csv` | 40 | **verbatim source excerpt** | Slice of the official file. |
| `a_sales_au_deliveries.csv` | 16 | **verbatim source excerpt** | Slice of the official file. |
| `a_sales_mtc_gross.csv` | 17 | **verbatim source excerpt** | Slice of the official file. |
| `a_sales_au_price_per_gram.csv` | 92 | **verbatim source excerpt** | Full monthly series 2018-11 .. 2026-06 from the official file. |
| `a_sales_au_activityvolume.csv` | 40 | **verbatim source excerpt** | Slice of the official file. |
| `a_applications_all.csv` | 14 | **verbatim source excerpt** | Full small dataset from the official file. |
| `a_applications_dbe.csv` | 7 | **verbatim source excerpt** | Full small dataset from the official file. |
| `l_applications_all_details.csv` | 20 | **redacted source excerpt** | First slice of the official application-detail file; EIN/TIN, business/mailing/establishment addresses, ZIPs, phones, emails, fee and equity-program numbers blanked. Only identity columns (legal name, license number/type/status, municipality) remain populated. |
| `a_agents_gender.csv` | 4 | **verbatim source excerpt** | Full small dataset from the official file. |
| `a_agents_raceethnicity.csv` | 10 | **verbatim source excerpt** | Full small dataset from the official file. |
| `adv1.html`, `adv2.html`, `adv3.html` | — | **redacted source excerpt** | Real advisory pages downloaded from the CCC advisories portal, truncated to table-relevant sections; nav boilerplate stripped. |
| `advisories.json` | 3 advisories | **derived from verbatim source** | Parsed records produced from the real advisory HTML; advisory titles were programmatically prefixed with the Commission's own term ("Public Health and Safety Advisory: …"). No synthetic values. |

Captured 2026-08-09 (this v2 run): `l_applications_all_details.csv` added to
match the current official catalog (the file was missing from the original
2026-08-05 fixture set).

## Integrity notes

* Verified on 2026-08-05: the license fixtures contain **0** email addresses,
  0 phone numbers, 0 EIN/TIN values, and 0 coordinate values after redaction.
* The 2025 testing fixture contains 39 rows (the older `README.md` says 40;
  `PROVENANCE.md` counts are authoritative).
* The `advisories.json` fixture's third advisory has no package table (the
  published notice references the Summary Suspension Order's 544 lab
  samples); it is modeled honestly with an affected-product count of 0.

## Handcrafted edge cases

No fixture row set is handcrafted. All rows are verbatim source excerpts,
redacted source excerpts, synthetic schema-faithful rows (2024 testing
fixture), or derived from verbatim source (`advisories.json`). Handcrafted
edge-case inputs, if ever needed, must be confined to unit-test literals
inside `tests/` and must never be added to the fixture directory.

## Guard verification

```sh
python3 scripts/state_ingest.py massachusetts --fixtures-only      # refuses (exit 2)
# dev-only: writes to var/ingest/massachusetts-ccc/demo-content (gitignored)
python3 scripts/state_ingest.py massachusetts --fixtures-only --allow-fixture-content --skip-publish --quiet
```
