"""Tests for the durable COA & laboratory measurement model (scripts/coa_model.py).

Covers: result-state distinctness (zero / nd / below_lod / below_loq / missing /
not_tested are never conflated), audited unit and basis normalization, display
rounding, record validation, comparability grading A-F, and the Massachusetts
CCC adapter against the real verbatim fixture rows
(tests/fixtures/massachusetts/CCC_Testing_Results_2025.csv).
"""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from scripts.coa_model import (
    AnalyteMeasurement,
    Batch,
    CalibrationType,
    ComparabilityGrade,
    ComparabilityView,
    CoaRecord,
    DensityRequiredError,
    InstrumentTechnique,
    Laboratory,
    MethodMetadata,
    MoistureRequiredError,
    RecordKind,
    Report,
    ReportingBasis,
    ResultState,
    RoundingRule,
    UnitConversionError,
    censorship_summary,
    coa_problems,
    coa_warnings,
    comparability_grade,
    convert_basis,
    convert_unit,
    decode_result,
    from_massachusetts_normalized,
    massachusetts_rows_to_record,
    round_to_sigfigs,
)

FIXTURES = Path(__file__).parent / "fixtures" / "massachusetts"
MA_2025 = FIXTURES / "CCC_Testing_Results_2025.csv"


def measurement(
    compound_name: str = "THC",
    state: ResultState = ResultState.NUMERIC,
    value: float | None = 1.34,
    unit: str = "% w/w",
    reported_value: str = "1.34",
    reported_unit: str = "%",
    compound_id: str | None = None,
    lod: float | None = None,
    loq: float | None = None,
) -> AnalyteMeasurement:
    return AnalyteMeasurement(
        compound_id=compound_id,
        compound_name=compound_name,
        reported_value=reported_value,
        reported_unit=reported_unit,
        state=state,
        value=value,
        unit=unit,
        lod=lod,
        loq=loq,
    )


def record(
    measurements: tuple[AnalyteMeasurement, ...],
    *,
    record_kind: RecordKind = RecordKind.UNVERIFIED,
    report_id: str = "ma-ccc:tag123",
    basis: ReportingBasis = ReportingBasis.UNKNOWN,
    report_date: str | None = None,
) -> CoaRecord:
    return CoaRecord(
        report=Report(
            report_id=report_id,
            report_date=report_date,
            test_date="2025-06-24",
            jurisdiction="MA",
        ),
        batch=Batch(
            batch_id="tag123",
            metrc_tag="tag123",
            basis=basis,
            decarb_convention="native",
            record_kind=record_kind,
            jurisdiction="MA",
        ),
        measurements=measurements,
    )


class ResultStateTest(unittest.TestCase):
    """The mission core rule: ND / <LOQ / 0 / missing / not tested are distinct."""

    def test_states_are_distinct(self):
        self.assertIs(decode_result("ND")[0], ResultState.ND)
        self.assertIs(decode_result("n.d.")[0], ResultState.ND)
        self.assertIs(decode_result("not detected")[0], ResultState.ND)
        self.assertIs(decode_result("<LOQ")[0], ResultState.BELOW_LOQ)
        self.assertIs(decode_result("<LOD")[0], ResultState.BELOW_LOD)
        self.assertIs(decode_result("")[0], ResultState.MISSING)
        self.assertIs(decode_result(None)[0], ResultState.MISSING)
        self.assertIs(decode_result("not tested")[0], ResultState.NOT_TESTED)
        self.assertIs(decode_result("1.34")[0], ResultState.NUMERIC)

    def test_explicit_zero_is_zero_not_nd(self):
        for printed in ("0", "0.0", "0.00"):
            state, value, note = decode_result(printed)
            self.assertIs(state, ResultState.ZERO, printed)
            self.assertEqual(value, 0.0)
            self.assertIn("flagged for review", note)

    def test_censored_below_numeric_threshold(self):
        state, value, note = decode_result("<0.05")
        self.assertIs(state, ResultState.BELOW_LOQ)
        self.assertIsNone(value)

    def test_unrecognized_string_preserved_as_missing(self):
        state, value, note = decode_result("TBD")
        self.assertIs(state, ResultState.MISSING)
        self.assertIn("TBD", note)

    def test_value_contracts(self):
        # numeric requires a value
        with self.assertRaises(ValueError):
            measurement(state=ResultState.NUMERIC, value=None)
        # nd must not carry a value
        with self.assertRaises(ValueError):
            measurement(state=ResultState.ND, value=0.0)
        # zero must be exactly zero
        with self.assertRaises(ValueError):
            measurement(state=ResultState.ZERO, value=0.1)
        # below_lod / below_loq require their limits
        with self.assertRaises(ValueError):
            measurement(state=ResultState.BELOW_LOD, value=None)
        with self.assertRaises(ValueError):
            measurement(state=ResultState.BELOW_LOQ, value=None, loq=None)
        # and they must not carry a value
        with self.assertRaises(ValueError):
            AnalyteMeasurement(
                compound_name="THC", state=ResultState.BELOW_LOQ, value=0.02, loq=0.05
            )
        # valid censored forms construct fine
        ok = measurement(state=ResultState.BELOW_LOQ, value=None, loq=0.05)
        self.assertIsNone(ok.value)
        self.assertEqual(ok.loq, 0.05)
        nd = measurement(state=ResultState.ND, value=None)
        self.assertIsNone(nd.value)


class UnitNormalizationTest(unittest.TestCase):
    def test_mass_mass_exact_factors(self):
        value, audit = convert_unit(1.0, "% w/w", "mg/g")
        self.assertAlmostEqual(value, 10.0)
        self.assertEqual(audit.from_unit, "% w/w")
        self.assertEqual(audit.to_unit, "mg/g")

        value, _ = convert_unit(10.0, "mg/g", "ug/g")
        self.assertAlmostEqual(value, 10_000.0)

        value, _ = convert_unit(1.0, "ug/g", "ppm")
        self.assertAlmostEqual(value, 1.0)  # mass/mass ppm == ug/g

        value, _ = convert_unit(2.0, "ppb", "ug/g")
        self.assertAlmostEqual(value, 0.002)

        value, _ = convert_unit(0.5, "% w/w", "ug/g")
        self.assertAlmostEqual(value, 5_000.0)

    def test_identity_conversion(self):
        value, audit = convert_unit(3.5, "ppm", "ppm")
        self.assertAlmostEqual(value, 3.5)
        self.assertEqual(audit.formula, "identity")

    def test_mass_volume_requires_density(self):
        with self.assertRaises(DensityRequiredError):
            convert_unit(50.0, "mg/mL", "% w/w")
        value, audit = convert_unit(50.0, "mg/mL", "% w/w", density_g_per_ml=1.0)
        self.assertAlmostEqual(value, 5.0)  # 50 mg/mL @ 1 g/mL == 5% w/w
        self.assertIsNotNone(audit.added_uncertainty)

    def test_mg_ml_to_mg_g(self):
        value, _ = convert_unit(50.0, "mg/mL", "mg/g", density_g_per_ml=0.94)
        self.assertAlmostEqual(value, 50.0 / 0.94)

    def test_unknown_unit_raises(self):
        with self.assertRaises(UnitConversionError):
            convert_unit(1.0, "other", "mg/g")

    def test_basis_conversion(self):
        value, audit = convert_basis(
            20.0, ReportingBasis.DRY_WEIGHT, ReportingBasis.AS_RECEIVED, 0.10
        )
        self.assertAlmostEqual(value, 18.0)
        self.assertIsNotNone(audit.added_uncertainty)
        value, _ = convert_basis(
            18.0, ReportingBasis.AS_RECEIVED, ReportingBasis.DRY_WEIGHT, 0.10
        )
        self.assertAlmostEqual(value, 20.0)

    def test_basis_requires_moisture(self):
        with self.assertRaises(MoistureRequiredError):
            convert_basis(
                20.0, ReportingBasis.DRY_WEIGHT, ReportingBasis.AS_RECEIVED, None
            )
        with self.assertRaises(MoistureRequiredError):
            convert_basis(
                20.0, ReportingBasis.DRY_WEIGHT, ReportingBasis.AS_RECEIVED, 1.0
            )

    def test_rounding_rules(self):
        # NIST half-even on measurements
        self.assertAlmostEqual(round_to_sigfigs(2.25, 2, RoundingRule.HALF_EVEN), 2.2)
        self.assertAlmostEqual(round_to_sigfigs(2.35, 2, RoundingRule.HALF_EVEN), 2.4)
        # calculated values round half up (Mississippi hybrid convention)
        self.assertAlmostEqual(round_to_sigfigs(2.25, 2, RoundingRule.HALF_UP), 2.3)
        self.assertAlmostEqual(round_to_sigfigs(2.35, 2, RoundingRule.HALF_UP), 2.4)
        # truncation
        self.assertAlmostEqual(round_to_sigfigs(2.29, 2, RoundingRule.TRUNCATE), 2.2)


class RecordValidationTest(unittest.TestCase):
    def test_verified_requires_canonical_report_id_and_date(self):
        with self.assertRaises(ValueError) as ctx:
            record((measurement(),), record_kind=RecordKind.VERIFIED,
                   report_id="ma-ccc:tag123")
        message = str(ctx.exception)
        self.assertIn("verified records require a canonical lab-results/TLAB-XXXX report id", message)
        self.assertIn("verified records require a report_date", message)
        ok = record((measurement(),), record_kind=RecordKind.VERIFIED,
                    report_id="lab-results/TLAB-0101", report_date="2025-06-24")
        self.assertEqual(coa_problems(ok), [])

    def test_provisional_id_ok_for_unverified_but_warned(self):
        rec = record((measurement(),))
        self.assertEqual(coa_problems(rec), [])
        warnings = coa_warnings(rec)
        self.assertTrue(any("provisional report id" in w for w in warnings))
        self.assertTrue(any("no method metadata" in w for w in warnings))
        self.assertTrue(any("basis unknown" in w for w in warnings))

    def test_duplicate_analyte_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            record((measurement(), measurement()))
        self.assertIn("duplicate analyte measurement", str(ctx.exception))

    def test_bad_producer_id_rejected(self):
        rec = record((measurement(),))
        with self.assertRaises(ValueError) as ctx:
            CoaRecord(
                report=rec.report,
                batch=Batch(
                    batch_id="b1", producer_id="products/TPRD-0001",
                    basis=ReportingBasis.UNKNOWN, record_kind=RecordKind.UNVERIFIED,
                ),
                measurements=rec.measurements,
            )
        self.assertIn("producer_id must be a canonical", str(ctx.exception))

    def test_censorship_summary_counts_states(self):
        rec = record((
            measurement(),
            measurement(compound_name="Arsenic", state=ResultState.ZERO,
                        value=0.0, reported_value="0.0", unit="ppm",
                        reported_unit="ppm"),
            measurement(compound_name="THCA", state=ResultState.NUMERIC,
                        value=27.06, reported_value="27.06", unit="% w/w"),
        ))
        summary = censorship_summary(rec)
        self.assertEqual(summary["numeric"], 2)
        self.assertEqual(summary["zero"], 1)
        self.assertEqual(summary["nd"], 0)
        self.assertEqual(summary["not_tested"], 0)

    def test_json_round_trip(self):
        rec = record((measurement(),))
        payload = json.loads(json.dumps(rec.to_dict()))
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["measurements"][0]["state"], "numeric")


def view(
    compound_name: str = "THC",
    matrix_class: str = "flower",
    technique: InstrumentTechnique = InstrumentTechnique.HPLC_DAD,
    derivatization: bool | None = None,
    basis: ReportingBasis = ReportingBasis.AS_RECEIVED,
    moisture: float | None = None,
    z: float | None = 0.5,
    mu: float | None = 0.08,
    matrix_matched: bool | None = True,
) -> ComparabilityView:
    return ComparabilityView(
        compound_name=compound_name,
        matrix_class=matrix_class,
        instrument_technique=technique,
        derivatization=derivatization,
        basis=basis,
        moisture_content_pct=moisture,
        pt_z_score=z,
        measurement_uncertainty=mu,
        matrix_matched_calibration=matrix_matched,
    )


class ComparabilityGradeTest(unittest.TestCase):
    def test_grade_a_full_metadata(self):
        grade, reasons = comparability_grade(view(), view())
        self.assertIs(grade, ComparabilityGrade.A)
        self.assertEqual(reasons, ["all_criteria_met"])

    def test_grade_f_different_analyte_and_matrix(self):
        grade, reasons = comparability_grade(view(), view(compound_name="THCA"))
        self.assertIs(grade, ComparabilityGrade.F)
        self.assertEqual(reasons, ["different_analyte"])
        grade, reasons = comparability_grade(view(), view(matrix_class="concentrate"))
        self.assertIs(grade, ComparabilityGrade.F)
        self.assertEqual(reasons, ["different_matrix_class"])

    def test_grade_b_basis_differs_but_moisture_known(self):
        a = view(basis=ReportingBasis.AS_RECEIVED, moisture=0.10)
        b = view(basis=ReportingBasis.DRY_WEIGHT, moisture=0.10)
        grade, reasons = comparability_grade(a, b)
        self.assertIs(grade, ComparabilityGrade.B)
        self.assertIn("basis_converted_with_moisture", reasons)

    def test_grade_d_moisture_unknown_for_conversion(self):
        a = view(basis=ReportingBasis.AS_RECEIVED, moisture=None)
        b = view(basis=ReportingBasis.DRY_WEIGHT, moisture=None)
        grade, reasons = comparability_grade(a, b)
        self.assertIs(grade, ComparabilityGrade.D)
        self.assertIn("moisture_unknown_for_conversion", reasons)

    def test_grade_d_unsatisfactory_pt(self):
        a = view(z=3.2)
        grade, reasons = comparability_grade(a, view())
        self.assertIs(grade, ComparabilityGrade.D)
        self.assertIn("lab_a_pt_unsatisfactory", reasons)

    def test_grade_d_gc_underivatized_vs_lc_acidic(self):
        a = view(
            compound_name="THCA",
            technique=InstrumentTechnique.GC_FID,
            derivatization=False,
        )
        b = view(compound_name="THCA", technique=InstrumentTechnique.HPLC_DAD)
        grade, reasons = comparability_grade(a, b)
        self.assertIs(grade, ComparabilityGrade.D)
        self.assertIn("gc_underivatized_vs_lc_acidic", reasons)

    def test_grade_d_calibration_mismatch(self):
        a = view(matrix_matched=True)
        b = view(matrix_matched=False)
        grade, reasons = comparability_grade(a, b)
        self.assertIs(grade, ComparabilityGrade.D)
        self.assertIn("calibration_type_mismatch", reasons)

    def test_grade_c_multiple_noncritical(self):
        # Two non-critical differences: missing MU + basis differs with
        # moisture known -> C (more than one non-critical reason).
        a = view(mu=None, basis=ReportingBasis.AS_RECEIVED, moisture=0.10)
        b = view(mu=None, basis=ReportingBasis.DRY_WEIGHT, moisture=0.10)
        grade, reasons = comparability_grade(a, b)
        self.assertIs(grade, ComparabilityGrade.C)
        self.assertIn("missing_MU", reasons)
        self.assertIn("basis_converted_with_moisture", reasons)

    def test_grade_d_missing_mu_is_not_critical_alone(self):
        # One non-critical reason (missing_MU) grades B, not D.
        a = view(mu=None)
        grade, reasons = comparability_grade(a, view())
        self.assertIs(grade, ComparabilityGrade.B)
        self.assertIn("missing_MU", reasons)


class MassachusettsAdapterTest(unittest.TestCase):
    """Maps the REAL verbatim CCC 2025 fixture rows through the model."""

    @classmethod
    def setUpClass(cls):
        cls.rows = []
        with open(MA_2025, newline="", encoding="utf-8-sig") as handle:
            for raw in csv.DictReader(handle):
                cls.rows.append(raw)

    def test_fixture_is_verbatim_real_data(self):
        self.assertEqual(len(self.rows), 39)

    def test_decode_real_thc_rows(self):
        by_result = {r["RESULT"]: r for r in self.rows if r["ANALYTE/TEST ID"].startswith("THC (")}
        self.assertEqual(by_result["1.34"]["LAB PERFORMING THE TEST"], "Lab_H")
        self.assertEqual(by_result["0.0"]["LAB PERFORMING THE TEST"], "Lab_G")
        state, value, _ = decode_result("1.34")
        self.assertIs(state, ResultState.NUMERIC)
        self.assertEqual(value, 1.34)
        state, value, note = decode_result("0.0")
        self.assertIs(state, ResultState.ZERO)
        self.assertIn("flagged for review", note)

    def test_cross_lab_thc_spread_is_preserved(self):
        values = [
            (r["LAB PERFORMING THE TEST"], r["RESULT"])
            for r in self.rows if r["ANALYTE/TEST ID"].startswith("THC (")
        ]
        labs = {lab for lab, _ in values}
        self.assertIn("Lab_H", labs)
        self.assertIn("Lab_G", labs)
        self.assertIn("Lab_A", labs)
        printed = {v for _, v in values}
        self.assertIn("0.0", printed)  # explicit zero survives, not converted to nd

    def test_from_massachusetts_normalized_maps_identity(self):
        row = next(r for r in self.rows if r["ANALYTE/TEST ID"].startswith("THCA ("))
        from scripts.ingest.states.massachusetts import normalize_testing_common
        normalized = normalize_testing_common(row, release="CCC_Testing_Results_2025")
        m = from_massachusetts_normalized(normalized)
        self.assertEqual(m.compound_id, "cannabinoids/TCBN-0007")
        self.assertEqual(m.compound_name, "THCA")
        self.assertIs(m.state, ResultState.NUMERIC)
        self.assertEqual(m.unit, "% w/w")

    def test_from_massachusetts_normalized_lead_and_arsenic(self):
        from scripts.ingest.states.massachusetts import normalize_testing_common
        lead = from_massachusetts_normalized(normalize_testing_common(
            next(r for r in self.rows if r["ANALYTE/TEST ID"].startswith("Lead (")),
            release="CCC_Testing_Results_2025",
        ))
        self.assertEqual(lead.compound_id, "contaminants/TCNT-0007")
        self.assertIs(lead.state, ResultState.ZERO)
        arsenic = from_massachusetts_normalized(normalize_testing_common(
            next(r for r in self.rows if r["ANALYTE/TEST ID"].startswith("Arsenic (")),
            release="CCC_Testing_Results_2025",
        ))
        self.assertIsNone(arsenic.compound_id)  # no canonical record yet; never invented
        self.assertEqual(arsenic.compound_name, "Arsenic")

    def test_rows_to_record_groups_and_flags(self):
        from scripts.ingest.states.massachusetts import normalize_testing_common
        rows = [
            normalize_testing_common(r, release="CCC_Testing_Results_2025")
            for r in self.rows
        ]
        # group by the raw METRC SOURCE TAG (package-level)
        from collections import OrderedDict
        groups: dict[str, list[dict]] = OrderedDict()
        for raw, norm in zip(self.rows, rows):
            tag = raw["METRC SOURCE TAG"]
            groups.setdefault(tag, []).append(norm)
        self.assertEqual(len(groups), 22)
        first_tag = next(iter(groups))
        rec = massachusetts_rows_to_record(
            groups[first_tag], metrc_tag=first_tag
        )
        self.assertTrue(rec.batch.batch_id.startswith(first_tag[:12]))
        self.assertEqual(rec.batch.record_kind.value, "unverified")
        self.assertEqual(rec.report.jurisdiction, "MA")
        self.assertIs(rec.batch.basis, ReportingBasis.UNKNOWN)
        warnings = coa_warnings(rec)
        self.assertTrue(any("provisional report id" in w for w in warnings))
        self.assertTrue(any("explicit zero flagged" in w for w in warnings))
        summary = censorship_summary(rec)
        self.assertGreaterEqual(summary["zero"], 1)
        self.assertGreaterEqual(summary["numeric"], 1)


try:
    import jsonschema  # noqa: F401
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


class SchemaConsistencyTest(unittest.TestCase):
    """The JSON Schema must stay in sync with the Python model contract."""

    ROOT = Path(__file__).parent.parent
    SCHEMA = ROOT / "metadata" / "coa-measurement.schema.json"

    def test_schema_is_valid_json_with_definitions(self):
        payload = json.loads(self.SCHEMA.read_text())
        self.assertEqual(payload["title"], "Durable COA & Laboratory Measurement Record")
        self.assertIn("analyteMeasurement", payload["definitions"])
        self.assertEqual(payload["properties"]["schema_version"]["const"], "1.0")

    def test_schema_allows_provisional_id_for_unverified(self):
        rec = record((measurement(),))  # provisional ma-ccc: id, unverified
        payload = rec.to_dict()
        self.assert_valid(payload)

    @unittest.skipUnless(_HAS_JSONSCHEMA, "jsonschema package not installed")
    def test_schema_validates_real_ma_record_when_jsonschema_available(self):
        with open(MA_2025, newline="", encoding="utf-8-sig") as handle:
            raw_rows = list(csv.DictReader(handle))
        from scripts.ingest.states.massachusetts import normalize_testing_common
        rows = [
            normalize_testing_common(r, release="CCC_Testing_Results_2025")
            for r in raw_rows
        ]
        tag = raw_rows[0]["METRC SOURCE TAG"]
        rec = massachusetts_rows_to_record(rows, metrc_tag=tag)
        self.assert_valid(rec.to_dict())

    def assert_valid(self, payload: dict) -> None:
        if _HAS_JSONSCHEMA:
            import jsonschema
            schema = json.loads(self.SCHEMA.read_text())
            jsonschema.validate(payload, schema)
        else:
            # Structural smoke check without the dependency: a verified record
            # must carry a canonical report id and a report date.
            verified = dict(payload)
            verified["batch"] = dict(verified["batch"])
            verified["batch"]["record_kind"] = "verified"
            verified["report"] = dict(verified["report"])
            verified["report"]["report_id"] = "lab-results/TLAB-0101"
            verified["report"]["report_date"] = "2025-06-24"
            for m in verified["measurements"]:
                self.assertIn(m["state"], {
                    "numeric", "nd", "below_lod", "below_loq",
                    "zero", "missing", "not_tested",
                })
                if m["state"] in ("numeric", "zero"):
                    self.assertIsInstance(m["value"], (int, float))
                else:
                    self.assertIsNone(m["value"])


if __name__ == "__main__":
    unittest.main()
