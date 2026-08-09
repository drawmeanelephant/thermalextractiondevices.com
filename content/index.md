---
title: "Thermal Extraction Devices"
id: index
status: published
tags: ["thermal", "extraction", "devices", "home"]
---

# Thermal Extraction Devices

Welcome to the canonical technical archive for **Thermal Extraction Devices** (`thermalextractiondevices.com`).

This platform is an evidence-aware archive of thermal extraction and vaporization devices, manufacturer and device lineage, hardware architecture, cannabis chemistry, terpenes, cannabinoids, cultivars, products, batches, laboratories, jurisdictions, requirements, recalls, and safety documentation. Records distinguish source-attributed facts, editorial taxonomy, demonstrations, and unresolved research. The archive does not assert closed-loop industrial systems, firmware telemetry, engineering schematics, calibration services, or pressure-performance guarantees unless a published record supports the claim.

---

## Technical Collections

- **[Terpenes](terpenes.md)**: Volatile terpene profiles, boiling point references, and physical properties (`terpenes/TTRP-XXXX`).
- **[Cannabinoids](cannabinoids.md)**: Phytocannabinoid identity, physical properties, and thermal degradation context (`cannabinoids/TCBN-XXXX`).
- **[Botanicals](botanicals.md)**: Non-cannabis plant species sharing volatile terpene chemistry (`botanicals/TBOT-XXXX`).
- **[Cultivars](cultivars.md)**: Genetic lineage indices and cultivar overviews (`cultivars/TCUL-XXXX`).
- **[Products](products.md)**: Commercial producer products and packaged offerings (`products/TPRD-XXXX`).
- **[Lab Results](lab-results.md)**: COA records and clearly labeled synthetic demonstrations; no demo is evidence of a real batch (`lab-results/TLAB-XXXX`).
- **[Devices](devices.md)**: Source-attributed thermal extraction and vaporization hardware records (`devices/TED-XXXX`).
- **[Manufacturers](manufacturers.md)**: Manufacturer identity, product lineage, hardware architecture, materials, lifecycle, warranty, and recall records (`manufacturers/TMFR-XXXX`).
- **[Specifications](specs.md)**: Reserved for source-supported electrical, mechanical, and thermodynamic parameters (`specs/TSPEC-XXXX`).
- **[Safety & Compliance](safety.md)**: Safety records and source-supported hazard guidance; no empty pressure-performance promises (`safety/TSAFE-XXXX`).
- **[Reference](reference.md)**: Taxonomy, evidence grammar, and engineering reference tables (`reference/TREF-XXXX`).
- **[Guides](guides.md)**: Evidence-aware reading, lineage, COA, and specimen-format guidance (`guides/TGDE-XXXX`).
- **[Law & Use](law-and-use.md)**: Jurisdiction, licensing, requirements, recalls, and statutory-source records (`law-and-use/TLAW-XXXX`).
- **[Releases](releases.md)**: Reserved for documented hardware revisions and future release notes; no firmware or calibration claims are currently published (`releases/TREL-XXXX`).
- **[Changelog](changelog.md)**: Historical archive and data-model changes, not a record of unsupported field-service events (`changelog/TCHG-XXXX`).

---

## Cannabis Regulation & Public Data

Verified jurisdiction profiles and source-traceable regulatory records. The [Jurisdictions](jurisdictions.md) catalog covers all 50 U.S. states, Washington, D.C., U.S. territories, the federal context, and an international country layer, each with authority, program status, data surface, and provenance.

**Deep-data implementations** — jurisdictions with dedicated ingestion pipelines and published data records:

- **California (DCC)**: license registry, testing laboratories, recalls, contaminants, requirements, and aggregate datasets derived from California Department of Cannabis Control data. See the [California DCC Data Landscape](datasets/TDTS-0004.md) overview.
- **Massachusetts (CCC)**: the reference state adapter (`scripts/ingest/states/massachusetts.py`) with a verified open-data catalog; live ingestion pending a privacy-safe sync.

Related regulatory collections:

- **[Jurisdictions](jurisdictions.md)**: U.S. state/territory/federal and international jurisdiction profiles (`jurisdictions/TJUR-XXXX`).
- **[Licenses](licenses.md)**: Aggregate license counts and licensing summaries (`licenses/TLIC-XXXX`).
- **[Organizations](organizations.md)**: Licensed organizations and recall-involved businesses (`organizations/TORG-XXXX`).
- **[Testing Laboratories](testing-laboratories.md)**: Testing laboratory license records (`testing-laboratories/TSTL-XXXX`).
- **[Recalls](recalls.md)**: Cannabis recall notices and safety enforcement records (`recalls/TRCL-XXXX`).
- **[Contaminants](contaminants.md)**: Contaminant classes regulated under cannabis testing (`contaminants/TCNT-XXXX`).
- **[Datasets](datasets.md)**: Dated, source-traceable dataset snapshots and aggregate reporting surfaces (`datasets/TDTS-XXXX`).
- **[Requirements](requirements.md)**: Regulatory requirements and testing panels (`requirements/TREQ-XXXX`).

---

## Massachusetts CCC Data Collections

Source-traceable records derived from Massachusetts Cannabis Control Commission (CCC) open data (license tracker, testing results, public health and safety advisories, testing laboratories, contaminants, requirements, and aggregate datasets). See the [Massachusetts Cannabis Data Landscape](jurisdictions/TJUR-0075.md) overview.

- **[Jurisdictions](jurisdictions.md)**: State-level jurisdiction profiles (`jurisdictions/TJUR-XXXX`).
- **[Licenses](licenses.md)**: Aggregate license counts and licensing summaries (`licenses/TLIC-XXXX`).
- **[Organizations](organizations.md)**: Licensed organizations and advisory-connected licensees (`organizations/TORG-XXXX`).
- **[Testing Laboratories](testing-laboratories.md)**: Massachusetts Independent Testing Laboratories (`testing-laboratories/TSTL-XXXX`).
- **[Safety Advisories](safety-advisories.md)**: CCC public health and safety advisories, with the Commission's own terminology preserved (`safety-advisories/TSAD-XXXX`).
- **[Contaminants](contaminants.md)**: Contaminant classes regulated under cannabis testing (`contaminants/TCNT-XXXX`).
- **[Datasets](datasets.md)**: Dated, source-traceable dataset snapshots and aggregate reporting surfaces (`datasets/TDTS-XXXX`).
- **[Requirements](requirements.md)**: Regulatory requirements and testing panels (`requirements/TREQ-XXXX`).
- **[Affected Products](affected-products.md)**: Normalized package-level records from public health advisories (`affected-products/TAFP-XXXX`).

---

## Archival & Graph Architecture

This repository is compiled statically using **Boris** and deployed continuously to Cloudflare Pages.
