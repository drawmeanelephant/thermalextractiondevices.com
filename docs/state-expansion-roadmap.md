# State Expansion Roadmap — Next 10 Ingestion Targets

Status: **draft (research-complete, nothing implemented)** · Date: 2026-08-08
Author: State Program Expansion Scout (Agent 6)
Branch: `agent/state-ingestion-roadmap`

This document turns the national regulatory-data research into an
implementation-ready state expansion queue. It ranks the **next 10 strongest
state candidates** after California (DCC, in `data/dcc/`, `scripts/dcc_ingest.py`)
and Massachusetts (CCC, in `scripts/ingest/states/massachusetts.py`).

---

## 1. Method and evidence policy

> **Corpus note.** The task prompt references an organized research corpus
> (`research/README.md`, `research/_index/manifest.jsonl`,
> `research/jurisdictions/`). **No `research/` directory exists in this
> worktree or on `github/main`.** The "national state-data survey" was
> therefore re-derived from primary sources: every URL cited below was
> fetched or probed live on 2026-08-08 (HTTP status, page text, or Socrata
> API response), and official `.gov` domains were used as the source of
> truth. No API, endpoint, or dataset was invented; where an interface is
> undocumented or unproven it is labeled as such.

Evidence rules applied (per repository conventions in `reports/` and
`docs/ingest/`):

* Official regulator pages and state open-data portals are primary evidence.
* Perplexity-style research reports were **not** used as evidence.
* Dashboards embedded via Looker Studio / Power BI / Tableau are treated as
  **undocumented and potentially unstable** (precedent: California DCC
  harvest report, `content/datasets/TDTS-0002.md`), so they are not counted
  as machine-readable sources unless a documented download/API also exists.
* A retailer/third-party description was never used to infer regulator
  behavior or data availability.
* "Boiling point is not a vaporizer setpoint" analog: a *reported* test
  result is not a regulatory *limit*. Testing-rules references are cited to
  regulation text, not to lab marketing.

Scoring rubric — every dimension scored **1–5** (5 = best for this project):

| Dimension | 5 means |
| --- | --- |
| Chemistry value | public numeric analyte/contaminant results at scale |
| Batch-level value | per-batch / per-sample test records (not just aggregates) |
| License value | complete, current license registry |
| Lab value | lab identity + lab-level test attribution |
| Machine readability | documented API / stable CSV/JSON downloads |
| Historical depth | multi-year back catalog retained |
| Source stability | dedicated, maintained publication surface |
| Ingestion complexity | low implementation effort (5 = easiest) |
| Privacy risk | low risk of publishing restricted/sensitive data (5 = safest) |

---

## 2. Shared ingest contract (what an adapter must provide)

Reference: `docs/ingest/OPERATOR.md`, `docs/ingest/implementation-report.md`,
`scripts/ingest/core.py`, `scripts/ingest/states/massachusetts.py`,
`scripts/dcc_ingest.py`. A state adapter owns **everything state-specific**;
the `scripts/ingest/` package owns everything generic:

**State adapter contract (per `massachusetts.py`):**

* `STATE` slug + `REGULATOR` identity dict (name, jurisdiction, code, site).
* `DATASETS` table of `DatasetDef`s: exact official URL, reporting period,
  expected schema, source disclaimers, clarifications. Archive the exact URL
  per snapshot.
* Per-dataset normalizers (source fields → canonical fields).
* `PRIVACY_SPEC`: excluded field names + per-entity allowlists.
* State terminology preserved verbatim (MA: "public health and safety
  advisory", never relabeled "recall").
* Page-generation policy: what pages to emit, relations/summaries, and the
  no-one-page-per-license aggregate rule.

**Shared machinery (reused as-is):** `Fetcher`/`FixtureFetcher` (retries,
content-type guards, streaming), `ArtifactStore` (immutable SHA-256 raw
snapshots), `SchemaSpec` + drift/row-collapse/duplicate-key/date-regression
guards, `NaturalKeyRegistry` stable IDs with tamper detection, `PrivacySpec`
scans, Markdown/Boris helpers, `ChangeReport` sync reports, `state_ingest.py`
CLI, and the publication gate chain (`ted_ids.py`, link audit,
`validate_graph.sh`).

---

## 3. Candidate verification (primary sources, 2026-08-08)

### 3.1 Nevada — Cannabis Compliance Board (CCB) ✅ strong

| Category | Verified source |
| --- | --- |
| Regulator | https://ccb.nv.gov/ (Nevada Cannabis Compliance Board) |
| License registry | https://ccb.nv.gov/license-search/ (searchable; ~4,617 records) and https://ccb.nv.gov/list-of-licensees/ |
| Testing-lab registry | `Testing Facility Name` field in lab data; approved labs appear in the Metrc extracts |
| Recalls/advisories | Public Health & Safety Bulletins (2023-01..03 verified; 2025-02 Amended PDF dated 2025-12-12); "Public Health and Safety Advisories" nav section; **machine-readable via WordPress REST API** `https://ccb.nv.gov/wp-json/wp/v2/posts?search=bulletin` (verified live) |
| Testing rules | NAC Chapter 453A; 2026 regulatory package R152-24-RP1 (adopted 2026-06-18) |
| Contaminant limits | NAC 453A panels |
| Machine-readable datasets | **Lab Library**: Metrc testing data, 2020 → previous month, monthly + full-year ZIP files of CSVs at `https://ccb.nv.gov/lab-library/` (verified; 2026.zip ≈ 28.7 MB) |
| Batch/product data | Per-sample `PackageLabSampleId`, `PackageLabel`, product category, quantity/UOM |
| Chemistry data | 14-column schema incl. `Test Type Name`, `Test Passed`, numeric result (README `READ_ME_FIRST_LAB_DATA.xlsx` verified) |
| Sales/plant data | Not published as open data; licensing data carries operator info |
| API/download | Manual ZIP downloads behind dated URLs (`ccbdownload.wpenginepowered.com/wp-content/uploads/YYYY/MM/…`); WP REST API for advisories; no SODA |
| Update cadence | Monthly (lab data "updated as of: July 1, 2026"); bulletins as issued |
| Historical availability | 2020–present, month by month |
| Public-use restrictions | None found on lab data; license search includes owner names/addresses |

### 3.2 Colorado — Marijuana Enforcement Division (MED) ✅

| Category | Verified source |
| --- | --- |
| Regulator | https://med.colorado.gov/ (MED, Dept. of Revenue) |
| Open-data portal | https://data.colorado.gov (Socrata) |
| License registry | `Licensed Marijuana Businesses in Colorado` (`93ae-ftjz`) is an **href view** pointing at the MED licensee lookup; MED Licensed Facilities + Licensee Lookup Tool on med.colorado.gov |
| Testing-lab registry | MED licensed facilities list |
| Recalls/advisories | MED enforcement activity + Final Administrative Enforcement Actions pages (no structured recall feed found) |
| Testing rules | Regulated Marijuana Rules (1 CCR 212-3) |
| Contaminant limits | 1 CCR 212-3 testing panels |
| Machine-readable datasets | Marijuana Sales by County (`j7a3-jgd3`, verified tabular, monthly, 2014–present, rows updated Aug 2026), Sales Revenue (`p6y8-s74x`), Tax revenue by county/city (`v9m8-x8dh`, `qvd3-njpu`), Tax & Fee Revenue (`3sm5-jtur`), medical registry stats (`5yqk-p422`) — all SODA |
| Chemistry data | Not public per-batch; MED Quarterly Market Update dashboard (METRC-derived, updated quarterly) is aggregate-only |
| Sales/plant data | Monthly sales by county, city, product classes (2014–present) |
| API/download | Socrata SODA + CSV exports |
| Update cadence | Monthly (sales), quarterly (dashboard) |
| Historical availability | 2014–present on portal |
| Public-use restrictions | Standard public data; addresses in license data |

### 3.3 Connecticut — Dept. of Consumer Protection (DCP) ✅

| Category | Verified source |
| --- | --- |
| Regulator | https://portal.ct.gov/DCP (DCP, Cannabis program) |
| Open-data portal | https://data.ct.gov (Socrata) |
| License registry | Cannabis Applications (`bqby-dyzr`); lottery/application reports (`w85q-8cfm`, `y64a-qj22`, `7kwc-wvc8`) |
| Testing-lab registry | Not found as a distinct public list |
| Recalls/advisories | DCP consumer alerts (not structured) |
| Testing rules | Connecticut cannabis testing regulations (DCP) |
| Contaminant limits | DCP regulations |
| Machine-readable datasets | **Cannabis Product Registry** (`egd5-wb6r`, 34,970 rows, verified): brand, dosage form, producer, THC/THCA/CBD/CBDA + terpenes (a-pinene, b-myrcene, b-caryophyllene, limonene, …), **`lab_analysis` COA URL** + label/product image links (hosted at `elicense.ct.gov`); sales by month/week (`f382-bnu5`, `ucaf-96h6`), price per gram (`ttwq-xhyz`), product-type sales (`twgv-a8qu`, `jyg4-yu7v`), avg product price (`crdh-m57i`), products sold (`t3s5-39as`), cannabis tax (`jey2-vq68`) |
| Chemistry data | **Product-level** analyte/terpene values + COA links (unique among candidates without per-batch results) |
| Batch/product data | Product-level, not batch-level |
| Sales/plant data | Retail sales + price by period and product type |
| API/download | Socrata SODA (verified live: `…/resource/egd5-wb6r.json` returns rows) |
| Update cadence | Weekly/monthly sales; registry updated as products register |
| Historical availability | Adult-use since Jan 2023; datasets cover from launch |
| Public-use restrictions | None found; COA documents are GUID URL links (link-stability caveat) |

### 3.4 Oregon — OLCC / OHA ✅

| Category | Verified source |
| --- | --- |
| Regulator | OLCC (adult-use) https://www.oregon.gov/olcc/ ; OHA (testing labs) https://www.oregon.gov/oha/ph/diseasesconditions/chronicdisease/medicalmarijuanaprogram/pages/laboratories.aspx |
| Open-data portal | https://data.oregon.gov (Socrata) |
| License registry | OLCC Cannabis Business Licenses & Endorsements (`h9xu-m9mv`, story view over table; metadata reports **Data Publishing Frequency: Daily**) |
| Testing-lab registry | OHA licensed testing laboratories page |
| Recalls/advisories | OLCC Product Recall Notices https://www.oregon.gov/olcc/pages/product-recalls.aspx (verified: pesticide/arsenic/mold-heavy-metal recalls 2021–2024) |
| Testing rules | OAR 333-007 (OHA) + OLCC rules; failed results must be reported to OHA/ODA |
| Contaminant limits | OAR 333-007 panels |
| Machine-readable datasets | OLCC Marijuana Market Data (`qutr-cyzn`), Cannabis Theft (`bsfq-7e4y`), Minor Decoy Operations (`5e3n-xpsm`), Cannabis Pesticide Guide List (`8xsj-gz6v`/`crm6-xdta`/`b8ki-p9ef`) |
| Chemistry data | **Not public per-batch** (results go to regulators; 2017 state audit questioned testing reliability) |
| Batch/product data | None public |
| Sales/plant data | Market data + theft + decoy datasets on Socrata |
| API/download | Socrata SODA/CSV; note: OLCC datasets are **story views** (embedded table needs resolution), and export endpoints intermittently returned HTTP 500 during probe |
| Update cadence | Daily (license data), periodic (others) |
| Historical availability | Long-lived portal; license/market data multi-year |
| Public-use restrictions | None found |

### 3.5 New York — Office of Cannabis Management (OCM) ✅

| Category | Verified source |
| --- | --- |
| Regulator | https://cannabis.ny.gov/ (OCM) |
| Open-data portal | https://data.ny.gov (Socrata) |
| License registry | **Current OCM Licenses** (`jskf-tt3q`, verified columns: license_number, license_type, status, issued/effective/expiration dates, entity_name, dba, address, county, region, tier_type, cultivation indoor/outdoor/mixed-light); Registered Retail Dealers (`gttd-5u6y` + map `75hy-mnme`); Cannabinoid Hemp Licenses (`4r7n-55mm`); Medical providers (`gegk-4ghy`) |
| Testing-lab registry | Not found as public dataset |
| Recalls/advisories | OCM press releases; no structured recall feed found |
| Testing rules | NY CRR Part 125 (OCM testing regulations) |
| Contaminant limits | Part 125 panels |
| Chemistry data | Not public |
| Machine-readable datasets | Full license registry via SODA (verified live) |
| Sales/plant data | Not on portal (published via reports) |
| API/download | Socrata SODA/CSV |
| Update cadence | Ongoing (licenses as issued) |
| Historical availability | Program launched 2022; datasets recent |
| Public-use restrictions | Addresses public in license data |

### 3.6 Washington — Liquor and Cannabis Board (LCB) ✅ (with legal caveat)

| Category | Verified source |
| --- | --- |
| Regulator | https://lcb.wa.gov/ (WA LCB) |
| Open-data portal | https://data.wa.gov — LCB Cannabis Renewal (`brpd-b6zd`), Local Authority Letters (`vgcw-qfjm`) |
| License registry | Frequently Requested Lists: `CannabisApplicants08042026.xlsx` (dated XLSX, active + pending-issued) |
| Testing-lab registry | `Lab-List-8-4-2026.xlsx` (approved testing labs); WSDA Cannabis Lab Analysis Program (agr.wa.gov) |
| Recalls/advisories | LCB press releases + public health notices; no structured feed found |
| Testing rules | WAC 314-55-102/109 (testing + quarantine) |
| Contaminant limits | WAC 314-55 |
| Machine-readable datasets | Dated **XLSX** files on `lcb.wa.gov/sites/default/files/…`: license applicants, medically endorsed stores (updated Tuesdays), approved infused products, enforcement visits, violations, compliance checks, sales activity by license number, FY2015–FY2025 sales & excise tax by county, local government distributions |
| Chemistry data | **Not public per-batch**: labs submit results to CCRS for LCB review; research dashboards "beginning stage" (verified `lcb.wa.gov/research/dashboards`) |
| Batch/product data | None public |
| Sales/plant data | Sales activity by license number; tax by county FY15–FY25 |
| API/download | No API; page-driven discovery of dated XLSX; no Socrata for the lists |
| Update cadence | Monthly for enforcement/sales lists; Tuesdays for medical endorsements |
| Historical availability | High — dated files retained since FY2015 |
| Public-use restrictions | **RCW 42.56.070(8): records may not be used for commercial purposes** (stated on the lists page) — legal gate before any derived publication |

### 3.7 Maine — Office of Cannabis Policy (OCP) ✅

| Category | Verified source |
| --- | --- |
| Regulator | https://www.maine.gov/dafs/ocp/ (OCP) |
| Open-data portal | https://www.maine.gov/dafs/ocp/open-data/adult-use |
| License registry | Applicant, Licensee, and Entity Search (interactive) |
| Testing-lab registry | Part of licensee search; OCP testing-lab certification rules |
| Recalls/advisories | OCP compliance data (violation data) |
| Testing rules | OCP testing rules (technical rulemaking in progress) |
| Contaminant limits | OCP rules |
| Machine-readable datasets | Retail sales data, compliance data, opt-in communities (dashboards/links); **testing data = aggregate sample reports** ("uploaded into an internal database, summarized and presented here for public information") |
| Chemistry data | Aggregate summaries only (e.g., 2023 contaminant-fail report) |
| Batch/product data | None public |
| API/download | No documented API |
| Update cadence | Quarterly reports (most recent quarterly report) |
| Historical availability | Adult-use since Oct 2020 |
| Public-use restrictions | None found |

### 3.8 Michigan — Cannabis Regulatory Agency (CRA) ✅

| Category | Verified source |
| --- | --- |
| Regulator | https://www.michigan.gov/cra |
| License registry | CRA "Find / Verify a CRA Licensed Professional or Business" |
| Testing-lab registry | CRA licensed lab list (on site) |
| Recalls/advisories | CRA press releases; no structured feed found |
| Testing rules | MRTMA rules |
| Contaminant limits | MRTMA panels |
| Machine-readable datasets | data.michigan.gov: CRA Scorecard (`kprp-u978`), Events (`d4pa-u9c8`) — thin; **monthly reports are PDFs** (`michigan.gov/cra/-/media/…/monthly-report/September-Monthly-Report-2025.pdf`, verified URL) |
| Chemistry data | Not public per-batch |
| Batch/product data | None public |
| Sales/plant data | Monthly PDF reports (sales, prices, license counts) |
| API/download | PDF downloads; irregular filename pattern ("August-2024" vs "September-Monthly-Report-2025") |
| Update cadence | Monthly |
| Historical availability | Monthly reports archived |
| Public-use restrictions | None found |

### 3.9 New Mexico — Cannabis Control Division (CCD) ✅

| Category | Verified source |
| --- | --- |
| Regulator | https://www.rld.nm.gov/cannabis/ (CCD, NMRLD) |
| License registry | Public License Search (Salesforce): https://nmrldlpi.my.site.com/ccd/s/public-license-search |
| Testing-lab registry | Part of license search |
| Recalls/advisories | CCD notices (not structured) |
| Testing rules | NMAC 16.8 / CCD rules |
| Contaminant limits | NMAC panels |
| Machine-readable datasets | C.R.O.P. data catalog https://crop.rld.nm.gov/data-catalog.html (downloadable datasets; page text verified, dataset list did not render in static fetch — contents unverified) |
| Chemistry data | Not public |
| API/download | Salesforce search UI; CROP downloads (format unverified) |
| Update cadence | Ongoing |
| Historical availability | Program since 2021/2022 |
| Public-use restrictions | CROP disclaimer: self-reported data, no warranty |

### 3.10 New Jersey — Cannabis Regulatory Commission (CRC) ✅ (weak)

| Category | Verified source |
| --- | --- |
| Regulator | https://www.nj.gov/cannabis/ |
| License registry | License awards totals published per public meeting (aggregate counts only) |
| Testing-lab registry | Aggregate counts (10 testing labs) |
| Recalls/advisories | CRC announcements |
| Testing rules | NJAC 17:30 |
| Contaminant limits | NJAC 17:30 panels |
| Machine-readable datasets | data.nj.gov: Cannabis Dispensary List (`8hz7-zvhn`); reports page = aggregate PDFs (quarterly sales totals, patient counts, applicant demographics) |
| Chemistry data | Not public |
| API/download | Socrata (one list); PDFs for stats |
| Update cadence | Quarterly (sales), as-issued (licenses) |
| Historical availability | Since 2021 |
| Public-use restrictions | None found |

### 3.11 Also considered (not ranked in top 10)

| State | Finding |
| --- | --- |
| Maryland (MCA) | Interactive Data Dashboard (cannabis.maryland.gov/pages/data-dashboard.aspx) + licensee pages; **no machine-readable datasets found** on data.maryland.gov; dashboard-only |
| Illinois (ILCC) | **No cannabis datasets on data.illinois.gov** (catalog query empty); reports on ILCC site, low machine readability |
| Arizona (ADHS) | Monthly PDF reports (medical program stats); no open data, no public results |
| Missouri (DHSS DCR) | Sales data dashboard (Oct 2020 → current) at health.mo.gov; dashboard-only, no documented API; seed-to-sale contract in flux (2026 RFP) — source-stability risk |
| Ohio (DCC) | Salesforce license search (elicense.com.ohio.gov); no open data |
| Mississippi (MMCP) | Single dataset on data.mmcp.ms.gov; tiny program |

---

## 4. Scores

| Rank | State | Chem | Batch | Lic | Lab | Mach | Hist | Stab | Cx (5=easy) | Priv (5=safe) | **Total** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Nevada | 5 | 5 | 3 | 5 | 4 | 5 | 4 | 3 | 4 | **38** |
| 2 | Colorado | 2 | 1 | 5 | 2 | 5 | 5 | 4 | 5 | 4 | **33** |
| 3 | Connecticut | 3 | 2 | 3 | 2 | 5 | 3 | 5 | 5 | 4 | **32** |
| 4 | Oregon | 1 | 1 | 5 | 2 | 5 | 5 | 4 | 4 | 4 | **31** |
| 5 | New York | 1 | 1 | 5 | 1 | 5 | 3 | 4 | 5 | 3 | **28** |
| 6 | Washington | 1 | 1 | 4 | 4 | 3 | 5 | 4 | 3 | 2 | **27** |
| 7 | Maine | 3 | 2 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | **25** |
| 8 | Michigan | 1 | 1 | 4 | 3 | 2 | 4 | 3 | 2 | 3 | **23** |
| 9 | New Mexico | 1 | 1 | 4 | 2 | 3 | 3 | 3 | 3 | 3 | **23** |
| 10 | New Jersey | 1 | 1 | 3 | 2 | 2 | 3 | 3 | 3 | 3 | **21** |
| — | Maryland | 1 | 1 | 3 | 2 | 2 | 3 | 3 | 3 | 3 | 21 |
| — | Illinois | 1 | 1 | 3 | 2 | 2 | 3 | 3 | 3 | 3 | 21 |
| — | Arizona | 1 | 1 | 3 | 2 | 1 | 4 | 3 | 2 | 3 | 20 |

Notes on judgment calls:

* **Michigan vs New Mexico tie (23):** Michigan ranked 9th on market size and
  license richness; New Mexico 10th because its CROP catalog contents are
  unverified and its market is small. Either order is defensible.
* **Connecticut vs Oregon (32 vs 31):** near-tie; Connecticut ranked ahead on
  **chemistry value** (product-level analytes + COA links), which is this
  project's differentiator. Oregon's license/market data is the larger, more
  mature ingest surface; if chemistry is deprioritized, swap 3 and 4.

---

## 5. Recommendations

### Next state: **Nevada** 🇺🇸

The only remaining state (after Massachusetts) that publishes **public
per-batch numeric test results**, with a 2020→present monthly archive. The
14-column Metrc lab extract maps almost directly onto the batch/laboratory
measurement model established in commit `2674afb`
(`tests/test_coa_model.py`): facility/lab/date/package-sample identity, test
type, pass/fail, and numeric result. Advisories are machine-readable via the
site's WordPress REST API. No commercial-use restriction was found.

Wave-1 Nevada scope (do **not** build all at once):

1. `lab-library` monthly ZIPs → lab-results + contaminant entities
   (start with 2026 monthly files; backfill 2020–2025 in a second pass).
2. License registry snapshot (`list-of-licensees` / `license-search`).
3. Public Health & Safety Bulletins via `wp-json` → advisory entities,
   preserving the regulator's "bulletin" terminology (per the MA
   never-relabel rule).

### States 2–5

| Pos | State | Why |
| --- | --- | --- |
| 2 | Colorado | Biggest mature market; 2014→present license/sales on Socrata (cheapest ingestion); quarterly METRC dashboard gives aggregate market signal. No chemistry. |
| 3 | Connecticut | Unique **product-level chemistry** (analytes/terpenes + COA links) + weekly sales/price data, all on Socrata; tiny market but high data density per dollar of implementation. |
| 4 | Oregon | Daily-updated OLCC license data, market/theft/decoy datasets, and a structured recall-notice page; large market. Requires Socrata story-view resolution; no chemistry. |
| 5 | New York | Cleanest license registry of the large markets (`data.ny.gov` SODA), full entity/tier/cultivation fields; new program (2022+) limits history and there is no chemistry. |

### States 6–10

| Pos | State | Why |
| --- | --- | --- |
| 6 | Washington | Richest license/lab/enforcement/sales **lists** (FY2015+ history) but XLSX-only, no API, no public results, and **RCW 42.56.070(8) prohibits commercial use of records** — needs a legal gate before any derived publication. |
| 7 | Maine | Aggregate testing summaries + licensee/compliance data; moderate value, low complexity. |
| 8 | Michigan | Very large market with monthly PDF reports; hard ingestion (PDF parsing), no chemistry. |
| 9 | New Mexico | Public license search + CROP catalog; contents of catalog unverified. |
| 10 | New Jersey | Aggregate statistics only; weakest machine readability of the ranked set. |

---

## 6. Architecture mapping: generic vs state-specific

### 6.1 Generic reusable ingestion behavior (build once in `scripts/ingest/`)

Already shared: acquisition, archival, schema guards, stable IDs, privacy
scans, Markdown emission, sync reports, publication gates (see §2).

**New generic modules this research justifies (candidate shared code):**

1. **`SocrataSource`** — one client for data.oregon.gov, data.colorado.gov,
   data.ct.gov, data.ny.gov, data.wa.gov, data.nj.gov, data.michigan.gov.
   Generic behavior: catalog discovery (`/api/catalog/v1`), SODA row queries
   (`/resource/{id}.json`), CSV export (`/api/views/{id}/rows.csv`),
   view metadata for update cadence/row counts, retry-on-5xx (Fetcher
   already retries; probes showed intermittent 500s). State adapter supplies
   only dataset IDs + column mappings. **Detail:** some views are `story`
   (Oregon: resolve embedded `tableId`) or `href` (Colorado license dataset:
   treat as a link, not data).
2. **`DatedFileIndex`** — page-driven discovery of dated artifacts (Nevada
   monthly ZIPs, Washington dated XLSX): fetch index page → discover links →
   immutable SHA-256 archival → row-identity comparison across releases.
   This is exactly the pattern Massachusetts uses for its `resource/*.csv`
   discovery, generalized.
3. **`ZipOfCsv` streaming reader** — Nevada lab library (28 MB+ monthly ZIPs;
   stream to disk, never fully in memory — mirrors MA testing-CSV handling).
4. **XLSX reader** — Washington lists (need a dependency decision: add
   `openpyxl` or convert server-side; unresolved).
5. **PDF-report ingestion** — Michigan/Arizona/New Jersey; fragile and
   low-value; **explicitly deferred** until chemistry/lab sources are
   exhausted.

### 6.2 State-specific adapter behavior (per state, in `states/<slug>.py`)

Everything in the §2 contract is state-specific: `REGULATOR`, `DATASETS`
table, normalizers, `PRIVACY_SPEC`, terminology, page-generation policy,
natural keys. Two examples of state-specific decisions the research surfaced:

* **Terminology**: Nevada publishes "Public Health and Safety Bulletins" /
  "Advisories"; Oregon publishes "Product Recall Notices"; Washington
  publishes press releases. The adapter must preserve each regulator's label
  (MA precedent: never relabel advisory as recall).
* **Natural keys**: Nevada `PackageLabSampleId` (Metrc) for lab results;
  OLCC license numbers; MED license numbers; CT registration numbers; NY
  license numbers; WA UBI/license numbers. Each needs its own
  `NaturalKeyRegistry` mapping.

### 6.3 Entity/graph mapping

New states create new **jurisdiction profiles** (`jurisdictions/TJUR-NNNN`)
and **dataset records** (`datasets/TDTS-NNNN`) following the California
pattern (`content/jurisdictions/TJUR-0001.md`, `content/datasets/TDTS-0001.md`).
Existing collections are reused:

* Testing rules → `requirements/TREQ-NNNN` (Nevada NAC 453A; Colorado
  1 CCR 212-3; Oregon OAR 333-007/OLCC; Washington WAC 314-55).
* Labs → `testing-laboratories/TSTL-NNNN` (Nevada testing facilities from lab
  data; Washington approved-lab list).
* Contaminants/analytes → `contaminants/TCNT-NNNN` (Nevada test types;
  Connecticut registry analytes).
* Recalls/advisories → `recalls/TRCL-NNNN` + `safety-advisories/TSAD-NNNN`
  (Nevada bulletins; Oregon recall notices), preserving terminology.
* Per-batch lab results (Nevada) → the **batch/laboratory measurement model**
  from `2674afb`; batch identity = `PackageLabSampleId`, measurements =
  (test type, numeric result), compliance = pass/fail flags.

### 6.4 Privacy and legal gates

* **Washington RCW 42.56.070(8)** — records "may not be used for commercial
  purposes". Publishing derived WA content may require legal review; rank
  WA ingest as archive-only until cleared.
* **Nevada** license search contains owner/member names and addresses — keep
  out of generated content per the existing `PRIVACY_SPEC` patterns (no
  addresses, no per-license pages).
* **Connecticut** COA/label documents are GUID URLs on `elicense.ct.gov` —
  treat as unstable link targets; do not hotlink images into content.
* Universal: no one-page-per-license, no lab/producer rankings, no numeric
  action limits without regulation-text confirmation (existing policy).

---

## 7. Primary-source verification ledger

All URLs verified live 2026-08-08 (HTTP 200 / API response / page text).

| State | URL(s) verified |
| --- | --- |
| Nevada | ccb.nv.gov, ccb.nv.gov/lab-library/ (2020–2026 ZIP index + README), ccb.nv.gov/license-search/, ccb.nv.gov/list-of-licensees/, ccb.nv.gov/wp-json/wp/v2/posts?search=bulletin, ccb.nv.gov/ccb-issues-public-health-and-safety-bulletin-2023-0{1,2,3}/, catalog.metrc.com |
| Colorado | data.colorado.gov (views 93ae-ftjz, j7a3-jgd3, p6y8-s74x, v9m8-x8dh, qvd3-njpu, 3sm5-jtur, 5yqk-p422), med.colorado.gov/data-and-resources, med.colorado.gov/rules |
| Connecticut | data.ct.gov (views egd5-wb6r [34,970 rows], f382-bnu5, ucaf-96h6, ttwq-xhyz, twgv-a8qu, t3s5-39as, crdh-m57i, jey2-vq68, w85q-8cfm, bqby-dyzr) |
| Oregon | data.oregon.gov (views h9xu-m9mv, qutr-cyzn, bsfq-7e4y, 5e3n-xpsm, 8xsj-gz6v), oregon.gov/olcc/pages/product-recalls.aspx, OHA testing-lab page |
| New York | data.ny.gov (views jskf-tt3q [columns verified], gttd-5u6y, 4r7n-55mm, gegk-4ghy) |
| Washington | lcb.wa.gov/records/frequently-requested-lists (dated XLSX links), lcb.wa.gov/research/dashboards, lcb.wa.gov/ccrs/faq, data.wa.gov (brpd-b6zd, vgcw-qfjm), catalog.data.gov record for brpd-b6zd |
| Maine | maine.gov/dafs/ocp/open-data/adult-use (+ testing-data page) |
| Michigan | michigan.gov/cra monthly-report PDF URL pattern, data.michigan.gov (kprp-u978, d4pa-u9c8) |
| New Mexico | rld.nm.gov/cannabis/, nmrldlpi.my.site.com/ccd/s/public-license-search, crop.rld.nm.gov/data-catalog.html |
| New Jersey | nj.gov/cannabis/resources/reports-stats-info/, data.nj.gov (8hz7-zvhn) |
| Others | cannabis.maryland.gov/pages/data-dashboard.aspx, data.illinois.gov (catalog query empty), azdhs.gov licensing pages, health.mo.gov cannabis data & reports, com.ohio.gov cannabis control, data.mmcp.ms.gov |

---

## 8. Uncertain claims left unresolved

* Oregon OLCC license dataset is a Socrata **story view**; the embedded table
  (`tableId 20469928`) and its SODA/export access were not fully resolved;
  export endpoints returned intermittent HTTP 500 during the probe.
* Nevada license registry export format: `license-search` is interactive;
  whether a full extract is downloadable from `list-of-licensees` was not
  confirmed.
* New Mexico C.R.O.P. catalog dataset list did not render in a static fetch;
  the set and formats of downloadable datasets are **unverified**.
* Michigan monthly-report URL pattern is inconsistent across months
  ("August-2024" vs "September-Monthly-Report-2025"); needs link discovery.
* Connecticut COA/label document GUID URLs: stability over time unverified.
* Washington LCB research dashboards are "beginning stage"; a future public
  testing-results surface may change the WA chemistry score.
* Missouri/Ohio/Maryland dashboards were treated as non-sources (no
  documented API); this is a classification, not a verification.
* Nevada lab-data ZIP internal layout (one CSV per date range per the README)
  was verified from the README text, not by unzipping a full-year archive.

---

## 9. Suggested next work

1. **Nevada adapter** (`scripts/ingest/states/nevada.py`) — wave 1: lab
   library 2026 monthly ZIPs → lab-results/contaminants against the batch/lab
   measurement model; license registry snapshot; bulletins via `wp-json`.
   Verify ZIP layout against one real archive first.
2. **`SocrataSource` shared module** — then Colorado (licenses + sales) and
   Connecticut (product registry + sales/price), the two cheapest high-value
   ingests.
3. **`DatedFileIndex` shared module** — Oregon (story-view resolution) and
   Washington (XLSX discovery, archive-only pending legal review).
4. Maine aggregate testing summaries; Michigan PDF monthly reports (deferred
   tooling decision); New Mexico CROP verification; New Jersey last.
5. Re-run the reconciliation/rebase checklist from
   `docs/ingest/implementation-report.md` §2 before any new state content is
   published.

---

## 10. Required report fields

* **Files added**: `docs/state-expansion-roadmap.md` (this document).
* **Files modified**: none in this commit (research-only).
* **Entities created**: none — planning document; no Boris content entities,
  IDs, or pages were created.
* **Graph relationships created**: none (no `relations` emitted).
* **Primary sources verified**: §7 ledger (all live-fetched 2026-08-08).
* **Uncertain claims left unresolved**: §8.
* **Validation results**: see below.
* **Research corpus records consumed**: `research/` is absent from this
  worktree; consumed instead: `docs/ingest/OPERATOR.md`,
  `docs/ingest/implementation-report.md`, `docs/ingest/audit.md`,
  `scripts/ingest/*` (core, fetch, storage, schema, ids, validation,
  markdown, diff, `states/massachusetts.py`), `scripts/dcc_ingest.py`,
  `data/dcc/manifest.json`, `content/jurisdictions/TJUR-0001.md`,
  `content/datasets/TDTS-0001.md` / `TDTS-0002.md`, `reports/README.md`,
  `reports/source-manifest.md`, and commit `2674afb` (batch/laboratory
  measurement model).
* **Suggested next work**: §9.

### Validation

* Every external URL in §7 was fetched or probed live during research
  (HTTP 200 / JSON API response / page text captured above).
* All internal references in this document point to existing repository
  files or commits; no Markdown link audit needed for `docs/` (outside the
  published `content/` tree), and the site build is unaffected by this
  docs-only change.
* No fixture or synthetic data was created; no APIs were invented; no
  state content was generated.
