---
id: cannabinoids/TCBN-0007
title: "Δ9-Tetrahydrocannabinolic Acid (THCA)"
parent: cannabinoids
status: published
tags: ["cannabinoid", "phytocannabinoid", "acid"]
relations: [relates_to=cannabinoids/TCBN-0006, relates_to=cannabinoids/TCBN-0008, relates_to=cannabinoids/TCBN-0002, relates_to=cannabinoids/TCBN-0003]
summary: Acidic phytocannabinoid precursor of Δ9-THC, dominant in fresh drug-type flower; no measured atmospheric boiling point because decarboxylation precedes boiling.
---

# Δ9-Tetrahydrocannabinolic Acid (THCA)

## Identity

| Property | Value |
| --- | --- |
| Preferred name | Δ9-Tetrahydrocannabinolic acid A (THCA-A) |
| IUPAC name | (6aR,10aR)-1-hydroxy-6,6,9-trimethyl-3-pentyl-6a,7,8,10a-tetrahydro-6H-benzo[c]chromene-2-carboxylic acid |
| CAS number | 23978-85-0 (THCA-A) |
| PubChem CID | 98523 |
| InChIKey | FCHTHPIEJYEJOM-DUYOSMWVSA-N [^1] |
| Molecular formula | C22H30O4 |
| Molecular mass | 358.48 g/mol (exact 358.2144 Da) |
| Compound class | Cannabinoid acid; meroterpenoid (prenylated benzochromene) |
| Stereochemistry | Two stereocenters; natural material is (6aR,10aR). THCA-B (3-COOH regioisomer) is a distinct minor entity; Δ8-THCA (CAS 5957-75-5) is a distinct positional isomer [^1] |
| Major synonyms | THCA, Δ9-THCA-A, tetrahydrocannabinolic acid; decarboxylation product is Δ9-THC |

### Identity notes

- Many COAs report "THCA" without specifying the isomer; THCA-A is the natural biosynthetic product, THCA-B is a minor isomer with a different retention time and melting point [^1].
- Δ9-THCA vs. Δ8-THCA have distinct CAS numbers (23978-85-0 vs. 5957-75-5) and must not be collapsed [^1].
- GC without derivatization converts THCA to THC in the injector and reports "Total THC"; the theoretical weight-conversion factor is 0.877, with empirical flower-matrix values lower [^2].

## Physical properties

| Property | Value | Conditions / Notes |
| --- | --- | --- |
| Melting point | ≈70 °C (with decomposition) for THCA-A; 184–185 °C for THCA-B | THCA-A decarboxylates at melt [^1] |
| Boiling point | **No experimentally measured boiling point at 1 atm.** The "≈437 °C" figure is a QSPR prediction, not a measurement; thermal degradation precedes boiling [^2] |
| Vapor pressure | No authoritative experimental data; predicted values only | Antoine parameters not published [^2] |
| logP (octanol-water) | ≈5.4–5.8 (predicted) | Highly lipophilic |
| Water solubility | <1 mg/L (very low) | Soluble in ethanol, methanol, chloroform, DMSO, oils |
| Thermal decomposition | Decarboxylation onset ≈105 °C; complete ≈160 °C (solid state, ≈20 min); onset shifts higher in plant matrix | First-order kinetics; Ea ≈85–88 kJ/mol [^2] |
| Oxidation sensitivity | Moderate; forms CBN-type oxidation products under heat/air | Slower than THC oxidation; THCA decarboxylates first [^2] |
| Light sensitivity | Photodegradation reported; UV accelerates decarboxylation and oxidation | Amber storage for standards [^2] |
| Known degradation products | Δ9-THC (decarboxylation), CBN (oxidation of THC), Δ8-THC (isomerization), quinones (pyrolysis) | [^2] |

> **Boiling point is not a device setpoint.** No experimentally validated boiling point or vapor-pressure curve exists for THCA. The "437 °C" value is a QSPR prediction; thermal behavior in plant matrix is governed by decarboxylation kinetics, not phase change.

## Thermal-extraction context

{{include includes/boiling-point-vs-device-note.md}}

Thermal release of the THC series from botanical matrix requires decarboxylation of THCA to THC (onset ≈105 °C, accelerated at higher temperature), followed by vapor-pressure-driven evaporation of the neutral THC. Device chamber temperature is not sample temperature; material lags the setpoint.

## Cannabis occurrence

- Measured fresh/frozen "THCA flower" and drug-type flower batches have reported 15–30% w/w (dry-weight basis) THCA [^3].
- Values are batch- and report-attached; no universal cultivar claim is made. Consult [Lab Results](../lab-results.md) for batch-level measurements.

## Biosynthesis and processing

THCA is biosynthesized from CBGA by THCAS (THCA synthase) and competes with CBDAS and CBCAS for the shared CBGA pool; the THCAS/CBDAS allele balance defines chemotype I/II/III. Drying, curing, and heating convert THCA to THC, and prolonged oxidation yields CBN [^2].

## Reported biological activity

### Human evidence
THCA itself is the non-psychoactive precursor; intoxicating effects in humans are attributed to its decarboxylation product Δ9-THC. No verified controlled human study of inhaled isolated THCA was identified for this archive [^4].

### Preclinical animal and in vitro evidence

{{include includes/preclinical-evidence-note.md}}

Preclinical studies report anti-inflammatory and neuroprotective-like activity of THCA in vitro at micromolar concentrations; these do not establish human effects at consumer-relevant doses [^4].

### Industry claims
"THCA flower is federally legal because it is non-psychoactive until heated" is a legal/market framing, not a chemistry claim about consumer effects; health claims for THCA lack controlled human evidence [^4].

## Degradation products

- Primary: Δ9-THC (decarboxylation)
- Secondary: CBN (oxidation of THC), Δ8-THC (isomerization), quinones (pyrolysis)

## Sources

[^1]: PubChem CID 98523, Δ9-Tetrahydrocannabinolic acid (CAS 23978-85-0). Verified 2026-08-08.
[^2]: Research-corpus dossier research/compounds/cannabinoids/thca/artifact.md (QSPR boiling-point prediction; decarboxylation kinetics; GC artifact). Not all ledger items re-verified in this wave.
[^3]: Occurrence ranges as reported in the THCA dossier from measured COA and published datasets; representative values, not universal cultivar statements.
[^4]: Research-corpus dossier research/compounds/cannabinoids/thca/artifact.md evidence table; no human trials identified.

## Related pages

- [Cannabinoids Index](../cannabinoids.md)
- [CBGA Record](cbga.md) (biosynthetic precursor)
- [THCV Record](thcv.md) (propyl homologue)
- [CBD Record](cbd.md) (competitive biosynthetic branch)
