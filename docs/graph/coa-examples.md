# COA Data Model — Representative Real-Data Examples

**Status:** Documentation examples only · **Scope:** every example below is derived from **real** Massachusetts Cannabis Control Commission (CCC) open-data testing rows, not from synthetic or demonstration COAs.

**Provenance of every example row:** the official CCC testing dataset `CCC_Testing_Results_2025` (Open Data catalog: <https://masscannabiscontrol.com/open-data/data-catalog/>), captured verbatim in `tests/fixtures/massachusetts/CCC_Testing_Results_2025.csv` (39 rows, label "verbatim source excerpt" per `tests/fixtures/massachusetts/PROVENANCE.md`). Laboratory names in the public file are pseudonymized by the Commission (`Lab_H`, `Lab_G`, `Lab_A`), and this documentation preserves them as-is. None of these records is a published COA on the site; they demonstrate the model against real data. Metrc package identifiers are truncated to 12 hex characters here for readability; the model stores full tags.

The 11 synthetic rows appended to the *2024* testing fixture (which include a fabricated "Blue Dream" potency row) are **never** used in this document or anywhere in the model — fixture provenance is enforced, not assumed.

---

## 1. Same analyte, different laboratories: the state of real cross-lab data

All seven THC rows in the verbatim 2025 slice, exactly as printed, decoded by `decode_result`:

| Printed result | Lab | Decoded state | Normalized value | Note |
| --- | --- | --- | --- | --- |
| `1.34` | Lab_H | `numeric` | 1.34 % w/w | fully quantified |
| `0.36` | Lab_H | `numeric` | 0.36 % w/w | fully quantified |
| `3.26` | Lab_H | `numeric` | 3.26 % w/w | fully quantified |
| `2.48` | Lab_H | `numeric` | 2.48 % w/w | fully quantified |
| `0.0` | Lab_G | `zero` | 0.0 % w/w | **flagged for review** — explicit zero, never treated as `nd`/`missing` |
| `0.231` | Lab_A | `numeric` | 0.231 % w/w | fully quantified; precision preserved (3 sig figs) |
| `1.576` | Lab_H | `numeric` | 1.576 % w/w | fully quantified; precision preserved |

The spread (0.0–3.26 %) is exactly why the model refuses to pool these without grading: none of the rows carries method, LOD/LOQ, basis, or moisture metadata, so the pairwise grade between any two of them is **D** with reasons `missing_MU` (and `moisture_unknown_for_conversion` where bases are unknown). See §4.

## 2. One batch record (real rows, provisional id)

Rows for Metrc package `ed4c192146b5` (tested 2025-06-24, Lab_H): THCA 29.05%, Lead 0.0 ppm, Arsenic 0.0 ppm. Mapped through `massachusetts_rows_to_record` (measurement summaries shown; the full record also carries report/batch headers):

```json
{
  "compound_id": null,
  "compound_name": "Arsenic",
  "reported_value": "0.0",
  "reported_unit": "ppm",
  "state": "zero",
  "value": 0.0,
  "unit": "ppm"
}
{
  "compound_id": "contaminants/TCNT-0007",
  "compound_name": "Lead",
  "reported_value": "0.0",
  "reported_unit": "ppm",
  "state": "zero",
  "value": 0.0,
  "unit": "ppm"
}
{
  "compound_id": "cannabinoids/TCBN-0007",
  "compound_name": "THCA",
  "reported_value": "29.05",
  "reported_unit": "%",
  "state": "numeric",
  "value": 29.05,
  "unit": "% w/w"
}
```

Identity notes: THCA maps to the canonical record `cannabinoids/TCBN-0007`; Lead maps to `contaminants/TCNT-0007`; Arsenic has no canonical archive record yet, so `compound_id` stays `null` and the parsed name is preserved. THC also has no canonical `cannabinoids/TCBN-*` record yet, so THC rows map to `null` as well (flagged in the design doc's open questions).

The provisional record id is `ma-ccc:ed4c192146b5…`, `record_kind` is `unverified`, `basis` is `unknown` (the CCC CSV does not encode reporting basis — the Commission's March 2024 guidance recommends as-received reporting for flower, but the model does not assume it), and `coa_warnings` reports the provisional id, the missing method metadata, the unknown basis, and every explicit zero for review.

## 3. Explicit zero ≠ not detected (the mission's core rule)

The THC row printed `0.0` by Lab_G (package `2b6d377932fb…`) decodes to `state: "zero"` with `value: 0.0` and a quantitation note:

> explicit zero as printed; flagged for review — chemically implausible for cannabinoids in cannabis, but a common ND reporting convention for contaminants

A hypothetical `"ND"` row, a blank row, and a `<0.05` row would decode to `nd` (no value), `missing` (no value), and `below_loq` (value null, `loq` 0.05) respectively. These five states are never merged: `censorship_summary` on the Lab_G record counts `zero: 3, numeric: 0` — a reader can see that the package's THC, Lead, and Arsenic were printed as zeros, not that they were not detected or untested.

## 4. Comparability grading in practice

`comparability_grade` between the Lab_H `THC 1.34` measurement and the Lab_A `THC 0.231` measurement (both without method metadata) returns:

```text
grade: D
reasons: ['missing_MU']
```

Because both records lack `instrument_technique`, `basis` (unknown), moisture, calibration, PT, and uncertainty, the honest answer is "not comparable" — the model never returns A/B for data that cannot support it. Once a real report supplies a method section (`HPLC-DAD`, basis `as-received`, `measurement_uncertainty: 0.08`, matrix-matched calibration, `|z| < 2` for both labs), the same pair can grade **A** with `['all_criteria_met']`, and the pooled comparison becomes defensible.

---

*Compiled 2026-08-08. Sources: CCC Open Data catalog (official), verbatim fixture slice with provenance recorded in `tests/fixtures/massachusetts/PROVENANCE.md`. Companion: `docs/graph/coa-lab-data-model.md`, `docs/graph/coa-migration.md`.*
