---
id: cannabinoids/TCBN-0006
title: "Cannabigerolic Acid (CBGA)"
parent: cannabinoids
status: published
tags: ["cannabinoid", "phytocannabinoid", "acid", "precursor"]
relations: [relates_to=cannabinoids/TCBN-0005, relates_to=cannabinoids/TCBN-0001, relates_to=cannabinoids/TCBN-0002, relates_to=cannabinoids/TCBN-0003, relates_to=cannabinoids/TCBN-0007]
summary: Shared biosynthetic precursor of the major cannabinoid acids; no measured atmospheric boiling point because decarboxylation precedes boiling.
---

# Cannabigerolic Acid (CBGA)

## Identity

| Property | Value |
| --- | --- |
| Preferred name | Cannabigerolic acid (CBGA) |
| IUPAC name | (2E)-3-(3,7-dimethylocta-2,6-dien-1-yl)-2,4-dihydroxy-6-pentylbenzoic acid |
| CAS number | 25555-57-1 |
| PubChem CID | 6449999 |
| InChIKey | SEEZIOZEUUMJME-FOWTUZBSSA-N [^1] |
| Molecular formula | C22H32O4 |
| Molecular mass | 360.49 g/mol (exact 360.2301 Da) |
| Compound class | Phytocannabinoid; olivetolic-acid derivative; meroterpenoid |
| Stereochemistry | No chiral centers; the (2E) geranyl geometry is natural. The (2Z) isomer is theoretically possible but not reported in nature [^1] |
| Major synonyms | Cannabigerolic acid, CBGA; decarboxylation product is CBG |

### Identity notes

- CBGA shares the molecular formula C22H32O4 with other acid isomers; LC-MS/MS with MRM transitions is required to resolve co-eluting acids [^1].
- The geranyl (C10) side chain distinguishes CBGA (C22) from the C5-side-chain CBGVA (C17); confirm by MS/MS fragment at m/z 319 (geranyl loss) [^1].

## Physical properties

| Property | Value | Conditions / Notes |
| --- | --- | --- |
| Melting point | ≈138–142 °C (decomposition) | Cayman Chemical CRM CoA; decomposes on melting [^2] |
| Boiling point | **Not experimentally determined at 1 atm** — thermally labile, decomposes before boiling. Reported "425 °C" values are predictions for neutral CBG, not CBGA [^2] |
| Vapor pressure | <10⁻⁶ Torr at 25 °C (estimated) | Acidic cannabinoids are far less volatile than neutrals [^2] |
| logP (octanol-water) | 5.8 (computed) | Acidic proton lowers logP vs. CBG (≈7.1) |
| Water solubility | <1 mg/L (practically insoluble) | Soluble in ethanol, methanol, acetonitrile |
| Thermal degradation onset | ≈110 °C (decarboxylation in plant matrix); 250 °C at GC injector | Primary pathway: CBGA → CBG [^2] |
| Oxidation / light sensitivity | High; phenolic dihydroxy motif; UV accelerates decarboxylation and oxidation | Store under inert gas, amber, −20 °C [^2] |
| Known degradation products | CBG (decarboxylation); CBC, CBL, CBSA (cannabielsoic acids), quinones (secondary) | [^2] |

> **Boiling point is not a device setpoint.** Blog figures such as "CBGA boils at 180 °C" are unreferenced marketing values; CBGA decomposes at 1 atm and no intact acid boiling point exists.

## Thermal-extraction context

{{include includes/boiling-point-vs-device-note.md}}

CBGA has negligible volatility at ambient temperature; thermal release from botanical matrix follows decarboxylation to neutral CBG, which then evaporates. Device setpoints must be established empirically, not from boiling-point tables.

## Cannabis occurrence

CBGA is the shared precursor of THCA, CBDA, and CBCA and is usually a minor measured analyte in mature flower, except in Type IV (CBG-dominant) material. Values are batch- and report-attached; no universal cultivar claim is made. Consult [Lab Results](../lab-results.md) for batch-level measurements.

## Biosynthesis and processing

CBGA is biosynthesized from geranyl diphosphate (GPP) and olivetolic acid by geranylpyrophosphate:olivetolate geranyltransferase (GOT). CBGAS/CBDAS/THCAS/CBCAS then cyclize or oxidize CBGA into the major acid cannabinoids; the relative synthase expression determines chemotype [^2].

## Reported biological activity

### Human evidence
No verified controlled human study of isolated CBGA was identified for this archive [^3].

### Preclinical animal and in vitro evidence

{{include includes/preclinical-evidence-note.md}}

Preclinical studies report CBGA effects on ion channels and inflammatory signaling in vitro at micromolar concentrations; no human-relevant effect at consumer doses is established [^3].

### Industry claims
"CBGA is the mother of all cannabinoids" is a reasonable biosynthetic description but is often used as a marketing claim; health claims for CBGA lack controlled human evidence [^3].

## Degradation products

- Primary: CBG (decarboxylation)
- Secondary: CBC, CBL, CBSA, quinones (heat/light/air)

## Sources

[^1]: PubChem CID 6449999, Cannabigerolic acid (CAS 25555-57-1). Verified 2026-08-08.
[^2]: Research-corpus dossier research/compounds/cannabinoids/cbga/artifact.md (CRM CoA melting point, decarboxylation kinetics, vapor-pressure analogy per PMC10249740). Not all ledger items re-verified in this wave.
[^3]: Research-corpus dossier research/compounds/cannabinoids/cbga/artifact.md evidence table; no human trials identified.

## Related pages

- [Cannabinoids Index](../cannabinoids.md)
- [CBG Record](cbg.md) (neutral decarboxylation product)
- [THCA Record](thca.md) (CBGAS branch product)
- [CBDA Record](cbda.md) (CBDAS branch product)
- [CBCA Record](cbca.md) (CBCAS branch product)
