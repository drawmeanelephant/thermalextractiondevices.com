---
title: "Terpenes"
id: terpenes
status: published
tags: ["terpenes", "chemistry", "reference"]
summary: Index of volatile terpene compounds, physical properties, and thermal extraction context.
---

# Terpenes Reference Index

Catalog of volatile terpene compounds detected in cannabis laboratory analysis and botanical sources.

This collection provides physical property data (with boiling points referenced to their measurement pressure, sourced from NIST Chemistry WebBook where available and flagged where not), chemical identity, sensory character, and evidence-classified biological research for thermal extraction analysis.

Boiling points are reported at the stated reference pressure. Where a value could not be confirmed against NIST, the record says so explicitly rather than implying a primary measurement. Biological activity is separated into human clinical evidence, preclinical animal evidence, in vitro evidence, traditional use, and marketing or anecdotal claims, and is never silently upgraded across evidence classes.

All satellite records in this collection follow the form identifier schema `terpenes/TTRP-XXXX`.

---

## Collection catalog

19 compounds are indexed below. **Boiling points are a physical reference property of the pure compound — not a device setting.** See [Physical Property Data Standards (TREF-0001)](reference/TREF-0001.md) and the [boiling point vs device setting note](includes/boiling-point-vs-device-note.md) before applying any value.

| Terpene | CAS number | Chemical family | Boiling point (at reference pressure) | Data confidence |
| --- | --- | --- | --- | --- |
| [α-Bisabolol](terpenes/alpha-bisabolol.md) | 515-69-5 | Monocyclic sesquiterpenoid | 153 °C at 0.667 kPa (5 mmHg) | Secondary; no NIST normal BP |
| [α-Humulene](terpenes/alpha-humulene.md) | 6753-98-6 | Monocyclic sesquiterpene | 264 °C at 101.325 kPa | Secondary; unconfirmed by NIST |
| [α-Pinene](terpenes/alpha-pinene.md) | 80-56-8 | Bicyclic monoterpene | 156 °C at 101.325 kPa | NIST-verified (mean of 14) |
| [α-Terpineol](terpenes/alpha-terpineol.md) | 98-55-5 | Monocyclic monoterpene alcohol | ≈218 °C at 101.325 kPa | NIST-verified (3 determinations) |
| [β-Caryophyllene](terpenes/beta-caryophyllene.md) | 87-44-5 | Bicyclic sesquiterpene | 263 °C at 101.325 kPa | Secondary; unconfirmed by NIST |
| [β-Myrcene](terpenes/beta-myrcene.md) | 123-35-3 | Acyclic monoterpene | 167 °C at 101.325 kPa | NIST-verified |
| [β-Pinene](terpenes/beta-pinene.md) | 127-91-3 | Bicyclic monoterpene | 166 °C at 101.325 kPa | Antoine estimate |
| [Camphene](terpenes/camphene.md) | 79-92-5 | Bicyclic monoterpene | 156–160 °C at 101.325 kPa | ICSC/ChemicalBook; NIST too dispersed |
| [D-Limonene](terpenes/d-limonene.md) | 5989-27-5 | Cyclic monoterpene | 176 °C at 101.325 kPa | NIST-verified (mean of 18) |
| [Eucalyptol](terpenes/eucalyptol.md) | 470-82-6 | Bicyclic monoterpenoid ether | 176 °C at 101.325 kPa | NIST-verified (mean of 6) |
| [Fenchol](terpenes/fenchol.md) | 1632-73-1 | Bicyclic monoterpene alcohol | ≈201–202 °C at 101.325 kPa | Secondary (PubChem/GoodScents) |
| [Geraniol](terpenes/geraniol.md) | 106-24-1 | Acyclic monoterpene alcohol | ≈229–230 °C at 101.325 kPa | Secondary (NTP/PubChem) |
| [Guaiol](terpenes/guaiol.md) | 489-86-1 | Sesquiterpene alcohol | 132–136 °C at 1.33 kPa (10 Torr) | Secondary; no NIST normal BP |
| [Linalool](terpenes/linalool.md) | 78-70-6 | Acyclic monoterpenoid | 198 °C at 101.325 kPa | NIST-verified |
| [Nerolidol](terpenes/nerolidol.md) | 7212-44-4 | Acyclic sesquiterpenoid | 276 °C at 101.325 kPa | NIST (isomer record) |
| [Ocimene](terpenes/ocimene.md) | 13877-91-3 | Acyclic monoterpene | 176 °C at 101.325 kPa | Predicted |
| [Sabinene](terpenes/sabinene.md) | 3387-41-5 | Bicyclic monoterpene | ≈164 °C at 101.325 kPa | NIST-verified (2 determinations) |
| [Terpinolene](terpenes/terpinolene.md) | 586-62-9 | Monocyclic monoterpene | 185 °C at 101.325 kPa | NIST-verified (mean of 7) |
| [Valencene](terpenes/valencene.md) | 4630-07-3 | Bicyclic sesquiterpene | 123 °C at 1.47 kPa (11 mmHg); ≈274 °C at 101.325 kPa | Secondary; no NIST normal BP |

### Reading the table

- **Pressure matters.** Values are only comparable at the same reference pressure. Reduced-pressure values (e.g., α-bisabolol at 5 mmHg, guaiol at 10 Torr, valencene at 11 mmHg) cannot be compared directly with atmospheric-pressure values.
- **Confidence tiers** follow the [source hierarchy in TREF-0001](reference/TREF-0001.md): "NIST-verified" values are primary measurements from the NIST Chemistry WebBook; "Secondary" values come from authoritative compilations that could not be confirmed against NIST and are labeled as such on the record; "Predicted" values are estimates and are never presented as measured.
- **Higher boiling point ≠ better extraction target.** Vaporization from real plant material depends on partial vapor pressure, moisture, airflow, and thermal conductance. A device set to a compound's boiling point will not selectively extract only that compound.

### Composition of the collection

- **13 monoterpenes/monoterpenoids** (α-pinene, β-pinene, β-myrcene, camphene, d-limonene, eucalyptol, fenchol, geraniol, linalool, ocimene, sabinene, α-terpineol, terpinolene) — the more volatile fraction, released early from botanical headspace.
- **6 sesquiterpenes/sesquiterpenoids** (α-bisabolol, α-humulene, β-caryophyllene, guaiol, nerolidol, valencene) — lower volatility, higher standard boiling temperatures.
- Every record keeps isomers and enantiomers as distinct identities (e.g., α-/β-pinene, D-/L-limonene, cis-/trans-nerolidol) and never collapses them.

---

## Measured occurrence in cannabis flower

The table below summarizes the strongest peer-reviewed **measured** concentrations located for each compound in the research dossiers, footnoted to the primary source of each figure. These describe what has been measured in laboratory analyses — they are not cultivar marketing claims, and no cultivar name is chemically fixed. Batch-level quantitations recorded from Certificates of Analysis live in [Lab Results](lab-results.md).

| Terpene | Typical measured concentration in cannabis | Basis (material & method) | Source |
| --- | --- | --- | --- |
| [α-Bisabolol](terpenes/alpha-bisabolol.md) | 0.66–0.68 mg/g dry weight — consistently minor (<1 mg/g) where detected | Dried flower, hydrodistilled essential oil, validated GC-MS (2 US hemp cultivars) | [^1] |
| [α-Humulene](terpenes/alpha-humulene.md) | ≈0.1–2 mg/g dry weight | Dried flower, GC-MS (hydrodistilled oil) and chemotype surveys | [^1][^3] |
| [α-Pinene](terpenes/alpha-pinene.md) | Most abundant monoterpene in Finola hemp; dominant across chemotypes (range not reported) | Dried flower, HS-SPME-GC-MS | [^2][^3] |
| [α-Terpineol](terpenes/alpha-terpineol.md) | 0.034–0.08 mg/g dry weight; 0.1–0.9 mg/g in dispensary flower — minor | Dried flower, GC-FID (Univ. of Mississippi chemovars; California dispensary cultivars) | [^5][^4] |
| [β-Caryophyllene](terpenes/beta-caryophyllene.md) | 3.89–4.69 mg/g dry weight — among the most abundant sesquiterpenes | Dried flower, hydrodistilled oil, validated GC-MS (2 US hemp cultivars) | [^1][^3] |
| [β-Myrcene](terpenes/beta-myrcene.md) | 5.85–8.62 mg/g dry weight — frequently the dominant monoterpene | Dried flower, hydrodistilled oil, validated GC-MS (2 US hemp cultivars) | [^1] |
| [β-Pinene](terpenes/beta-pinene.md) | 0.14–0.53 mg/g dry weight — minor relative to β-myrcene and limonene in the same samples | Dried flower, hydrodistilled oil, validated GC-MS (2 US hemp cultivars) | [^1] |
| [Camphene](terpenes/camphene.md) | 0.002–0.09 mg/g dry weight (THC-dominant); up to ≈0.48 mg/g (CBD-dominant) | Dried flower, chemotype surveys | [^4][^3] |
| [D-Limonene](terpenes/d-limonene.md) | 0.53–2.64 mg/g dry weight (525–2,644 µg/g) — among the most abundant monoterpenes | Dried flower, GC-MS (5 Canadian cultivars) | [^3] |
| [Eucalyptol](terpenes/eucalyptol.md) | Detected in 3 of 19 cultivars; 0.01–0.39% of identified peak area where present | Dried flower, HS-SPME-GC-MS (Thai cultivar survey) | [^9] |
| [Fenchol](terpenes/fenchol.md) | 0.028–1.09 mg/g dry weight | Dried flower, pooled literature survey (chemotypes I–III) | [^7] |
| [Geraniol](terpenes/geraniol.md) | Trace to below limit of quantitation | Dried flower, GC-MS (Finola hemp; 2 US hemp cultivars) | [^2][^1] |
| [Guaiol](terpenes/guaiol.md) | ≈10% of the terpene fraction in a high-CBD full-spectrum extract (flower data scarce) | Extract, GC-MS | [^10] |
| [Linalool](terpenes/linalool.md) | Common but rarely dominant; batch-dependent, no fixed range | Dried flower, chemotype surveys | [^3] |
| [Nerolidol](terpenes/nerolidol.md) | Usually absent or trace; <0.1% dry weight where above LOQ (Black Lime only) | Dried flower, 9-cultivar GC-MS profiling | [^6] |
| [Ocimene](terpenes/ocimene.md) | 0.19–1.38 mg/g dry weight (191–1,382 µg/g) in 4 of 6 cultivars, not detected in the rest; typically <5% of total terpenes | Dried flower, 6 cultivars (GC-MS) | [^3][^1] |
| [Sabinene](terpenes/sabinene.md) | ≤0.005 mg/g dry weight (chemotype I), lower in chemotype III — trace | Dried flower, pooled literature survey | [^7] |
| [Terpinolene](terpenes/terpinolene.md) | 0.18–30.5 mg/g dry weight (up to ≈3% of dry weight in one of nine cultivars) — highly variable | Dried flower, hydrodistilled essential oil, GC-MS (9 Italian hemp cultivars) | [^8] |
| [Valencene](terpenes/valencene.md) | Trace (≤0.4 g/100 g of essential oil); no quantitative data located for drug-type flower | Hydrodistilled essential oil (Italian hemp cultivars) | [^8] |

### Reading the occurrence table

- **Units and bases are not interchangeable.** Dry-weight values (mg/g) describe the flower itself; essential-oil percentages (g/100 g oil) describe the distilled oil; peak-area percentages describe relative detector response. Only values on the same basis can be compared directly.
- **Concentrations are batch-, cultivar-, and method-dependent.** Ranges reflect the cultivars and methods of the cited study, not a physical constant of the compound. Cultivar names are not chemically fixed across markets.
- **Absence is information.** Compounds reported as trace, below LOQ, or not detected (e.g., geraniol, nerolidol, eucalyptol in most cultivars) are honest negatives — no marketing figure was substituted where peer-reviewed data are scarce.
- Every range is footnoted to its primary source; the same figures appear with full context in each record's [Cannabis laboratory results](lab-results.md) section.

---

## Related collections

- **[Botanicals](botanicals.md)** — non-cannabis plant species (hops, citrus, lavender) that share these terpene profiles.
- **[Cannabinoids](cannabinoids.md)** — the phytocannabinoid companion collection, with its own thermal-degradation context.
- **[Lab Results](lab-results.md)** — batch Certificates of Analysis recording measured terpene concentrations.
- **[Physical Property Data Standards (TREF-0001)](reference/TREF-0001.md)** — how boiling points and source confidence are reported.
- **[Evidence Labels and Claim Grammar (TREF-0003)](reference/evidence-labels-and-claim-grammar.md)** — how biological activity claims are classified.

[^1]: Joy N, et al. A Validated GC-MS Method for Major Terpenes Quantification in *Cannabis sativa* L. Essential Oil. 2025. PMC12670203; PMID 40042239.
[^2]: Booth JK, Page JE, Bohlmann J. Terpene synthases from *Cannabis sativa*. *PLoS One.* 2017;12(3):e0173911. PMID 28355238.
[^3]: Booth JK, et al. Terpene synthases and terpene variation in *Cannabis sativa*. *Plant Physiol.* 2020;184(1):130–147. doi:10.1104/pp.20.00593. PMID 32591428.
[^4]: Fischedick JT. Identification of Terpenoid Chemotypes Among High (−)-trans-Δ9-Tetrahydrocannabinol-Producing *Cannabis sativa* L. Cultivars. *Cannabis Cannabinoid Res.* 2017;2(1):34–47. PMID 28861503.
[^5]: Ibrahim EA, et al. Quantitative Determination of Cannabis Terpenes Using Gas Chromatography-Flame Ionization Detector. *Cannabis Cannabinoid Res.* 2023;8(5):899–910. doi:10.1089/can.2022.0188. PMID 36322895.
[^6]: Zager JJ, Lange I, Srividya N, et al. Gene Networks Underlying Cannabinoid and Terpenoid Accumulation in Cannabis. *Plant Physiol.* 2019;180(4):1877–1897.
[^7]: Chacon FT, Raup-Konsavage WM, Vrana KE, Kellogg JJ. Secondary Terpenes in *Cannabis sativa* L.: Synthesis and Synergy. *Biomedicines.* 2022;10(12):3142. doi:10.3390/biomedicines10123142. PMID 36551898.
[^8]: Mazzara E, et al. A Comprehensive Phytochemical Analysis of Terpenes, Polyphenols and Cannabinoids, and Micromorphological Characterization of 9 Commercial Varieties of *Cannabis sativa* L. *Plants.* 2022;11(7):891. doi:10.3390/plants11070891.
[^9]: Janta S, et al. Chemical profiling and clustering of various dried cannabis flowers. *J Cannabis Res.* 2024. doi:10.1186/s42238-024-00252-w. PMID 39639406.
[^10]: Anil SM, Shalev N, Vinayaka AC, et al. Cannabis compounds exhibit anti-inflammatory activity in vitro in COVID-19-related inflammation in lung epithelial cells and pro-inflammatory activity in macrophages. *Sci Rep.* 2021;11. doi:10.1038/s41598-021-81049-2. PMID 33446817.
