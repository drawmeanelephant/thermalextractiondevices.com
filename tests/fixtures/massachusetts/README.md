# Massachusetts fixtures

Small, committed fixtures derived from the official Massachusetts CCC schemas.
They exist so unit tests and `--fixtures-only` runs never require network
access. They are **samples**, not the full source datasets.

## Provenance

All fixtures were captured from the official CCC data catalog
(`https://masscannabiscontrol.com/open-data/data-catalog/`) on 2026-08-05:

| Fixture | Source dataset | Size | Notes |
| --- | --- | --- | --- |
| `l_licenses_all_details_public.csv` | All Licenses / Licensing Tracker | 14 rows | All 10 active ITLs + 1 each of Retailer/Cultivator/Product Manufacturer/MTC |
| `l_licenses_commence_ops.csv` | Commence Ops | 8 rows | ITLs + representative rows |
| `l_licenses_mtc.csv` | MTC Licenses | 5 rows | Coordinates/addresses scrubbed |
| `CCC_Testing_Results_2025.csv` | Testing results 2025 | 40 rows | All 7 analytes represented |
| `Testing_Results_2024_20260415_OpenData.csv` | Testing results 2024 | 41 rows | 30 real rows (Arsenic/Metal/Buds) + 11 schema-faithful rows crafted from the official analyte naming convention to represent Potency/Microbial/Metal categories |
| `a_sales_au_gross.csv` | AU facility sales | 40 rows | Category spread |
| `a_sales_au_deliveries.csv` | Retail/delivery weekly | 16 rows | |
| `a_sales_mtc_gross.csv` | MTC facility sales | 17 rows | |
| `a_sales_au_price_per_gram.csv` | Avg monthly price/g | 92 rows | Full series 2018-11..2026-06 |
| `a_sales_au_activityvolume.csv` | Plant activity | 40 rows | |
| `a_applications_all.csv` | Applications | 14 rows | Full |
| `a_applications_dbe.csv` | DBE totals | 7 rows | Full |
| `a_agents_gender.csv` | Agent gender | 4 rows | Full |
| `a_agents_raceethnicity.csv` | Agent race/ethnicity | 10 rows | Full |
| `advisories.json` | Advisories portal | 3 advisories | Parsed records incl. affected-product and retailer tables |

## Scrubbing

Sensitive source columns are blanked in committed fixtures: `EIN_TIN`,
business/mailing street addresses, business email, business phone,
`FULL_ADDRESS`, `LATITUDE`/`LONGITUDE`, equity/SE account numbers, and ZIP
codes. Public values (license numbers, legal names, municipalities, counties,
license types, statuses, dates) are preserved exactly.

## Usage

```sh
python3 scripts/state_ingest.py massachusetts --fixtures-only --skip-publish --quiet
```

Unit tests load these directly through `FixtureFetcher`.
