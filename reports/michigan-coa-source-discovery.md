# Michigan COA Source Discovery

Systematic survey of certificate-of-analysis (COA) availability for Michigan
cannabis products, conducted 2026-08-09.

## Summary

Michigan's COA landscape is **fragmented across individual laboratory portals**.
There is no state-level COA verification system, no statewide open-data release,
and no public API. Only one laboratory (Iron Labs) provides publicly enumerable
COA pages. The remaining laboratories gate COA access behind login portals,
batch-ID lookup forms, or QR codes.

## Discovered Systems

### Iron Laboratories (Iron Labs)

- **Access**: Public web pages at `https://results.ironlaboratories.com/sample/{id}`
- **Enumeration**: ID sequence appears sequential; pages are publicly accessible
  without authentication
- **Report format**: Structured HTML with tables for each analyte panel
- **Sample IDs tested**: 160047 (concentrate sample), 163182 (flower sample)
- **Data captured**: Analyte names, results, LOD, LOQ, pass/fail, method references
- **Ingestion suitability**: **High**. Deterministic HTML parsing; enumerable IDs;
  no rate-limiting detected during research scraping
- **Caveats**:
  - ID space is unbounded; not all IDs return valid reports
  - Only Iron Labs' own results — no multi-lab coverage
  - No direct producer/brand linkage in the report URL
  - Historical availability before ~2022 unknown
- **Caveat emptor**: Iron Labs had a 2019 CRA settlement for test result
  discrepancies ($100,000 fine). Reports from that period should carry an
  explicit provenance note.

### PSI Labs

- **Access**: `https://results.thepsilabs.org/` — login-gated portal
- **Enumeration potential**: **None** without credentials
- **Format**: QR codes on product labels link to restricted result pages
- **Caveats**: No public enumeration surface discovered

### ACT Laboratories

- **Access**: Private portal; batch ID lookup required
- **Enumeration potential**: **None** without known batch IDs
- **Caveats**: No public enumeration surface discovered

### North Coast Testing Laboratories

- **Access**: Private portal
- **Enumeration potential**: **None**
- **Caveats**: Limited public documentation of the portal

### Steadfast Labs

- **Access**: Private portal
- **Enumeration potential**: **None**
- **Caveats**: No public COA surface discovered

### Viridis Laboratories

- **Access**: Private portal (`viridislabs.com`)
- **Enumeration potential**: **None**
- **Historical note**: 2021 CRA recall of Viridis-tested products (potency
  inflation concern). Viridis sued the CRA; the recall was partially rescinded
  after settlement. This episode highlights the absence of mandatory
  inter-laboratory proficiency testing in Michigan at that time.
- **Caveats**: Historical results should carry provenance notes about the
  2021 testing dispute

### Cambium Analytica

- **Access**: Private portal (`cambiumanalytica.com`)
- **Enumeration potential**: **None**

### Candid Testing

- **Access**: Unknown — no public website or portal discovered
- **Enumeration potential**: **None**

## Producer/Retailer COA Availability

A limited survey of Michigan dispensary and producer websites found:

- **Most producers do not publish COAs** on their public-facing product pages
- **Dispensary menus** (Leafly, Weedmaps, Dutchie) occasionally link to lab
  results, but links are not systematic or machine-discoverable
- **QR codes on product packaging** commonly link to COA pages, but these
  are per-package and not enumerable without physical product access

## Regulator-Published COAs

The CRA does **not** publish COAs, batch-level test results, or laboratory
performance data. The only regulator-published documents containing test
results are:

- **Recall bulletins**: Occasionally reference specific analytes (e.g., MCT
  oil in the Exclusive Brands recall; untested distillate in the Flavor
  Galaxy recall)
- **Laboratory Technical Guidance**: Describes required panels and action
  limits but does not publish actual results

## Ingestion Feasibility Assessment

| System | Public? | Enumerable? | Structured? | Suitability |
|--------|---------|-------------|-------------|-------------|
| Iron Labs | Yes | Yes (sequential) | HTML tables | High |
| PSI Labs | Login req. | No | Unknown | None |
| ACT Labs | Login req. | No | Unknown | None |
| North Coast | Login req. | No | Unknown | None |
| Steadfast | Login req. | No | Unknown | None |
| Viridis | Login req. | No | Unknown | None |
| Cambium | Login req. | No | Unknown | None |
| Candid | Unknown | No | Unknown | None |

## Comparison with MA and CA

| Dimension | California (DCC) | Massachusetts (CCC) | Michigan (CRA) |
|-----------|------------------|---------------------|----------------|
| State-level COA data | Yes (DCC lab results) | Yes (CCC Testing Results) | **No** |
| Multi-lab coverage | Yes (all licensed labs) | Yes (anonymized) | **No** |
| Public lab portals | Varies by lab | Varies by lab | Iron Labs only |
| Batch-level traceability | Metrc IDs in state data | Metrc IDs in state data | Metrc only (not public) |

## Recommendations

1. **Ingest Iron Labs COAs** as a heterogeneous sample corpus (flower,
   concentrate, edible categories) to validate the CA/MA normalization model
   against a third state's report format
2. **Document the Iron Labs COA parser** as a Michigan-specific adapter that
   lives alongside the shared COA model, not inside it
3. **Do not attempt to enumerate the full Iron Labs ID space** until the
   normalization model is confirmed to handle Michigan report layouts
4. **Note the COA gap** as a significant Michigan data limitation — unlike
   MA and CA, Michigan has no multi-lab, state-level testing data surface
