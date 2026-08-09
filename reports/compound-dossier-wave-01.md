# Compound Dossier Wave 1 — Editorial Report

Status: **PASS** for ID/graph/link gates; pre-existing PII audit baseline noted below.

## Scope

Converted research dossiers under `research/compounds/` into canonical chemistry pages for the 7 terpenes not previously represented in the site and 8 cannabinoids (a new collection). Selection rule: compounds with the strongest artifact/source coverage that were **not** already comprehensively represented in `content/`.

## Files added

| File | Type |
| --- | --- |
| `content/cannabinoids.md` | New collection trunk (`cannabinoids/TCBN-XXXX`) |
| `content/cannabinoids/cbca.md` | Cannabichromenic Acid (CBCA), `cannabinoids/TCBN-0001` |
| `content/cannabinoids/cbd.md` | Cannabidiol (CBD), `cannabinoids/TCBN-0002` |
| `content/cannabinoids/cbda.md` | Cannabidiolic Acid (CBDA), `cannabinoids/TCBN-0003` |
| `content/cannabinoids/cbdv.md` | Cannabidivarin (CBDV), `cannabinoids/TCBN-0004` |
| `content/cannabinoids/cbg.md` | Cannabigerol (CBG), `cannabinoids/TCBN-0005` |
| `content/cannabinoids/cbga.md` | Cannabigerolic Acid (CBGA), `cannabinoids/TCBN-0006` |
| `content/cannabinoids/thca.md` | Δ9-Tetrahydrocannabinolic Acid (THCA), `cannabinoids/TCBN-0007` |
| `content/cannabinoids/thcv.md` | Δ9-Tetrahydrocannabivarin (THCV), `cannabinoids/TCBN-0008` |
| `content/terpenes/alpha-terpineol.md` | `terpenes/TTRP-0013` |
| `content/terpenes/camphene.md` | `terpenes/TTRP-0014` |
| `content/terpenes/fenchol.md` | `terpenes/TTRP-0015` |
| `content/terpenes/geraniol.md` | `terpenes/TTRP-0016` |
| `content/terpenes/guaiol.md` | `terpenes/TTRP-0017` |
| `content/terpenes/sabinene.md` | `terpenes/TTRP-0018` |
| `content/terpenes/valencene.md` | `terpenes/TTRP-0019` |
| `reports/compound-dossier-wave-01.md` | This report |

## Files modified

| File | Change |
| --- | --- |
| `content/index.md` | Added Cannabinoids to Technical Collections |
| `scripts/ted_ids.py` | Added `cannabinoids` → `TCBN` to `DEFAULT_PREFIX` and `FORM_PREFIXES`; made pending-ID allocation preserve existing satellite IDs (id-policy immutability) instead of renumbering siblings alphabetically |
| `metadata/id-map.jsonl` | Regenerated: 151 pages (was 135), new collections allocated |

## Entities created

- 1 collection trunk: `cannabinoids`
- 8 cannabinoid satellites (`TCBN-0001`…`TCBN-0008`)
- 7 terpene satellites (`TTRP-0013`…`TTRP-0019`)
- 15 canonical compound records total (existing IDs `TTRP-0001`…`TTRP-0012` untouched)

## Graph relationships created

All relations use the site's supported `relates_to` verb; richer semantic vocabulary (isomer_of, biosynthesized_from, degrades_to, co_occurs_with, investigated_for) is documented in each page's narrative sections and in the cultivar-chemotype design document:

- CBD `relates_to` CBDA, CBGA, THCA, β-Myrcene, β-Caryophyllene
- CBDA `relates_to` CBD, CBGA, THCA
- CBGA `relates_to` CBG, CBCA, CBD, CBDA, THCA (precursor hub)
- CBG `relates_to` CBGA, CBD
- THCA `relates_to` CBGA, THCV, CBD, CBDA
- THCV `relates_to` THCA
- CBDV `relates_to` CBD
- CBCA `relates_to` CBGA, CBD

## Primary sources verified (web-checked against authoritative databases)

- **Terpenes**: α-Terpineol (CAS 98-55-5, CID 17100, NIST Tboil 490.7/491.15/491.0 K); Camphene (CAS 79-92-5, CID 6616, ICSC 1704 156–160 °C; NIST mean flagged unusable); Fenchol (CAS 1632-73-1, CID 15406, 201–202 °C @ 760 mmHg); Geraniol (CAS 106-24-1, CID 637566, 229–230 °C @ 760 mmHg); Guaiol (CAS 489-86-1, CID 227829, 132–136 °C @ 10 Torr per CAS Common Chemistry; atmospheric value unconfirmed); Sabinene (CAS 3387-41-5, CID 18818, NIST Tboil 436.7/437 K); Valencene (CAS 4630-07-3, CID 9855795, 123 °C @ 11 mmHg; 274 °C @ 760 mmHg lit.)
- **Cannabinoids**: CBD (13956-29-1, CID 644019); CBDA (1244-58-2, CID 160570); CBCA (20408-52-0, CID 3084339); CBDV (24274-48-4, CID 11601669); CBG (25654-31-3, CID 5315659); CBGA (25555-57-1, CID 6449999); THCA (23978-85-0, CID 98523); THCV (31262-37-0, CID 93147). All formulas and masses cross-checked against PubChem/CAS Common Chemistry.

## Boiling-point policy enforced

Every boiling-point statement preserves its measurement pressure. For every major cannabinoid, the page states explicitly that the compound thermally degrades (decarboxylates or oxidizes) before boiling intact at 1 atm, and that "boiling point" figures circulating in vaporizer marketing are not thermodynamic boiling points and are never treated as device setpoints (see the boiling-point-vs-device-note include on every page).

## Uncertain claims left unresolved

- CBD InChIKey stereoisomer suffix differs between NIST and PubChem records — flagged, not asserted.
- CBDV InChIKey from the research dossier was garbled — omitted, flagged.
- Guaiol atmospheric boiling point (288–310 °C range) not confirmed by NIST — reported as unconfirmed.
- Camphene NIST mean boiling temperature (380 ± 100 K) too dispersed to cite — ICSC/literature range used instead.
- THCA "≈437 °C" boiling point is a QSPR prediction, not a measurement — stated as such.
- Activity claims per compound are labeled with evidence class; in vitro/animal concentrations are noted as supraphysiological relative to human cannabis exposure; no human-inhalation evidence exists for any of the 15 compounds.

## Unsupported popular claims intentionally excluded

- "CBD/THCA/CBG/CBGA/CBDV/THCV boil at 160–220 °C" (vaporizer-chart boiling points) — excluded as thermodynamic claims; retained only as matrix-evaporation context with explicit correction.
- "CBG boils at 52 °C" — retained only as the reduced-pressure (high-vacuum) distillation figure it actually is.
- "CBD converts to THC in the stomach" — not demonstrated in humans; excluded.
- "Full-spectrum/entourage is more effective" — no controlled human comparison at matched dose; excluded.
- "CBG/CBDA/THCV health claims" (appetite suppression, anti-inflammatory cures, etc.) — no controlled human evidence; excluded or labeled as industry claims.
- Cultivar-specific chemistry ("Blue Dream contains X") — never written as universal statements; occurrence ranges are attached to measured batches/reports.

## Validation results

```
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl --write
  → normalized 151 pages; wrote metadata/id-map.jsonl
python3 scripts/ted_ids.py --root content --map metadata/id-map.jsonl
  → validated 151 pages; no files changed
bin/boris check --input content --format json
  → only baseline unreferenced_page findings (124); no unexpected findings
python3 scripts/audit_markdown_links.py content
  → all local Markdown links resolve
./bin/validate_graph.sh
  → ID + graph + build gates pass; blocked only by the pre-existing
    public-release PII audit on committed data/dcc/license-registry/*.json
    (untouched by this wave; baseline condition)
```

## Research corpus records consumed

- `research/compounds/terpenes/{alpha-bisabolol,alpha-pinene,d-limonene,eucalyptol,geraniol,linalool,nerolidol,ocimene,terpinolene,valencene}/artifact.md` (reference templates)
- `research/compounds/terpenes/{alpha-terpineol,camphene,fenchol,guaiol,sabinene}/source/2026-08-08-perplexity.md`
- `research/compounds/cannabinoids/{cbca,cbd,cbdv,cbg,cbga,thca,thcv}/artifact.md`
- `research/compounds/cannabinoids/cbda/source/2026-08-08-perplexity.md`
- `research/_index/manifest.jsonl` (index verification)

## Provenance remediation (2026-08-08, post-review)

All research-corpus artifact citations (`research/compounds/.../artifact.md`) that had served as the *published evidentiary endpoint* for material claims were replaced with directly verified primary sources, per the repository rule `research → source ledger → primary source → site claim`:

- **Thermal/degradation chemistry**: Wang et al. 2016 (Cannabis Cannabinoid Res, PMID 28861498) for decarboxylation kinetics; Dussy et al. 2005 (Forensic Sci Int, PMID 15734104) for THCA-A GC conversion; García-Valverde et al. 2022 (Front Chem) and Tsujikawa et al. 2022 (Forensic Sci Int, PMID 35728413) for thermal degradation / GC cyclization; Urvashi & Han et al. 2024 (J Cannabis Res) for pressurized-liquid decarb kinetics.
- **Vapor pressure / boiling-point corrections**: Lovestead & Bruno 2017 (Forensic Chem, PMID 29266138) for the measured CBD/Δ9-THC vapor pressures; the "El-Hage et al. 2023 (PMC10249740)" reference used by several pages was **corrected** to its actual authors, **Eyal et al. 2023** (Cannabis Cannabinoid Res, PMID 35442765).
- **Biological claims**: Nadal et al. 2017 (Br J Pharmacol), Ruhaak et al. 2011 (Biol Pharm Bull), Thomas et al. 2005 (Br J Pharmacol, THCV), Hill et al. 2012 (Br J Pharmacol, CBDV), Devinsky 2017 / Thiele 2018 / Thiele 2021 (Epidiolex RCTs), Bergamaschi 2011 (anxiety RCT), Ibeas Bih 2015 and Millar 2018 (reviews, class stated).
- **Occurrence ranges**: Jikomes & Zoorob 2018 (Sci Rep) for legal-market flower; Stack et al. 2023 (Plant Direct) for high-CBD hemp; ranges reworded as representative/batch-attached.
- **Geraniol**: corrected the garbled "LaVigne et al. 2021 (Cannabis Cannabinoid Res)" citation to the actual LaVigne et al. 2021 Sci Rep paper (PMID 33859287); occurrence re-sourced to Booth et al. 2017 (PLoS One).
- **Removed**: the temporally unstable "THCA flower is federally legal" industry framing (replaced with a chemistry-scoped statement); the "Not all ledger items re-verified in this wave" caveat no longer applies because ledger items now cite their primary sources directly.
- Claims that could not be verified against a primary source were softened or explicitly marked uncertain (e.g., THCA-B melting point, CBCA CBL photoproduct).

## Suggested next work

- Wave 2 compounds: THC, CBN, CBC, THCVA, CBDVA, CBGVA (source-only folders), plus CBDA/CBDVA artifact normalization.
- Attach batch COA records (`lab-results/TLAB-*`) to compound pages via measured-in relations once real COAs exist.
- Independent re-verification of each page's evidence-table claims against the primary papers in each dossier's source ledger.
