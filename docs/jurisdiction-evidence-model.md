# Jurisdiction Evidence Model

Status: **adopted (schema v1)** · Date: 2026-08-09 · Drives: COA normalization,
entity resolution, relationship layer, and state knowledge pages.

This document defines the minimum reusable schema for state-level cannabis
evidence in the Thermal Extraction Devices archive. It is deliberately
jurisdiction-agnostic: California and Massachusetts keep their own terminology,
license classes, and testing rules, but both emit records shaped like this model.

The implementation lives in `scripts/ingest/evidence.py` (schema constants,
dataclasses, validation, persistence). The model is expressed as normalized
machine records (CSV/JSON under `data/`) — **never** as prose-first content.
Human-readable pages are the end of the pipeline, not the source of truth.

---

## 1. Guiding rules (from the mission, made operational)

1. **Never delete a `*_raw` value after normalization.** Every normalized record
   retains the original source string alongside the normalized value.
2. **Analytical states are distinct.** `ND`, `<LOD`, `<LOQ`, a numeric value,
   and an absent measurement are different states and must never be collapsed
   (in particular: ND → 0, `<LOQ` → 0, `<LOD` → 0 are forbidden).
3. **Units are preserved.** Unit normalization may add a canonical unit, but the
   source unit string is always retained; silent unit conversion is forbidden
   without recording the conversion.
4. **Identity requires evidence.** A commercial cultivar name on a COA is
   `cultivar_raw`; it becomes a link to a canonical cultivar entity only when
   the identity policy (Step 9) permits it — otherwise it stays a
   `cultivar_normalized_candidate` with a confidence below the link threshold.
5. **Ambiguity is recorded, not fixed.** Unresolvable entity names produce
   candidate/unresolved markers, never fabricated certainties.
6. **COA values are batch-specific evidence.** They describe one batch/lot and
   never implicitly generalize to a brand, producer, or cultivar.
7. **Provenance is mandatory.** Every record carries source URL, source hash,
   retrieval timestamp, parser + version, and confidence fields.
8. **Separable concepts stay separable.** Legal entity, DBA, brand, license,
   facility, product, batch, lab, parent company are distinct fields/entities;
   the model never merges them.

---

## 2. Entity inventory

| Entity | Canonical ID collection (this repo) | Notes |
| --- | --- | --- |
| Jurisdiction | `jurisdictions/TJUR-*` | State/province profile |
| Regulator | (attribute of jurisdiction; no separate collection yet) | e.g. DCC, MA CCC |
| Statute / regulation / guidance document | `requirements/TREQ-*` + source artifact | Citations preserved verbatim |
| Regulatory requirement | `requirements/TREQ-*` | Panels, limits, sampling rules |
| License | `licenses/TLIC-*` | One row per license, never collapsed |
| License type | (attribute; state-specific vocabulary preserved) | e.g. "Cultivation - Small Outdoor", "Independent Testing Laboratory" |
| Legal entity | `organizations/TORG-*` | Source legal name; display names never merged |
| DBA | (attribute of license/organization) | Preserved as `*_dba` raw text |
| Brand | (attribute; `brand_raw`/`brand_normalized_candidate`) | Brand ≠ license holder |
| Facility / premises | (attribute of license) | Street excluded from public pages; municipality/county kept |
| Parent company / MSO | (attribute; resolution layer only) | Never inferred from similar names |
| Testing laboratory | `testing-laboratories/TSTL-*` | Registry entity (Step 6) |
| Laboratory accreditation | (attribute of lab registry) | ISO/IEC 17025, A2LA/PJLA certificate numbers |
| Product | `products/TPRD-*` | Commercial product label |
| Batch / lot | (COA header field; later `TLAB`-adjacent) | Batch ID as printed |
| Package identifier | (COA field; affected-products `TAFP-*` in MA) | UID / package ID |
| COA / laboratory report | `lab-results/TLAB-*` | One normalized record per report |
| Test panel | (attribute of COA) | The panel as declared by the lab/state |
| Analyte result | (row within a COA record; `data/coa/analyte-results.csv`) | One row per analyte per COA |
| Cannabinoid / terpene / contaminant | `terpenes/TTRP-*`, `contaminants/TCNT-*` (cannabinoids: see §6) | Linked only on unambiguous identity |
| Recall / enforcement action | `recalls/TRCL-*` (CA), `safety-advisories/TSAD-*` (MA) | State terminology preserved |
| Cultivar / commercial cultivar name | `cultivars/TCUL-*` + `cultivar_raw` fields | Raw never replaced by canonical silently |
| Breeder / genetic provenance claim | (attribute; evidence policy gated) | Only from suitable provenance sources |
| Source artifact | `data/coa-artifacts/<sha256>.*` | Immutable, hashed, dated |
| Dataset snapshot | `datasets/TDTS-*` | Dated, checksummed |

---

## 3. Normalized COA record (one per report)

Field list (implemented in `scripts/ingest/evidence.py` as `COA_FIELDS`):

```text
jurisdiction                # e.g. "massachusetts" | "california"
source_document             # filename or report id of the source artifact
source_url                  # canonical URL where the report was obtained
source_hash                 # SHA-256 of the raw artifact bytes
source_retrieved_at         # ISO-8601 retrieval timestamp
lab_raw                     # laboratory name as printed
lab_normalized_id           # testing-laboratories/TSTL-* when resolvable
lab_license                 # lab license number when printed
producer_raw                # producer as printed
producer_normalized_id      # organizations/TORG-* when resolvable
brand_raw                   # brand as printed
brand_normalized_id         # (reserved; brand collection not yet created)
product_raw                 # product label as printed
product_normalized_id       # products/TPRD-* when a product record exists
product_type_raw            # e.g. "Dried Flower", "Vape Cartridge"
product_type_normalized     # controlled term when unambiguous (else raw)
cultivar_raw                # cultivar/strain as printed on the COA
cultivar_normalized_candidate  # normalized candidate string (never a link)
batch_or_lot                # batch/lot id as printed
package_id                  # package/UID as printed
sample_id                   # sample id as printed
sample_date                 # ISO date when printed
received_date               # ISO date when printed
test_date                   # ISO date when printed
report_date                 # ISO date when printed
panel                       # declared test panel (state terminology preserved)
analyte_raw                 # analyte as printed
analyte_normalized_id       # TTRP-*/TCNT-*/cannabinoid id when unambiguous
result_raw                  # result as printed, e.g. "<0.10", "ND", "1.23"
result_numeric              # float when the value is numeric
result_state                # numeric | below_lod | below_loq | nd | blank | qualitative | unknown
unit_raw                    # unit as printed
unit_normalized             # canonical unit when unambiguous (else raw)
LOD                         # limit of detection as printed (raw text)
LOQ                         # limit of quantitation as printed (raw text)
regulatory_limit            # applicable action limit with citation (from Step 4 data)
pass_fail                   # pass | fail | not_applicable | unknown (as printed)
test_method                 # method as printed (e.g. "LC-MS/MS", "AOAC 2015.01")
parser_method               # parser id + version, e.g. "coa/csv/v1"
parser_confidence           # 0..1
normalization_confidence    # 0..1
notes                       # free text; ambiguity recorded here
```

Every field is optional except: `jurisdiction`, `source_document`, `source_hash`,
`source_retrieved_at`, `analyte_raw`, `result_raw`, `parser_method`. The
`*_raw` fields must never be blanked after normalization.

### 3.1 `result_state` semantics

| value | meaning | example |
| --- | --- | --- |
| `numeric` | quantitative value reported | `1.23` |
| `below_lod` | reported below the limit of detection | `<0.05` (LOD 0.05) |
| `below_loq` | reported below the limit of quantitation | `<0.10` (LOQ 0.10) |
| `nd` | reported "none detected" / ND | `ND` |
| `blank` | field present but empty | `—` |
| `qualitative` | non-quantitative result (e.g. "Pass", "Absent") | `Not Detected` with no numeric |
| `unknown` | could not be classified | free-text result |

`result_numeric` is populated **only** for `numeric`. Absence of a result must
not be treated as zero; presence of a result does not imply the analyte was
required by the jurisdiction.

---

## 4. Entity resolution and confidence

The relationship layer (Step 9) and entity resolution (Step 5) share one rule:
**a proposed relationship is not a fact.** Every proposal carries:

```text
source                     # which evidence record(s) support it
relationship               # e.g. "license->legal_entity"
from_id / to_id            # entity IDs (or candidate strings)
confidence                 # 0..1
status                     # confirmed | candidate | unresolved | rejected
evidence_url / evidence_hash
notes
```

Confidence bands used by the tooling:

* `1.0` — directly stated by a primary source (e.g. license row names the legal
  entity).
* `0.7–0.9` — same-string identity after deterministic normalization (case,
  punctuation, corporate-suffix abbreviation) with no counter-evidence.
* `0.3–0.6` — plausible but ambiguous (e.g. DBA matches a brand name; same
  cultivar string on two COAs).
* `<0.3` — recorded for the exception report but never proposed as a link.

Never infer ownership from similar names. Parent-company/MSO mappings are
always `candidate` until a primary corporate source (registry, annual report,
accreditation) states them.

---

## 5. Cultivar identity policy (Step 9)

* `cultivar_raw` on a COA is always preserved.
* A canonical `cultivars/TCUL-*` link is created only when evidence policy
  permits: e.g. a producer/licensee explicitly documents genetics, or a
  recognized cultivar record with published provenance exists. "Blue Dream" on
  a Massachusetts COA does **not** prove descent from any particular breeder's
  Blue Dream.
* Otherwise the record stores `cultivar_normalized_candidate` and the
  relationship layer emits `commercial_cultivar_name → possible_cultivar`
  with `status: candidate` and the confidence rules above.

---

## 6. Analyte graph mapping

Normalization targets the existing graph where identity is unambiguous:

* **Terpenes** → `terpenes/TTRP-*` (existing editorial records: α-pinene,
  β-myrcene, d-limonene, eucalyptol, linalool, nerolidol, terpinolene,
  α-bisabolol, α-humulene, β-caryophyllene, β-pinene, ocimene).
* **Contaminants** → `contaminants/TCNT-*` (CA-generated: pyrethrins,
  aflatoxins, ochratoxin A, STEC, salmonella, aspergillus, lead, residual
  solvents) and any MA analytes mapped by the MA adapter.
* **Cannabinoids** → a controlled vocabulary with stable slugs (THC, THCA,
  CBD, CBDA, CBG, CBGA, CBN, CBC, Delta-8-THC, Total THC, Total CBD…); a
  `cannabinoids` collection is created only when records exist that need pages.

Unknown analytes are never discarded: they remain `analyte_raw` with an empty
`analyte_normalized_id`, appear in the "unknown analytes" report, and are
surfaced for analyst review.

## 7. Artifact and snapshot model

* Raw artifacts: `data/coa-artifacts/<sha256><ext>` (immutable, hashed; never
  overwritten; `source_hash` ties records to bytes).
* Dataset snapshots: existing `ArtifactStore` (MA) and dated-dir (CA) layouts
  both conform — a snapshot is a dated/checksummed capture of a source payload.
* Parsed output never overwrites the raw artifact; normalized evidence records
  are written alongside, referencing the hash.

## 8. Implementation surface

* `scripts/ingest/evidence.py` — field constants, `AnalyteResult` /
  `COARecord` dataclasses, `result_state` classifier, validation
  (`validate_coa_record`), CSV/JSON persistence (`write_coa_csv`,
  `read_coa_csv`), analyte normalization helpers.
* `data/coa/<jurisdiction>/` — normalized analyzer output per state.
* `data/coa-artifacts/` — hashed raw COA documents.
* Tests in `tests/test_evidence.py`.
