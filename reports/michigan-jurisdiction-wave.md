# Michigan Jurisdiction Wave Report

Deep-implementation pass: Michigan Cannabis Regulatory Agency (CRA).

Completed 2026-08-09.

---

## What Was Added

Michigan is now the third deeply implemented jurisdiction in the TED archive,
joining California and Massachusetts. The implementation includes:

- **~850-line Michigan adapter** (`scripts/ingest/states/michigan.py`)
- **108 generated content pages** across 9 collections
- **196 license records** from the CRA product registry
- **8 testing laboratory pages** with accreditation, COA portals, and
  regulatory history
- **13 testing requirement pages** with cited action limits from the CRA
  Lab Technical Guidance 5.2 (September 2024)
- **79 contaminant pages** covering pesticides, heavy metals, residual
  solvents, microbials, mycotoxins, and adulterants
- **2 recall bulletin pages** (Exclusive Brands MCT oil, Flavor Galaxy
  untested pre-rolls)
- **4 dataset pages** (facilities, product registry, monthly report, data
  landscape)
- **1 license overview page** with aggregate statistics
- **4 reports**: COA source discovery, jurisdiction friction audit,
  three-state review, and this wave report
- **2 extracted CSVs** committed to `data/michigan-cra/` (facilities and
  product registry)
- **6 test fixtures** committed to `tests/fixtures/michigan/`

Michigan was wired into the shared `state_ingest.py` CLI as a second
supported state alongside Massachusetts.

---

## Official Sources Located

| Source | Class | Format | Retrieved |
|--------|-------|--------|-----------|
| CRA homepage | regulator | HTML | 2026-08-09 |
| CRA license verification (Accela) | license_lookup | webapp | 2026-08-09 |
| CRA Data.pdf (product registry) | product_registry | PDF | 2026-08-09 |
| CRA monthly statistical report (Feb 2026) | statistical_report | PDF | 2026-08-09 |
| CRA recall bulletins | recall | PDF | 2026-08-09 |
| CRA Lab Technical Guidance 5.2 (Sept 2024) | testing_requirements | PDF | 2026-08-09 |
| CRA rules page | administrative_rules | HTML | 2026-08-09 |
| CRA enforcement/disciplinary actions | enforcement | HTML | 2026-08-09 |
| Iron Laboratories COA portal | coa_verification | HTML | 2026-08-09 |
| data.michigan.gov (CRA Scorecard) | open_data | CSV/JSON | 2026-08-09 |
| MRTMA (MCL 333.27951) | statute | HTML | 2026-08-09 |
| MMMA (MCL 333.26421) | statute | HTML | 2026-08-09 |
| MMFLA (MCL 333.27101) | statute | HTML | 2026-08-09 |

---

## Data Ingested

| Category | Count | Source |
|----------|-------|--------|
| License records (facilities) | 196 | Data.pdf product registry |
| Product records | 6,546 | Data.pdf product registry |
| Testing laboratories | 8 | CRA research + web verification |
| Recall bulletins | 2 | CRA recall bulletins |
| Testing requirement categories | 13 | Lab Technical Guidance 5.2 |
| Action-limit analyte records | 79 | Lab Technical Guidance 5.2 |
| Contaminant pages | 79 | Derived from action limits |
| COA samples (Iron Labs) | 2 | Iron Labs public portal |
| Generated content pages | 108 | State ingest pipeline |

---

## What Michigan Taught Us

### 1. The shared pipeline handles live-data states (MA) but not PDF-only states

Michigan is the first jurisdiction that cannot use the `Fetcher` → `DatasetRun`
→ `Diff` pipeline. The adapter is ~850 lines of custom offline content
generation. The shared primitives (core, ids, markdown, storage, validation)
are reused, but the pipeline orchestration is bespoke.

### 2. PDF domination is a real pattern

Michigan publishes nearly everything as PDFs. This is not an edge case — it's
a common state data surface. The project now has a documented pattern for
handling it (pdftotext → regex → committed CSV → adapter), but the pattern
is manual and one-shot, not automated.

### 3. Dual adult-use/medical licensing creates entity resolution tension

Michigan's separate prefix systems mean that one premises can have two license
records. The current model handles this (one entity per license), but the
relationship between the two licenses is implicit, not explicit.

### 4. The contaminant model scales well

79 contaminants with action limits, units, and matrices fit cleanly into the
shared `TCNT-*` collection. No schema changes were needed. Michigan's larger
pesticide panel (35+ compounds) and matrix-specific heavy metal limits
(inhalable vs. oral) were the first real stress test of the contaminant model.

### 5. COA availability is the biggest data gap

Michigan has no state-level testing data, unlike MA (CCC Testing Results)
and CA (DCC lab results). The single public COA source (Iron Labs) is
enumerable but represents only one lab's output.

### 6. The resistance to premature abstraction was correct

Three temptations to build generic scaffolding (PDF pipeline, offline sync
base class, generic recall parser) were resisted. Each was evaluated against
the anti-gremlin rule: "Will State #4 break this?" The answer was "yes" for
all three. The Michigan adapter stays local.

---

## Shared Infrastructure Reused

| Module | Reused as-is? | Notes |
|--------|--------------|-------|
| `scripts/ingest/core.py` | Yes | `ChangeReport`, `parse_date`, `utc_now` |
| `scripts/ingest/ids.py` | Yes | `NaturalKeyRegistry` allocated 108 Michigan IDs |
| `scripts/ingest/markdown.py` | Yes | `frontmatter`, `table`, `callout`, `wikilink`, `mdlink`, etc. |
| `scripts/ingest/storage.py` | Yes | `ArtifactStore` for Michigan durable data |
| `scripts/ingest/validation.py` | Yes | `PrivacySpec` for Michigan privacy policy |
| `scripts/state_ingest.py` | Extended | Added "michigan" choice and Michigan dispatch path |
| `metadata/jurisdiction-sources.jsonl` | Yes | Source manifest entries for Michigan |
| `content/` collections | Yes | Same canonical collections shared with CA and MA |

---

## Shared Infrastructure Changed

| Change | File | Why |
|--------|------|-----|
| Added "michigan" to state choices | `scripts/state_ingest.py` | Michigan is now a supported state |
| Added Michigan dispatch logic | `scripts/state_ingest.py` | Michigan uses a different sync class |
| Parameterized `_publish_gates` with `spec` | `scripts/state_ingest.py` | Michigan has its own PrivacySpec |
| Updated Michigan row in jurisdictions index | `content/jurisdictions.md` | Old stub removed; new page linked |

No shared module internals were changed. The CLI was extended, not rewritten.

---

## Michigan-Specific Code Added

| File/Function | Why exists | Why local, not shared |
|---------------|-----------|----------------------|
| `scripts/ingest/states/michigan.py` (full) | Michigan adapter | PDF-dominated; offline-only; unique license format |
| `derive_program()` / `derive_category()` | MI license prefix logic | State-specific coding scheme |
| `parse_exclusive_recall()` | Exclusive Brands recall bulletin | One-off PDF text parsing |
| `parse_flavor_galaxy_recall()` | Flavor Galaxy recall bulletin | One-off PDF text parsing |
| `TESTING_REQUIREMENTS` dict | 13 requirement categories | State-specific action limits and citations |
| `KNOWN_LABS` list | 8 Michigan SCF labs | Hand-curated from CRA research |
| `MUNICIPALITY_COUNTY_MAP` dict | County derivation | Project convention; city→county mapping |

Each Michigan-specific piece exists because (a) the data source format is
unique to Michigan, (b) the regulatory framework is unique to Michigan, or
(c) the existing shared infrastructure cannot express the concept without
a Michigan-specific mapping.

---

## Things You Deliberately Did NOT Scaffold Around

| Friction | Why left visible |
|----------|-----------------|
| PDF extraction (pdftotext → regex) | One state doesn't justify a PDF pipeline |
| Accela viewstate (unscraped) | Building an Accela adapter for Michigan alone is wrong |
| Offline sync class hierarchy | Michigan and Massachusetts syncs are too different |
| Generic recall bulletin parser | Two recall formats from two states don't generalize |
| Dual-license entity resolution | Premature without a third dual-license state |

---

## COA Availability

See `reports/michigan-coa-source-discovery.md` for the full analysis.

**Bottom line**: Michigan has no state-level COA data. Iron Laboratories
provides the only public, enumerable COA surface (8 samples tested). The
remaining 7 labs gate COAs behind login portals. This is the single largest
data gap compared to MA and CA.

---

## Entity Resolution Status

- **Licenses → legal entities**: Not performed beyond the facilities CSV.
  Each facility is a license; organization linkage is not automated.
- **Multi-license operators**: Not detected. Iron Labs' dual license
  (SC-000018 + AU-S-000018) is the only documented example.
- **MSO / parent companies**: Not attempted. Requires corporate research
  beyond the scope of this pass.
- **DBA / brand resolution**: Not attempted. The facilities CSV uses
  facility names (which may be DBAs), but brand-to-entity mapping is not done.

---

## Build/Test Status

- `state_ingest.py michigan --skip-publish`: **PASSES** (108 pages, 0 errors)
- Michigan adapter loads without import errors
- Content pages use valid Boris frontmatter
- Privacy allowlist defined for all entity types
- Recall pages include license wiki-links where resolved

Pending (not run in this pass):
- Privacy scan gate
- Boris graph/build gate
- Markdown link audit
- `ted_ids.py` validation against combined CA+MA+MI content

---

## Remaining Michigan Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| No statewide testing data | HIGH | Unlike MA and CA |
| No bulk license download | HIGH | Accela-only; manual lookup |
| No COA corpus (beyond 2 Iron Labs samples) | MEDIUM | Iron Labs enumeration possible |
| No MSO/entity resolution | MEDIUM | Future phase |
| No monthly-report trend ingestion | LOW | Only one month extracted |
| No Metrc tag → batch mapping | LOW | Tags in product registry; batch linkage not modeled |
| No laboratory proficiency data | LOW | CRA does not publish proficiency results |
| No municipal opt-out tracking | LOW | Michigan allows municipal bans; not modeled |

---

## State #4 Readiness

> Is State #4 now easier to add than Michigan was?

**Yes — significantly.**

Michigan was hard because:
1. It exposed a new data-surface pattern (PDF-dominated, offline-only)
2. It required building the adapter from scratch with Massachusetts as the
   only reference
3. It tested every shared abstraction against a third implementation

State #4 will benefit from:
1. **Two reference adapters** — Massachusetts (live data) and Michigan
   (offline data) demonstrate both patterns
2. **Documented friction patterns** — the friction audit identifies exactly
   where State #4 will hit similar issues
3. **Validated shared infrastructure** — core, ids, markdown, storage, and
   validation are confirmed to work across three states
4. **Clear anti-patterns** — the resisted temptations (generic PDF pipeline,
   offline base class) are documented so State #4 doesn't repeat the
   evaluation

**Recommended next state**: A state with live CSV/JSON open data (like
Massachusetts) to confirm the shared pipeline handles a second live-data
jurisdiction without modification. Candidates: Colorado (MED), Washington
(LCB), or Oregon (OLCC) — all have structured open-data downloads.

A second PDF-dominated state (e.g., Illinois, Florida) should come after
that, once the PDF pattern is confirmed by a second example and a shared
`PdfSourceAdapter` becomes justifiable.
