# Thermal Extraction Devices Roadmap

Last reviewed: 2026-08-08

This roadmap describes the long-term direction of thermalextractiondevices.com
as a structured knowledge graph covering thermal extraction devices,
manufacturers, cannabis products, laboratory testing, jurisdictions,
cultivars, terpene chemistry, and evidence.

The project is intended to become useful both as a human-readable reference and
as a machine-readable research corpus.

## North Star

Build a richly interconnected reference graph that can answer questions such
as:

- Which devices support a particular material or heating method?
- What models has a manufacturer produced over time?
- Which cannabis testing programs operate in a jurisdiction?
- Which laboratories test regulated cannabis products in that jurisdiction?
- Which commercial products and batches have measured terpene and cannabinoid
  profiles?
- Which cultivar names occur across producers, states, batches, and
  laboratories?
- How chemically consistent is a cultivar name across batches and regions?
- Which terpene combinations repeatedly occur together?
- Which products or cultivar labels cluster into similar measured chemotypes?
- Which researched or reported effects are associated with particular compounds
  or chemical profiles?
- Where are products with similar measured profiles available or documented?
- How strong is the evidence behind any claimed relationship?

The graph must preserve the difference between measured fact, regulatory fact,
manufacturer claim, breeder provenance, scientific evidence, inference, and
anecdotal report.

## Core graph

The central cannabis graph should converge on:

~~~text
cultivar identity
    ↓
producer
    ↓
commercial product
    ↓
batch / lot / package
    ↓
laboratory report
    ↓
measured analytes
    ├── cannabinoids
    ├── terpenes
    └── contaminants

batch / product
    ├── jurisdiction
    ├── licensed organization
    ├── testing laboratory
    ├── product form
    ├── regulatory program
    └── provenance
~~~

Measured chemistry should then support derived relationships:

~~~text
measured batch profiles
    ↓
normalized chemical vectors
    ↓
profile similarity / chemotype clusters
    ↓
cultivar-name comparison
    ↓
producer comparison
    ↓
regional comparison
    ↓
evidence-linked compound/profile associations
~~~

The device graph should remain independent but interoperable:

~~~text
manufacturer
    ↓
device family
    ↓
device model / revision
    ├── heating architecture
    ├── supported materials
    ├── temperature control
    ├── power system
    ├── chamber / airpath materials
    ├── accessories
    ├── manuals
    ├── warranty
    ├── safety notices
    └── lifecycle status
~~~

## Scientific guardrails

Cultivar names must never be treated as fixed chemical identities.

A claim such as “Blue Dream contains terpene X” is weaker than:

> Batch ABC of Product XYZ, sold as Blue Dream, measured terpene X at
> concentration Y according to laboratory report Z.

The second form is the preferred evidence unit.

Effect relationships must also carry evidence classes:

- human clinical
- human observational
- preclinical animal
- in vitro
- traditional use
- consumer-reported
- manufacturer claim
- breeder claim
- editorial inference
- unknown

The graph may expose associations and patterns but must not convert
correlation into medical causation.

## Phase 1 — Foundation

### Goal

Make the data model stable enough that large-scale ingestion does not require
repeated restructuring.

### Deliverables

- stable entity-ID system with cross-state collision prevention
- deterministic Boris builds
- provenance requirements
- dataset manifests and immutable snapshots
- privacy and publication allowlists
- one state-adapter architecture and canonical CLI
- batch and COA entity model
- product-form taxonomy
- evidence classifications
- device specification schema
- manufacturer identity schema
- historical and superseded-record handling
- source freshness metadata
- automated graph validation
- automated privacy validation
- fixture-versus-live-data guards

### Exit criteria

A new manufacturer, device family, state program, laboratory dataset, or batch
dataset can be added without inventing a new architecture.

## Phase 2 — Device encyclopedia

### Goal

Build a broad historical and current catalog of thermal extraction devices.

### Coverage targets

- Milestone A: 25 manufacturers and 100 device models.
- Milestone B: 75 manufacturers and 400 device models or revisions, including
  historical and discontinued models.
- Milestone C: 150 or more manufacturers and 1,000 or more devices, revisions,
  and historically significant models.

Coverage should include portable, desktop, butane-powered, ball-vape,
log-vape, conduction, convection, hybrid, and niche architectures.

Manufacturer records should eventually include canonical identity, aliases,
operating status, official sources, product families, manuals, warranty and
repair policies, safety notices, ownership changes, historical models, and
discontinued lines.

Device records should eventually include model and revision, release period,
lifecycle status, heating architecture, heat source, supported material,
temperature range and control method, chamber and airpath claims, power
system, charging, dimensions, weight, accessories, official manuals,
manufacturer claims, independently verified facts, warranty, and safety
information.

## Phase 3 — State cannabis programs

### Goal

Build reusable state-level regulatory and testing datasets.

### Coverage targets

- Initial target: approximately 10 high-value jurisdictions with strong public
  data availability or major regulated markets.
- Expansion target: 25 state programs.
- Long-term target: 40 or more state or territorial programs where authoritative
  public data can be obtained.

Each jurisdiction should model the regulator, program, license classes,
licensed organizations, active testing laboratories, testing requirements,
contaminant limits, sampling rules, remediation and retesting, recalls,
public-health advisories, traceability systems, packaging and labeling
requirements, historical rule versions, effective dates, and source revisions.

State adapters should share retrieval, checksums, immutable snapshots, schema
drift checks, stable IDs, privacy filtering, normalization, Markdown
generation, graph validation, and publication reporting. State-specific code
should contain only source and regulatory peculiarities that cannot reasonably
be generalized.

## Phase 4 — Laboratory network

Represent testing laboratories, laboratory licenses, public accreditations,
jurisdictions, testing methodologies, regulatory analytes, datasets, and
laboratory-result records.

The graph should connect laboratories to jurisdictions, licenses, testing
programs, analytes, reports, and tested batches. Laboratory rankings or quality
judgments must not be inferred solely from public testing distributions.

## Phase 5 — Batch and COA graph

Make measured cannabis chemistry one of the primary data layers:

~~~text
producer
→ product
→ batch / lot / package
→ laboratory
→ report
→ measured analytes
~~~

Preserve the original product name, cultivar string, producer, batch, package
identifier, laboratory, jurisdiction, test date, sample date when available,
cannabinoid, terpene and contaminant values, units, detection limits, source
document, report revision, and correction or supersession history.

No measurement should float free from its batch or report.

## Phase 6 — Cultivar identity graph

Turn cultivar names from isolated encyclopedia entries into graph nodes
connecting breeder provenance, aliases, claimed lineage, producer products,
batches, laboratory reports, jurisdictions, measured profiles, candidate
chemotype clusters, and historical references.

Do not automatically merge similar names. Alias relationships require evidence.
Names such as Blue Dream, Blue Dream #5, Blue Dream Haze, and Blue Dream x ...
must receive separate treatment until evidence supports a relationship.

## Phase 7 — Terpene and cannabinoid profile intelligence

Use laboratory data to derive terpene prevalence, cannabinoid prevalence,
co-occurrence, normalized profile similarity, chemical-profile clusters,
within-cultivar variability, between-producer variability, geographic and
temporal variability, product-form variability, and detectable
laboratory-method variability.

The graph should be able to show that a cultivar name is chemically
consistent, heterogeneous, producer-dependent, or region-dependent rather than
assuming uniformity.

## Phase 8 — Effects and evidence graph

Connect compounds to evidence, biological targets or mechanisms, and
investigated effects. Connect measured profiles to constituent compounds and
clearly labeled evidence-linked associations.

Avoid “strain name → guaranteed effect.” Prefer:

~~~text
measured profile
→ compounds present
→ evidence associated with those compounds
→ clearly labeled confidence and evidence class
~~~

Consumer-reported effects may become a separate dataset later but must remain
distinct from clinical or mechanistic evidence.

## Phase 9 — Geography and availability

Connect jurisdictions to licensed producers, products, cultivar labels, and
measured batches; and connect jurisdictions to laboratories, reports, and
observed profiles.

Retail availability is highly time-sensitive and must remain separate from
historical regulatory records.

## Phase 10 — Graph discovery

Turn the accumulated records into a navigable research system through entity
pages, related-record panels, state and manufacturer filters, product-form and
analyte filters, cultivar and terpene filters, evidence filters, timeline
views, provenance displays, source freshness, historical state, and
profile-similarity navigation.

Potential derived pages include:

- cultivars commonly measured with terpinolene dominance
- cultivars showing high batch-to-batch terpene variability
- producers with repeated chemically similar batches
- terpene pairs frequently observed together
- regional differences for products sold under the same cultivar name
- devices supporting both flower and concentrates
- historical device families by heating architecture

## Quantitative long-term targets

These are direction-setting targets rather than promises:

- 150 or more manufacturers
- 1,000 or more device models
- 40 or more jurisdictions
- comprehensive laboratory coverage within supported states
- 2,500 or more cultivar identities
- 25,000 or more commercial products
- 250,000 or more measured batches
- 250,000 or more laboratory reports
- millions of analyte measurements
- thousands of official source records

The database should scale beyond these targets without requiring an
architectural rewrite.

## Quality over raw count

Every expansion milestone must preserve stable IDs, source attribution,
retrieval dates, jurisdiction, entity boundaries, units, batch ownership,
evidence class, historical versions, deterministic builds, privacy rules,
fixture isolation, and graph integrity.

A million measurements with lost provenance are less valuable than ten
thousand measurements whose lineage is fully traceable.

## Current strategic priority

The immediate sequence is:

1. Stabilize the multi-state ingestion architecture.
2. Resolve public-data storage and privacy policy.
3. Expand manufacturer and device coverage.
4. Add additional high-value state programs.
5. Grow the laboratory and batch/COA graph.
6. Normalize analyte measurements across jurisdictions.
7. Grow cultivar-to-batch relationships.
8. Introduce profile similarity and clustering.
9. Add evidence-linked compound/effect relationships.
10. Build geographic and graph-discovery features on the accumulated corpus.

The project should grow outward from trustworthy source records rather than
inward from assumptions about cultivar names or effects.

## Execution relationship

This document is strategic and changes infrequently. Current implementation
state, blockers, owners, branch lanes, and next actions live in
docs/status.md and docs/status/states/. Historical completed changes belong in
content/changelog/.
